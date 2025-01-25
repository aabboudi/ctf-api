from fastapi import APIRouter, HTTPException
from pymongo.errors import PyMongoError
from app.db.config import players_collection
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
