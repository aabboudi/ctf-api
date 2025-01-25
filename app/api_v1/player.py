from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from pymongo.errors import PyMongoError, DuplicateKeyError
from fastapi.responses import JSONResponse
from app.db import partials as dbx
from app.db.schemas import PlayerProfile
from app.db.config import ACCESS_TOKEN_EXPIRE_MINUTES, players_collection, flags_collection
from app.lib.hash import ncchash, create_access_token
from app.lib.auth import get_current_user
router = APIRouter()

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
    player.ncchash = ncchash(ip=player.ipaddr, mac=player.macaddr)
    # TODO: Add timezone
    player.createdAt = datetime.now().isoformat()
    player.updatedAt = datetime.now().isoformat()
    players_collection.insert_one(player.model_dump())
    return JSONResponse(content={"message": "Player data received successfully", "data": player.model_dump()}, status_code=200)
  except DuplicateKeyError:
    raise HTTPException(status_code=409, detail="Player already exists")
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))

# IPv4 & MAC Based Authentication
@router.post("/authenticate", tags=["Player"])
async def authenticate(request: dbx.AuthenticateRequest):
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
@router.delete("/delete-player", tags=["Player"])
async def delete_player(ncchash: str = Depends(get_current_user)):
  try:
    profile = players_collection.delete_one({"ncchash": ncchash})
    if profile.deleted_count == 0:
      raise HTTPException(status_code=404, detail="Player not found")
    return {"message": "Player deleted successfully", "ncchash": ncchash}
  except PyMongoError as e:
    raise HTTPException(status_code=500, detail=f"Database error: {e}")
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))
