import os
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException
from pymongo.errors import PyMongoError, DuplicateKeyError
from app.db.schemas import PlayerProfile
from app.db.config import players_collection
from app.includes.Requests import AuthenticateRequest
from app.includes.Hash import ncchash, create_access_token
from ..db.config import ACCESS_TOKEN_EXPIRE_MINUTES
router = APIRouter()

'''
General API Status
'''
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


'''
Admin Access
'''
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


'''
Player Profile Management
'''
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
    player.ncchash = ncchash(player.ipaddr, player.macaddr)
    # TODO: Add timezone
    player.createdAt = datetime.now()
    player.updatedAt = datetime.now()
    
    players_collection.insert_one(player.model_dump())
    return {"message": "Player data received successfully", "data": player.model_dump()}
  except DuplicateKeyError:
    raise HTTPException(status_code=400, detail="Player already exists")
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))

# IPv4 & MAC Based Authentication
@router.post("/authenticate", tags=["Player"])
async def authenticate(request: AuthenticateRequest):
  player_hash = ncchash(request.ipaddr, request.macaddr)
  try:
    player = players_collection.find_one({"ncchash": player_hash})
    if player is None:
      raise HTTPException(status_code=404, detail="Player not found")
    access_token_expires = timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    access_token = create_access_token(data={"sub": player_hash}, expires_delta=access_token_expires)
    return {"access_token": access_token, "access_token_expires": access_token_expires}
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
