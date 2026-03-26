from pydantic import BaseModel, Field, field_validator
from typing import Optional
from enum import Enum


class WatchStatus(str, Enum):
    watched = "watched"
    not_watched = "not_watched"


class MovieCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=300, description="Название фильма")
    studio: str = Field(..., min_length=1, max_length=200, description="Студия")
    year: int = Field(..., ge=1888, le=2100, description="Год съёмки")
    rating: float = Field(..., ge=0.0, le=10.0, description="Оценка от 0 до 10")
    status: WatchStatus = Field(default=WatchStatus.not_watched, description="Статус просмотра")
    actors: list[str] = Field(default=[], description="Список актёров")
    director: str = Field(..., min_length=1, max_length=200, description="Режиссёр")
    genre: str = Field(..., min_length=1, max_length=100, description="Жанр")

    @field_validator("actors")
    @classmethod
    def actors_not_empty_strings(cls, v):
        return [a.strip() for a in v if a.strip()]

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "Inception",
                "studio": "Warner Bros.",
                "year": 2010,
                "rating": 8.8,
                "status": "watched",
                "actors": ["Leonardo DiCaprio", "Joseph Gordon-Levitt", "Elliot Page"],
                "director": "Christopher Nolan",
                "genre": "Sci-Fi"
            }
        }
    }


class MovieUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=300)
    studio: Optional[str] = Field(None, min_length=1, max_length=200)
    year: Optional[int] = Field(None, ge=1888, le=2100)
    rating: Optional[float] = Field(None, ge=0.0, le=10.0)
    status: Optional[WatchStatus] = None
    actors: Optional[list[str]] = None
    director: Optional[str] = Field(None, min_length=1, max_length=200)
    genre: Optional[str] = Field(None, min_length=1, max_length=100)

    @field_validator("actors")
    @classmethod
    def actors_not_empty_strings(cls, v):
        if v is None:
            return v
        return [a.strip() for a in v if a.strip()]

    model_config = {
        "json_schema_extra": {
            "example": {
                "rating": 9.0,
                "status": "watched"
            }
        }
    }


class MovieResponse(BaseModel):
    id: str = Field(..., description="ID документа в MongoDB")
    title: str
    studio: str
    year: int
    rating: float
    status: WatchStatus
    actors: list[str]
    director: str
    genre: str

    model_config = {"from_attributes": True}


class MovieFilter(BaseModel):
    year_from: Optional[int] = Field(None, ge=1888, description="Год — начало диапазона")
    year_to: Optional[int] = Field(None, le=2100, description="Год — конец диапазона")
    rating_min: Optional[float] = Field(None, ge=0.0, le=10.0, description="Минимальная оценка")
    actor: Optional[str] = Field(None, description="Имя актёра")
    director: Optional[str] = Field(None, description="Имя режиссёра")
    genre: Optional[str] = Field(None, description="Жанр")
    status: Optional[WatchStatus] = Field(None, description="Статус просмотра")

    model_config = {
        "json_schema_extra": {
            "example": {
                "year_from": 2000,
                "year_to": 2020,
                "rating_min": 7.0,
                "genre": "Sci-Fi",
                "status": "watched"
            }
        }
    }


class FilterResult(BaseModel):
    total: int = Field(..., description="Количество найденных фильмов")
    movies: list[MovieResponse]