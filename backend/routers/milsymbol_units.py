from fastapi import APIRouter, Body, Request, status, HTTPException, Response
from models import UnitFeatureModel, UpdateUnitFeatureModel, UnitFeatureCollection
from bson import ObjectId
from pymongo import ReturnDocument
from motor.motor_asyncio import AsyncIOMotorCollection


router = APIRouter()

UNITS_PER_PAGE = 10


# POST handler(s)
@router.post(
    "/",
    response_description="Add a new unit feature",
    response_model=UnitFeatureModel,
    status_code=status.HTTP_201_CREATED,
    response_model_by_alias=False,
)
async def add_unit(request: Request, unit: UnitFeatureModel = Body(...)):
    """
    Create a new unit feature with a generated id.
    """
    units: AsyncIOMotorCollection = request.app.db["milsym_units_01"]

    document = unit.model_dump(by_alias=True, exclude=["id"])
    inserted = await units.insert_one(document)

    return await units.find_one({"_id": inserted.inserted_id})


# GET handler(s)
@router.get(
    "/",
    response_description="List all units, no pagination",
    response_model=UnitFeatureCollection,
    response_model_by_alias=False,
)
async def list_units(request: Request):
    """
    List all units.
    """
    units: AsyncIOMotorCollection = request.app.db["milsym_units_01"]

    results = []

    cursor = units.find()

    async for document in cursor:
        results.append(document)
    
    return UnitFeatureCollection(unit_features=results)


@router.get(
    "/{id}",
    response_description="Get a single unit feature by ID",
    response_model=UnitFeatureModel,
    response_model_by_alias=False,
)
async def show_unit(id: str, request: Request):
    """
    Get the record for a specific unit, looked up by `id`.
    """
    units: AsyncIOMotorCollection = request.app.db["milsym_units_01"]

    # try to convert the ID to an ObjectId, otherwise 404:
    try:
        id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=404, detail=f"Unit {id} not found")
    
    if (unit := await units.find_one({"_id": ObjectId(id)})) is not None:
        return unit
    
    raise HTTPException(status_code=404, detail=f"Unit with id: {id} not found")


# UPDATE handler(s)
@router.put(
    "/{id}",
    response_description="Update unit",
    response_model=UnitFeatureModel,
    response_model_by_alias=False,
)
async def update_unit(
    id: str,
    request: Request,
    unit: UpdateUnitFeatureModel = Body(...),
):
    """
    Update individual fields of an existing car record.

    Only the provided fields will be updated.
    Any missing or `null` fields will be ignored.
    """

    # try to convert the ID to an ObjectId, otherwise 404:
    try:
        id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=404, detail=f"Unit {id} not found")
    
    unit = {
        k: v
        for k, v in unit.model_dump(by_alias=True).items()
        if v is not None and k != "_id"
    }

    if len(unit) >= 1:
        units: AsyncIOMotorCollection = request.app.db["milsym_units_01"]

        update_result = await units.find_one_and_update(
            {"_id": id},
            {"$set": unit},
            return_document=ReturnDocument.AFTER,
        )
        if update_result is not None:
            return update_result
        else:
            raise HTTPException(status_code=404, detail=f"Unit {id} not found")
        
    # The update is empty, but we should still return the matching car:
    if (existing_car := await units.find_one({"_id": id})) is not None:
        return existing_car
    
    raise HTTPException(status_code=404, detail=f"Unit {id} not found")


# DELETE handler(s)
@router.delete(
    "/{id}",
    response_description="Delete a unit"
)
async def delete_unit(id: str, request: Request):
    """
    Remove a single unit.
    """
    try:
        id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=404, detail=f"Unit {id} not found")
    
    units: AsyncIOMotorCollection = request.app.db["milsym_units_01"]

    delete_result = await units.delete_one({"_id": id})

    if delete_result == 1:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    
    raise HTTPException(status_code=404, detail=f"Unit with {id} not found")
