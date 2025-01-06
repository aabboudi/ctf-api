from fastapi import APIRouter, HTTPException
from pymongo.errors import PyMongoError, DuplicateKeyError
from ..db.PlayerProfile import PlayerProfile
from ..config import players_collection

router = APIRouter()

# Get health status of the API
@router.get("/", tags=["Status"])
def health_check():
  return {"Status": "Running"}

# Get all player scores in descending order
@router.get("/get-scoreboard", tags=["Status"])
async def get_scoreboard():
  try:
    users = players_collection.find({}, {"_id": 0, "username": 1, "score": 1}).sort("score", -1)
    return [{"username": user["username"], "score": user["score"]} for user in users]
  except PyMongoError as e:
    raise HTTPException(status_code=500, detail=f"Database error: {e}")


'''API Endpoints for Player Profile Management'''
# Get all player profiles
@router.get("/get-player/{nccid}", tags=["Player"])
async def get_player(nccid: str):
  try:
    player = players_collection.find_one({"nccid": nccid}, {"_id": 0})
    if player is None:
      raise HTTPException(status_code=404, detail="Player not found")
    return player
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))

# Add a new player profile
@router.post("/add-player", tags=["Player"])
async def add_player(player: PlayerProfile):
  try:
    players_collection.insert_one(player.model_dump())
    return {"message": "Player data received successfully", "data": player.model_dump()}
  except DuplicateKeyError:
    raise HTTPException(status_code=400, detail="Player already exists")
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))

# Update an existing player score
@router.put("/update-score/{nccid}", tags=["Player"])
async def update_score(nccid: str, score: int):
  try:
    players_collection.find_one_and_update(
      {"nccid": nccid},
      {"$inc": {"score": score}},
      return_document=True
    )
    return {"message": "Score updated successfully", "nccid": nccid, "score": score}
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))

# Delete a player profile
@router.delete("/delete-player/{nccid}", tags=["Player"])
async def delete_player(nccid: str):
  try:
    result = players_collection.delete_one({"nccid": nccid})
    if result.deleted_count == 0:
      raise HTTPException(status_code=404, detail="Player not found")
    return {"message": "Player deleted successfully", "nccid": nccid}
  except PyMongoError as e:
    raise HTTPException(status_code=500, detail=f"Database error: {e}")
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))

# @app.put("/update-field/{nccid}")
# async def update_field(nccid: str, updated_field: Dict[str, Any]):
#   try:
#     # Update the specified field in the document corresponding to the given nccid
#     result = users_collection.update_one(
#       {"nccid": nccid},  # Filter by nccid
#       {"$set": updated_field}  # Update the document with the provided field
#     )
      
#     if result.matched_count == 0:
#       raise HTTPException(status_code=404, detail="User not found")
      
#     return {"message": "User document updated successfully"}
  
#   except PyMongoError as e:
#     raise HTTPException(status_code=500, detail=f"Database error: {e}")
#   except Exception as e:
#     raise HTTPException(status_code=500, detail=str(e))
