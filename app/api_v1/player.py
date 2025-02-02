import asyncio
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, WebSocket
from pymongo.errors import PyMongoError
from fastapi.responses import JSONResponse
from app.db import partials as dbx
from app.db.config import players_collection, flags_collection
from app.lib.hash import decrypt_flag
from app.lib.auth import get_current_user
router = APIRouter()

'''
Player Profile Management
'''
# Get player profile
@router.get("/get-player", tags=["Player"])
async def get_player(ncchash: str = Depends(get_current_user)):
  try:
    player = players_collection.find_one({"ncchash": ncchash}, {"_id": 0})
    if player is None:
      raise HTTPException(status_code=404, detail="Player not found")
    
    # Remove sensitive data from response object
    player.pop("ncchash", None)
    player.pop("isAdmin", None)
    return JSONResponse(status_code=200, content={"player": player})
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))

# Submit flag
@router.post("/submit-flag", tags=["Player"])
async def submit_flag(request: dbx.SubmitFlagRequest, ncchash: str = Depends(get_current_user)):
  try:
    encrypted_flag = request.flag
    flag = decrypt_flag(ncchash=ncchash, ciphertext=encrypted_flag)
    
    # Validate submission
    db_flag = flags_collection.find_one({"flag": flag}, {"_id": 0})
    if not db_flag:
      raise HTTPException(status_code=404, detail="Flag invalid")

    # Check if player has already captured this flag
    db_profile = players_collection.find_one({"ncchash": ncchash}, {"_id": 0})
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
    return JSONResponse(status_code=200, content={
      "message": "Flag submitted successfully",
      "nccid": db_profile["nccid"],
      "username": db_profile["username"],
      "score": db_profile["score"]
    })
  except HTTPException as e:
    raise HTTPException(status_code=e.status_code, detail=str(e))
  except Exception as e:
    raise HTTPException(status_code=404, detail="Flag invalid")

# Delete a player profile
@router.delete("/delete-player", tags=["Player"])
async def delete_player(ncchash: str = Depends(get_current_user)):
  try:
    profile = players_collection.delete_one({"ncchash": ncchash})
    if profile.deleted_count == 0:
      raise HTTPException(status_code=404, detail="Player not found")
    return JSONResponse(status_code=200, content={"message": "Player deleted successfully", "nccid": profile["nccid"]})
  except PyMongoError:
    raise HTTPException(status_code=500, detail="Database error: an error occurred while deleting this player")
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
