from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from pymongo.errors import DuplicateKeyError
from app.db import partials as dbx
from app.db.schemas import PlayerProfile
from app.db.config import ACCESS_TOKEN_EXPIRE_MINUTES, players_collection, flags_collection, store_collection
from app.lib.auth import get_current_user
from app.lib.hash import create_ncchash, create_access_token
router = APIRouter()

'''
General API Status
'''
# Get health status of the API
@router.get("/", tags=["General"])
def health_check():
  return {"Status": "Running"}

# Check if username already exist
@router.get("/check-username", tags=["General"])
async def check_username(username: str):
  try:
    if len(username)<3:
      raise HTTPException(status_code=400, detail="Username must be longer than 3 character")
    player = players_collection.find_one({"username": username})
    if player is None:
      return JSONResponse(content={"message": "Username is valid"}, status_code=200)    
    else:
      raise HTTPException(status_code=409, detail="Username already exists")
  except Exception as e:
    raise HTTPException(status_code=500, detail="An error occurred while checking the username")

'''
Auth
'''
# Add a new player profile
@router.post("/signup", tags=["Auth"])
async def add_player(player: PlayerProfile):
  try:
    player_exists = players_collection.find_one({"username": player.username})
    if player_exists:
      raise HTTPException(status_code=409, detail="Username already exists")
    player.ncchash = create_ncchash(ip=player.ipaddr, mac=player.macaddr)
    player.createdAt = datetime.now().isoformat()
    player.updatedAt = datetime.now().isoformat()
    players_collection.insert_one(player.model_dump())

    # Remove sensitive data from response object
    player = player.model_dump()
    player.pop("ncchash", None)
    player.pop("isAdmin", None)
    return JSONResponse(status_code=200, content={"message": "Player account created successfully", "profile": player})
  except DuplicateKeyError:
    raise HTTPException(status_code=409, detail="Player already exists")
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))

# IPv4 & MAC Based Authentication
@router.post("/login", tags=["Auth"])
async def authenticate(request: dbx.AuthenticateRequest):
  player_hash = create_ncchash(request.ipaddr, request.macaddr)
  try:
    player = players_collection.find_one({"ncchash": player_hash})
    if player is None:
      return JSONResponse(status_code=404, content={"message": "Player not found"})
    expires = timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    access_token = create_access_token(data={"sub": player_hash}, expires_delta=expires)
    expires_seconds = expires.total_seconds()
    return JSONResponse(status_code=200, content={"access_token": access_token, "expires": expires_seconds})
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))

'''
Stats
'''
@router.get("/stats/{mode}", tags=["General"])
async def get_ctf_stats(mode: str, ncchash: str = Depends(get_current_user)):
  try:
    if mode not in ["players", "flags", "store"]:
      raise HTTPException(status_code=400, detail="Stats mode invalid")
    
    if mode == "players":
      stats = players_collection.count_documents({})
    elif mode == "flags":
      stats = flags_collection.count_documents({})
    elif mode == "store":
      stats = store_collection.count_documents({})
    
    return JSONResponse(status_code=200, content={"mode": mode, "total": stats})
  except HTTPException as e:
    raise HTTPException(status_code=e.status_code, detail=str(e))
  except Exception:
    raise HTTPException(status_code=400, detail=f"Unhandled error getting total {mode}")
