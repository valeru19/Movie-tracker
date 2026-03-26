from bson import ObjectId
from bson.errors import InvalidId
from pymongo import ASCENDING, DESCENDING

from app.database import get_collection
from app.schemas import MovieCreate, MovieUpdate, MovieFilter


def _doc_to_dict(doc: dict) -> dict:
    doc["id"] = str(doc.pop("_id"))
    return doc


def _build_filter_query(filters: MovieFilter) -> dict:
    query = {}

    if filters.year_from is not None or filters.year_to is not None:
        query["year"] = {}
        if filters.year_from is not None:
            query["year"]["$gte"] = filters.year_from
        if filters.year_to is not None:
            query["year"]["$lte"] = filters.year_to

    if filters.rating_min is not None:
        query["rating"] = {"$gte": filters.rating_min}

    if filters.actor:
        query["actors"] = {"$elemMatch": {"$regex": filters.actor, "$options": "i"}}

    if filters.director:
        query["director"] = {"$regex": filters.director, "$options": "i"}

    if filters.genre:
        query["genre"] = {"$regex": filters.genre, "$options": "i"}

    if filters.status:
        query["status"] = filters.status.value

    return query


async def create_movie(data: MovieCreate) -> dict:
    collection = get_collection()
    doc = data.model_dump()
    doc["status"] = doc["status"].value if hasattr(doc["status"], "value") else doc["status"]
    result = await collection.insert_one(doc)
    created = await collection.find_one({"_id": result.inserted_id})
    return _doc_to_dict(created)


async def get_movie_by_id(movie_id: str) -> dict | None:
    collection = get_collection()
    try:
        oid = ObjectId(movie_id)
    except InvalidId:
        return None
    doc = await collection.find_one({"_id": oid})
    return _doc_to_dict(doc) if doc else None


async def get_all_movies(skip: int = 0, limit: int = 50) -> list[dict]:
    collection = get_collection()
    cursor = collection.find().sort("title", ASCENDING).skip(skip).limit(limit)
    return [_doc_to_dict(doc) async for doc in cursor]


async def update_movie(movie_id: str, data: MovieUpdate) -> dict | None:
    collection = get_collection()
    try:
        oid = ObjectId(movie_id)
    except InvalidId:
        return None

    update_data = data.model_dump(exclude_none=True)
    if "status" in update_data and hasattr(update_data["status"], "value"):
        update_data["status"] = update_data["status"].value

    if not update_data:
        return await get_movie_by_id(movie_id)

    result = await collection.find_one_and_update(
        {"_id": oid},
        {"$set": update_data},
        return_document=True,
    )
    return _doc_to_dict(result) if result else None


async def delete_movie(movie_id: str) -> bool:
    collection = get_collection()
    try:
        oid = ObjectId(movie_id)
    except InvalidId:
        return False
    result = await collection.delete_one({"_id": oid})
    return result.deleted_count == 1


async def filter_movies(filters: MovieFilter, skip: int = 0, limit: int = 50) -> tuple[int, list[dict]]:
    collection = get_collection()
    query = _build_filter_query(filters)
    total = await collection.count_documents(query)
    cursor = collection.find(query).sort("rating", DESCENDING).skip(skip).limit(limit)
    movies = [_doc_to_dict(doc) async for doc in cursor]
    return total, movies