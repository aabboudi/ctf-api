from datetime import datetime
from fastapi import APIRouter, HTTPException
from pymongo.errors import DuplicateKeyError
from app.db.config import players_collection, flags_collection
from app.db.schemas import FlagInput
router = APIRouter()

'''
Admin Access
'''
# Add flag
@router.post("/add-flag", tags=["Admin"])
async def add_flag(flagInput: FlagInput):
  try:
    flags_collection.insert_one(flagInput.model_dump())
    return {"message": "Flag added successfully", "flag": flagInput.flag, "score": flagInput.score, "type": flagInput.type}
  except DuplicateKeyError:
    raise HTTPException(status_code=409, detail="Flag already exists")
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))

# Add player score
@router.put("/add-extra-credit", tags=["Admin"])
# async def update_score(nccid: str, score: int, password: str = Depends(verify_admin_password)):
async def add_points(nccid: str, score: int):
  try:
    # TODO: Review score update and extra credit list
    players_collection.find_one_and_update(
      {"nccid": nccid},
      {
        "$inc": {"score": score},
        "$set": {"updatedAt": datetime.now()}
      },
      return_document=True
    )
    return {"message": "Score updated successfully", "nccid": nccid, "score": score}
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))
