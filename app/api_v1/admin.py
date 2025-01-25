from datetime import datetime
from fastapi import APIRouter, HTTPException
from app.db.config import players_collection
router = APIRouter()

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
