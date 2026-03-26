from fastapi import APIRouter, HTTPException, Query, status

from app.models import (
    create_movie,
    get_movie_by_id,
    get_all_movies,
    update_movie,
    delete_movie,
    filter_movies,
)
from app.schemas import MovieCreate, MovieUpdate, MovieResponse, MovieFilter, FilterResult, WatchStatus

router = APIRouter(prefix="/movies", tags=["Movies"])


# ─────────────────────────────────────────────
#  CRUD
# ─────────────────────────────────────────────

@router.post(
    "/",
    response_model=MovieResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Добавить фильм",
    description="Создаёт новый документ фильма в MongoDB.",
)
async def add_movie(data: MovieCreate):
    return await create_movie(data)


@router.get(
    "/",
    response_model=list[MovieResponse],
    summary="Список всех фильмов",
    description="Возвращает все фильмы с пагинацией, отсортированные по названию.",
)
async def list_movies(
    skip: int = Query(0, ge=0, description="Сколько документов пропустить"),
    limit: int = Query(50, ge=1, le=200, description="Максимум документов в ответе"),
):
    return await get_all_movies(skip=skip, limit=limit)


@router.get(
    "/{movie_id}",
    response_model=MovieResponse,
    summary="Получить фильм по ID",
)
async def get_movie(movie_id: str):
    movie = await get_movie_by_id(movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Фильм не найден")
    return movie


@router.patch(
    "/{movie_id}",
    response_model=MovieResponse,
    summary="Обновить фильм",
    description="Обновляет только переданные поля. Остальные остаются без изменений.",
)
async def patch_movie(movie_id: str, data: MovieUpdate):
    movie = await update_movie(movie_id, data)
    if not movie:
        raise HTTPException(status_code=404, detail="Фильм не найден")
    return movie


@router.delete(
    "/{movie_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить фильм",
)
async def remove_movie(movie_id: str):
    deleted = await delete_movie(movie_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Фильм не найден")


# ─────────────────────────────────────────────
#  Фильтрация
# ─────────────────────────────────────────────

@router.post(
    "/search/filter",
    response_model=FilterResult,
    summary="Поиск и подсчёт по критериям",
    description="""
Гибкая выборка фильмов с подсчётом. Все критерии опциональны и комбинируются:

- **year_from / year_to** — диапазон лет съёмки  
- **rating_min** — оценка от N и выше  
- **actor** — фильмы с этим актёром (поиск подстроки, без учёта регистра)  
- **director** — фильмы режиссёра (без учёта регистра)  
- **genre** — жанр (без учёта регистра)  
- **status** — `watched` или `not_watched`  

Результат содержит `total` (общее число подходящих документов) и `movies` (с пагинацией).
    """,
    tags=["Filter"],
)
async def search_movies(
    filters: MovieFilter,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    total, movies = await filter_movies(filters, skip=skip, limit=limit)
    return FilterResult(total=total, movies=movies)


# ─────────────────────────────────────────────
#  Быстрые GET-фильтры (удобны прямо из Swagger)
# ─────────────────────────────────────────────

@router.get(
    "/filter/by-year",
    response_model=FilterResult,
    summary="Фильмы по диапазону лет",
    tags=["Filter"],
)
async def filter_by_year(
    year_from: int = Query(..., ge=1888),
    year_to: int = Query(..., le=2100),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    f = MovieFilter(year_from=year_from, year_to=year_to)
    total, movies = await filter_movies(f, skip=skip, limit=limit)
    return FilterResult(total=total, movies=movies)


@router.get(
    "/filter/by-rating",
    response_model=FilterResult,
    summary="Фильмы с оценкой от N и выше",
    tags=["Filter"],
)
async def filter_by_rating(
    rating_min: float = Query(..., ge=0, le=10),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    f = MovieFilter(rating_min=rating_min)
    total, movies = await filter_movies(f, skip=skip, limit=limit)
    return FilterResult(total=total, movies=movies)


@router.get(
    "/filter/by-actor",
    response_model=FilterResult,
    summary="Фильмы с указанным актёром",
    tags=["Filter"],
)
async def filter_by_actor(
    actor: str = Query(..., description="Имя (или часть имени) актёра"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    f = MovieFilter(actor=actor)
    total, movies = await filter_movies(f, skip=skip, limit=limit)
    return FilterResult(total=total, movies=movies)


@router.get(
    "/filter/by-director",
    response_model=FilterResult,
    summary="Фильмы указанного режиссёра",
    tags=["Filter"],
)
async def filter_by_director(
    director: str = Query(...),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    f = MovieFilter(director=director)
    total, movies = await filter_movies(f, skip=skip, limit=limit)
    return FilterResult(total=total, movies=movies)


@router.get(
    "/filter/by-genre",
    response_model=FilterResult,
    summary="Фильмы указанного жанра",
    tags=["Filter"],
)
async def filter_by_genre(
    genre: str = Query(...),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    f = MovieFilter(genre=genre)
    total, movies = await filter_movies(f, skip=skip, limit=limit)
    return FilterResult(total=total, movies=movies)


@router.get(
    "/filter/by-status",
    response_model=FilterResult,
    summary="Фильмы по статусу просмотра",
    tags=["Filter"],
)
async def filter_by_status(
    watch_status: WatchStatus = Query(..., alias="status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    f = MovieFilter(status=watch_status)
    total, movies = await filter_movies(f, skip=skip, limit=limit)
    return FilterResult(total=total, movies=movies)