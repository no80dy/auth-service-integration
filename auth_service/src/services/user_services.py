import json
import logging
import uuid

from datetime import datetime
from functools import lru_cache

from fastapi import Depends
from sqlalchemy import select, update, UUID, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from werkzeug.security import generate_password_hash, check_password_hash
from opentelemetry import trace

from db.postgres import get_session
from db.redis import RedisStorage
from db.storage import get_nosql_storage, TokenHandler
from models.entity import User, RefreshSession, UserLoginHistory, Permission, Group
from schemas.entity import RefreshToDb, UserLoginHistoryInDb, UserLogoutHistoryInDb, RefreshDelDb

CACHE_EXPIRE_IN_SECONDS = 5 * 60  # 5 min


tracer = trace.get_tracer(__name__)


class UserService:
    def __init__(
            self,
            token_handler: TokenHandler,
            db: AsyncSession,
    ) -> None:
        self.token_handler = token_handler
        self.db = db

    async def get_user_permissions(self, user_id: str) -> list[str]:
        user = (await self.db.execute(
            select(User).where(User.id == user_id)
        )).scalar()

        permissions_in_groups = [group.permissions for group in user.groups]
        permissions_names = []
        for permissions_in_group in permissions_in_groups:
            permissions_names.extend(
                [permission_in_group.permission_name for permission_in_group in permissions_in_group]
            )

        return list(set(permissions_names))

    async def check_exist_user(self, user_dto):
        with tracer.start_as_current_span('check_exist_user'):
            result = await self.db.execute(select(User).where(User.username == user_dto.get('username')))
            user = result.scalars().first()

        return bool(user)

    async def check_unique_email(self, user_dto):
        with tracer.start_as_current_span('check_unique_email'):
            result = await self.db.execute(select(User).where(User.email == user_dto.get('email')))
            user = result.scalars().first()

        return True if not user else False

    async def create_user(self, user_dto):
        with tracer.start_as_current_span('create_user'):
            user = User(**user_dto)
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)

        return user

    async def update_password(self, user_dto):
        with tracer.start_as_current_span('update_password'):
            user = User(**user_dto)
            if (
                    not await self.check_repeated_password(user_dto.get('password'), user_dto.get('repeated_old_password')) or
                    not await self._check_old_password(user_dto) or
                    user_dto.get('password') == user_dto.get('new_password')  # старый и новый пароль должны отличаться
            ):
                return False

            new_password = generate_password_hash(user_dto.get('new_password'))
            await self.db.execute(
                update(User).where(User.username == user_dto.get('username')).values(password=new_password),
            )
            await self.db.commit()

        return user

    @staticmethod
    async def check_repeated_password(password, repeated_password):
        with tracer.start_as_current_span('check_repeated_password'):
            if not password == repeated_password:
                return False
            return True

    async def _check_old_password(self, user_dto):
        with tracer.start_as_current_span('_check_old_password'):
            result = await self.db.execute(select(User).where(User.username == user_dto.get('username')))
            user = result.scalars().first()
            old_pass_verified = check_password_hash(user.password, user_dto.get('password'))

        return True if old_pass_verified else False

    async def get_user_by_username(self, username: str) -> User | None:
        """Возвращает пользователя из базы данных по его username, если он есть."""
        with tracer.start_as_current_span('get_user_by_username'):
            try:
                result = await self.db.execute(select(User).where(User.username == username))
                user = result.scalars().first()
                return user
            except SQLAlchemyError as e:
                logging.error(e)

    async def put_refresh_session_in_db(self, user_id: str, user_agent: str, decrypted_token: dict) -> None:
        """Записывает созданный refresh токен в базу данных."""
        with tracer.start_as_current_span('put_refresh_session_in_db'):
            session_dto = json.dumps({
                'user_id': user_id,
                'refresh_jti': decrypted_token['jti'],
                'user_agent': user_agent,
                'expired_at': datetime.fromtimestamp(decrypted_token['exp']).isoformat(),
                'is_active': True
            })
            data = RefreshToDb.model_validate_json(session_dto)
            try:
                row = RefreshSession(**data.model_dump())
                self.db.add(row)
                await self.db.commit()
                await self.db.refresh(row)
            except SQLAlchemyError as e:
                logging.error(e)
                await self.db.rollback()

    async def check_if_session_exist(self, user_id: str, user_agent: str) -> bool:
        """Проверяет существование сессии."""
        with tracer.start_as_current_span('check_if_session_exist'):
            session_dto = json.dumps({
                'user_id': user_id,
                'user_agent': user_agent,
            })
            data = RefreshDelDb.model_validate_json(session_dto)
            try:
                stmt = select(RefreshSession). \
                    where(
                    User.id == data.user_id,
                        RefreshSession.user_agent == data.user_agent,
                        RefreshSession.is_active.is_(True),
                    )
                result = await self.db.execute(stmt)
                row = result.scalars().first()
                return True if row else False
            except SQLAlchemyError as e:
                logging.error(e)

    async def del_refresh_session_in_db(self, user_id: str, user_agent: str) -> None:
        """Помечает refresh токен как удаленный в базе данных."""
        session_dto = json.dumps({
            'user_id': user_id,
            'user_agent': user_agent,
        })
        data = RefreshDelDb.model_validate_json(session_dto)
        try:
            stmt = update(RefreshSession). \
                values(is_active=False). \
                where(
                    User.id == data.user_id,
                    RefreshSession.user_agent == data.user_agent,
                    RefreshSession.is_active.is_(True),
                )
            await self.db.execute(stmt)
            await self.db.commit()
        except SQLAlchemyError as e:
            logging.error(e)
            await self.db.rollback()

    async def del_all_refresh_sessions_in_db(self, user: User) -> None:
        try:
            await self.db.execute(
                update(RefreshSession).where(RefreshSession.user_id == user.id).values(is_active=False),
            )
            await self.db.commit()
        except SQLAlchemyError as e:
            logging.error(e)

    async def put_login_history_in_db(self, user_id: str, user_agent: str) -> None:
        """Записывает историю входа в аккаунт в базу данных."""
        history_dto = json.dumps({
            'user_id': user_id,
            'user_agent': user_agent,
        })
        data = UserLoginHistoryInDb.model_validate_json(history_dto)
        try:
            row = UserLoginHistory(**data.model_dump())
            self.db.add(row)
            await self.db.commit()
            await self.db.refresh(row)
        except SQLAlchemyError as e:
            logging.error(e)
            await self.db.rollback()

    async def check_if_user_login(self, user_id: str, user_agent: str) -> bool:
        """Проверяет существования активной записи о входе пользователя с данного устройства."""
        try:
            stmt = select(UserLoginHistory). \
                where(
                    UserLoginHistory.user_id == user_id,
                    UserLoginHistory.user_agent == user_agent,
                    UserLoginHistory.logout_at.is_(None))

            result = await self.db.execute(stmt)
            active_login_history = result.scalars().first()

            return True if active_login_history else False
        except SQLAlchemyError as e:
            logging.error(e)

    async def put_logout_history_in_db(self, user_id: str, user_agent: str) -> None:
        """Записывает историю выхода из аккаунта в базу данных."""
        history_dto = json.dumps({
            'user_id': user_id,
            'user_agent': user_agent,
            'logout_at': datetime.now().isoformat()
        })
        data = UserLogoutHistoryInDb.model_validate_json(history_dto)
        try:
            stmt = update(UserLoginHistory). \
                values(logout_at=data.logout_at). \
                where(
                    User.id == data.user_id,
                    UserLoginHistory.user_agent == data.user_agent
                )

            await self.db.execute(stmt)
            await self.db.commit()
        except SQLAlchemyError as e:
            logging.error(e)
            await self.db.rollback()

    async def count_refresh_sessions(self, user_id: str) -> int:
        """Возвращает число открытых сессий пользователя."""
        try:
            result = await self.db.execute(select(RefreshSession).where(
                RefreshSession.user_id == user_id,
                RefreshSession.is_active.is_(True),
                ))
            sessions = result.scalars().all()
            return sessions.count() if len(sessions) > 0 else 0
        except SQLAlchemyError as e:
            logging.error(e)

    async def calc_previous_and_next_pages(self, page_number, page_size, count):
        previous = page_number - 1 if page_number != 1 else None
        next_page = page_number + 1 if count // (page_size * page_number) > 1 else None
        return previous, next_page

    async def get_login_history(
            self,
            user_id: uuid,
            page_size: int,
            page_number: int,
    ) -> list[dict[str, UUID | datetime | str]]:

        offset_min, offset_max = await self.calculate_offset(page_size, page_number)

        result = await self.db.execute(
            select(UserLoginHistory).
            where(UserLoginHistory.user_id == str(user_id)).
            order_by(UserLoginHistory.id).
            offset(offset_min).
            limit(offset_max - offset_min)
        )
        history = result.scalars().all()

        history_dto = [{
            'user_id': item.user_id,
            'user_agent': item.user_agent,
            'login_at': item.login_at,
        } for item in history]

        return history_dto

    async def get_login_history_count(self, user_id: uuid):
        result = await self.db.execute(
            select(func.count(UserLoginHistory.id)).
            where(UserLoginHistory.user_id == str(user_id))
        )
        return result.scalar()

    async def calculate_offset(self, page_size: int, page_number: int) -> tuple[int, int]:
        offset_min = (page_number - 1) * page_size
        offset_max = offset_min + page_size

        return offset_min, offset_max


@lru_cache()
def get_user_service(
        no_sql: RedisStorage = Depends(get_nosql_storage),
        db: AsyncSession = Depends(get_session),
) -> UserService:
    token_handler = TokenHandler(no_sql, CACHE_EXPIRE_IN_SECONDS)

    return UserService(token_handler, db)
