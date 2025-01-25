from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pymongo.errors import PyMongoError, DuplicateKeyError
from app.db.config import players_collection, flags_collection
from app.db import partials as dbx
from app.lib.auth import verify_admin_user
router = APIRouter()

'''
Admin Access
'''
# Get all player scores in descending order
@router.get("/get-scoreboard", tags=["Admin"])
async def get_scoreboard(admin_nccid: str = Depends(verify_admin_user)):
  try:
    users = players_collection.find({}, {"_id": 0, "nccid": 1, "username": 1, "score": 1}).sort("score", -1)
    return [{"nccid": user["nccid"], "username": user["username"], "score": user["score"]} for user in users]
  except PyMongoError:
    raise HTTPException(status_code=500, detail="Database error: an error occurred while getting the scoreboard")

# Add flag
@router.post("/add-flag", tags=["Admin"])
async def add_flag(flagInput: dbx.FlagInput, admin_nccid: str = Depends(verify_admin_user)):
  try:
    flag_data = flagInput.model_dump()
    flag_data["createdBy"] = admin_nccid
    flag_data["createdAt"] = datetime.now().isoformat()
    flags_collection.insert_one(flag_data)
    return {
      "message": "Flag added successfully",
      "flag": flag_data["flag"],
      "score": flag_data["score"],
      "type": flag_data["type"],
      "createdBy": flag_data["createdBy"],
      "createdAt": flag_data["createdAt"]
    }
  except DuplicateKeyError:
    raise HTTPException(status_code=409, detail="Flag already exists")
  except Exception:
    raise HTTPException(status_code=500, detail="An error occurred while adding the flag")

# Add player score
@router.put("/add-extra-credit", tags=["Admin"])
async def add_points(request: dbx.AddPointsRequest, admin_nccid: str = Depends(verify_admin_user)):
  try:
    # TODO: Review score update and extra credit list
    player = players_collection.find_one_and_update(
      {"nccid": request.nccid},
      {"$inc": {"score": request.score},
       "$set": {"updatedAt": datetime.now().isoformat()}},
      return_document=True)

    if player is None:
      raise HTTPException(status_code=404, detail="Player not found")
    return {"message": "Score updated successfully", "nccid": player["nccid"], "score": player["score"]}
  except Exception:
    raise HTTPException(status_code=500, detail="An error occurred while updating the score")
