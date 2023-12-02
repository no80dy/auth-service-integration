import uuid

from datetime import datetime, date
from pydantic import (
    BaseModel,
    BeforeValidator,
)
from pydantic import Field
from typing_extensions import Annotated


def validate_datetime(
    datetime_val: str | datetime,
) -> datetime:
    """
    Validate and convert timestamps from SQLite format to datetime.

    Args:
        datetime_val (str | datetime):
            - If str: A timestamp string in SQLite format.
            - If datetime: A timestamp in datetime format (PostgreSQL).

    Returns:
        datetime:
            The converted timestamp in datetime format.
    """
    if isinstance(datetime_val, str):
        return datetime.strptime(
            datetime_val.split('+')[0], '%Y-%m-%d %H:%M:%S.%f'
        )
    return datetime_val.replace(tzinfo=None)


class TimeStampBaseModel(BaseModel):
    """
    Base model for working with timestamp data.

    Attributes:
        created_at (datetime):
            Date and time of creation.
        updated_at (datetime):
            Date and time of creation.
    """
    created_at: Annotated[datetime, BeforeValidator(validate_datetime)]
    updated_at: Annotated[datetime, BeforeValidator(validate_datetime)]


class UUIDBaseModel(BaseModel):
    """
    Base model for working with id data.

    Attributes:
        id (uuid.UUID):
            UUID v4 of object.
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4)


class Person(UUIDBaseModel, TimeStampBaseModel):
    """
    Class contains all columns of person table in database.

    Attributes:
        full_name (str):
            Full name of person.
    """
    full_name: str


class Filmwork(UUIDBaseModel, TimeStampBaseModel):
    """
    Class contains all columns of film_work table in database.

    Attributes:
        title (str):
            Film work title.
        description (str):
            Film work description.
        creation_date (date):
            Creation dat of film work.
        file_path (str):
            File path to the film work.
        type (str):
            Film work type which contains: (movie, tv-show, ).
        rating (float):
            Film work rating which contains value from 0.0 to 10.0.
    """
    title: str
    description: str | None
    creation_date: date | None
    file_path: str | None
    type: str
    rating: float | None


class Genre(UUIDBaseModel, TimeStampBaseModel):
    """
    Class contains all columns of genre table in database.

    Attributes:
        name (str):
            Genre name.
        description (str):
            Genre description.
    """
    name: str
    description: str | None


class PersonFilmwork(UUIDBaseModel):
    """
    Class contains all columns of person_film_work table.

    Attributes:
        role (str):
            Person role in film work.
        created_at (datetime):
            Date and time of creation.
        film_work_id (uuid.UUID):
            Film work id.
        person_id (uuid.UUID):
            Person id.
    """
    role: str
    created_at: Annotated[datetime, BeforeValidator(validate_datetime)]
    film_work_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    person_id: uuid.UUID = Field(default_factory=uuid.uuid4)


class GenreFilmwork(UUIDBaseModel):
    """
    Class contains all columns of genre_film_work table.

    Attributes:
        created_at (datetime):
            Date and time creation.
        genre_id (uuid.UUID):
            Genre id.
        film_work_id (uuid.UUID):
            Film work id.
    """
    created_at: Annotated[datetime, BeforeValidator(validate_datetime)]
    genre_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    film_work_id: uuid.UUID = Field(default_factory=uuid.uuid4)
