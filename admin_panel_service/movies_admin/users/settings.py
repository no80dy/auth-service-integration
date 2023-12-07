from dataclasses import dataclass


@dataclass
class Settings:
    REFRESH_TOKENS_URL = 'http://auth_service_fastapi:8000/api/v1/users/refresh-tokens'
    LOGOUT_URL = 'http://auth_service_fastapi:8000/api/v1/users/logout'
    CHANGE_PASSWORD_URL = 'http://auth_service_fastapi:8000/api/v1/users/change_password'
    LOG_IN_URL = 'http://auth_service_fastapi:8000/api/v1/users/signin'


settings = Settings()
