from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from app.db.config import players_collection
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
    raise HTTPException(status_code=500, detail=str(e))
