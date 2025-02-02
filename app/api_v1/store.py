from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from app.db.config import players_collection, flags_collection, store_collection, singletons_collection
from app.lib.auth import get_current_user, verify_admin_user
from app.lib.utils import happy_hour
router = APIRouter()

'''
Store Transactions
'''
# Is store open
@router.get("/is-open", tags=["Store", "Player"])
async def is_happy_hour(ncchash: str = Depends(get_current_user)):
  try:
    player = players_collection.find_one({"ncchash": ncchash})
    if player is None:
      return HTTPException(status_code=404, content="Player not found")
    
    store_open = happy_hour()
    return store_open
  except HTTPException as e:
    raise HTTPException(status_code=e.status_code, detail=str(e))
  except Exception:
    raise HTTPException(status_code=400, detail="Unhandled error fetching happy hour status")

# Unlock store
@router.post("/unlock", tags=["Store", "Player"])
async def unlock_store(ncchash: str = Depends(get_current_user)):
  try:
    player = players_collection.find_one({"ncchash": ncchash})
    if player is None:
      return HTTPException(status_code=404, content="Player not found")
    
    if player["storeUnlocked"] is True:
      return JSONResponse(status_code=200, content="Store is already unlocked")
    
    unlock_store_at = singletons_collection.find_one({"title": "store_config"})["unlock_store_at"]
    
    if player["score"] < unlock_store_at:
      raise HTTPException(status_code=403, detail="Player must reach 2000 points to unlock store")
    
    players_collection.find_one_and_update(
      {"ncchash": ncchash},
      {"$set": {"storeUnlocked": True}},
      return_document=False
    )
    return JSONResponse(status_code=200, content="Store is now unlocked. Happy shopping!")
  except HTTPException as e:
    raise HTTPException(status_code=e.status_code, detail=str(e))
  except Exception:
    raise HTTPException(status_code=400, detail="Transaction failed")

'''
Store Management
'''
# Open or close store
@router.post("/status", tags=["Store", "Admin"])
async def update_store_status(status: str, admin_nccid: str = Depends(verify_admin_user)):
  try:
    store_config = singletons_collection.find_one({"title": "store_config"})
    is_currently_open = store_config.get("isOpen", False)

    if (status.lower() == "open" and is_currently_open) or (status.lower() == "closed" and not is_currently_open):
      return JSONResponse(status_code=200, content=f"Store status is already {status}")
    
    singletons_collection.find_one_and_update(
      {"title": "store_config"},
      {"$set": {"isOpen": status.lower() == "open"}},
      return_document=False
    )

    return JSONResponse(status_code=200, content=f"Store status changed to {status}")
  except HTTPException as e:
    raise HTTPException(status_code=e.status_code, detail=str(e))
  except Exception:
    raise HTTPException(status_code=400, detail="Unhanlded error opening store")
