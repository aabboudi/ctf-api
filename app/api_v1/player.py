import asyncio
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, WebSocket
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
@router.get("/get-player", tags=["Player"])
async def get_player(ncchash: str = Depends(get_current_user)):
  try:
    player = players_collection.find_one({"ncchash": ncchash}, {"_id": 0})
    if player is None:
      raise HTTPException(status_code=404, detail="Player not found")
    return player
  except Exception:
    raise HTTPException(status_code=500, detail="An error occurred while getting player profile")

# Add a new player profile
@router.post("/add-player", tags=["Player"])
async def add_player(player: PlayerProfile):
  try:
    player_exists = players_collection.find_one({"username": player.username})
    if player_exists:
      return JSONResponse(content={"detail": "Username already exist."},  status_code=409)
    player.ncchash = ncchash(ip=player.ipaddr, mac=player.macaddr)
    player.createdAt = datetime.now().isoformat()
    player.updatedAt = datetime.now().isoformat()
    players_collection.insert_one(player.model_dump())
    return JSONResponse(content={"message": "Player account created successfully", "profile": player.model_dump()}, status_code=200)
  except DuplicateKeyError:
    raise HTTPException(status_code=409, detail="Player already exists")
  except Exception as e:
    raise HTTPException(status_code=500, detail="An error occurred while adding a player")

# IPv4 & MAC Based Authentication
@router.post("/authenticate", tags=["Player"])
async def authenticate(request: dbx.AuthenticateRequest):
  player_hash = ncchash(request.ipaddr, request.macaddr)
  try:
    player = players_collection.find_one({"ncchash": player_hash})
    if player is None:
      return JSONResponse(status_code=404, content={"message": "Player not found"})
    access_token_expires = timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    access_token = create_access_token(data={"sub": player_hash}, expires_delta=access_token_expires)
    access_token_expires_seconds = access_token_expires.total_seconds()
    return JSONResponse(
      status_code=200,
      content={
        "player": player,
        "access_token": access_token,
        "access_token_expires": access_token_expires_seconds
        })
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))

# Submit flag
@router.post("/submit-flag", tags=["Player"])
async def submit_flag(request: dbx.SubmitFlagRequest, ncchash: str = Depends(get_current_user)):
  try:
    encrypted_flag = request.flag
    flag = encrypted_flag # decrypt flag
    
    # Validate submission
    db_flag = flags_collection.find_one({"flag": flag}, {"_id": 0})
    db_profile = players_collection.find_one({"ncchash": ncchash}, {"_id": 0})
    
    if not db_flag:
      raise HTTPException(status_code=404, detail="Flag invalid.")

    # Check if player has already captured this flag
    if any(capture["nccid"] == db_profile["nccid"] for capture in db_flag.get('capturedBy', [])):
      raise HTTPException(status_code=409, detail="Flag already captured by you")

    # Add player to capturedBy list
    flags_collection.find_one_and_update(
      {"flag": flag},
      {"$push": {"capturedBy": {"nccid": db_profile["nccid"], "username": db_profile["username"], "capturedAt": datetime.now().isoformat()}}},
      return_document=False
    )

    # Update player score
    db_profile = players_collection.find_one_and_update(
      {"ncchash": ncchash},
      {"$inc": {"score": db_flag["score"]}},
      return_document=True
    )
    return {"message": "Flag submitted successfully", "nccid": db_profile["nccid"], "username": db_profile["username"], "score": db_profile["score"]}
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

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
  await websocket.accept()
  try:
    while True:
      try:
        # Fetch players from the database
        players_cursor = players_collection.find(
          {}, {"_id": 0, "username": 1, "score": 1}
          ).sort("score", -1)
        players = await players_cursor.to_list(length=100)  # Limit to 100 players

        # Send the players data to the client
        await websocket.send_json(players)
      except Exception as e:
        print(f"Error fetching or sending data: {e}")
        await websocket.send_json({"error": "Failed to fetch leaderboard data"})
        break  # Exit the loop on error

        # Wait for 5 seconds before the next update
      await asyncio.sleep(5)
  except Exception as e:
    print(f"WebSocket error: {e}")
  finally:
    await websocket.close()
