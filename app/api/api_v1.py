import asyncio
import os
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, WebSocket
from pymongo.errors import PyMongoError, DuplicateKeyError
from fastapi.responses import JSONResponse
from app.db.schemas import PlayerProfile
from app.db.config import players_collection
from app.includes.Requests import AuthenticateRequest, FlagRequest
from app.includes.Hash import ncchash, create_access_token
from ..db.config import ACCESS_TOKEN_EXPIRE_MINUTES
router = APIRouter()

'''
  Scoring Challenges
'''

challenges_scores = {
  "ncc0": {
    "flag": "ncc0",
    "score": 100
  },
  "ncc1": {
    "flag": "Zy7%RmBx#",
    "score": 150
  },
  "ncc2": {
    "flag": "Lm#2zP9Y$",
    "score": 200
  },
  "ncc3": {
    "flag": "Yd5!jK1W8",
    "score": 200
  },
  "ncc4": {
    "flag": "Xp4@Qe8hF",
    "score": 100
  },
  "ncc5": {
    "flag": "As7#Kd3u!",
    "score": 300
  },
}
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
# Check if username already exist
@router.get("/check-username/{username}", tags=["Player"])
async def check_username(username: str):
  try:
    player = players_collection.find_one({"username": username})
    if player is None:
        return JSONResponse(content={"message": "Username is valid"}, status_code=200)    
    else:
        return JSONResponse(content={"message": "Username already exists"}, status_code=409)    
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))
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
    exist_player = players_collection.find_one({"username": player.username})
    if exist_player is None:
      player.ncchash = ncchash(player.ipaddr, player.macaddr)
      # TODO: Add timezone
      player.createdAt = datetime.now().isoformat()
      player.updatedAt = datetime.now().isoformat()
      players_collection.insert_one(player.model_dump())
      return JSONResponse(content={"message": "Player data received successfully", "data": player.model_dump()}, status_code=200)
    else:
      return JSONResponse(content={"detail": "Username already exist."},  status_code=409)
  except DuplicateKeyError:
    return JSONResponse(status_code=409, content={"detail": "Player already exists"})
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))

# IPv4 & MAC Based Authentication
@router.post("/authenticate", tags=["Player"])
async def authenticate(request: AuthenticateRequest):
  player_hash = ncchash(request.ipaddr, request.macaddr)
  try:
    player = players_collection.find_one({"ncchash": player_hash},  {"_id": 0})
    if player is None:
      return JSONResponse(status_code=404, content={"message": "Player not found"})
    access_token_expires = timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    access_token = create_access_token(data={"sub": player_hash}, expires_delta=access_token_expires)
    # Convert timedelta to seconds
    access_token_expires_seconds = access_token_expires.total_seconds()
    return JSONResponse(
        status_code=200,
        content={
            "player": player,
            "access_token": access_token,
            "access_token_expires": access_token_expires_seconds  # Return as seconds
        }
    )
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))

@router.post("/flag", tags=["Player"])
async def flag(request: FlagRequest):
  try:
    score = 0
    for challenge in challenges_scores.values():
      if challenge["flag"] == request.flag:
        score = challenge["score"]
    
    if score == 0:
      return JSONResponse(status_code=201, content={"message": "Invalid Flag"})
    else:
      players_collection.find_one_and_update(
        {"nccid": request.nccid},
        {"$inc": {"score": score}},
        return_document=True
      )
      return {"message": "Score updated successfully", "nccid": request.nccid, "score": score}
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
