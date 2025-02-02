from fastapi import HTTPException
from app.db.config import singletons_collection

# Check store status
def happy_hour():
  storeConfig = singletons_collection.find_one({"title": "store_config"})
  if not storeConfig or not storeConfig.get('isOpen', False):
    raise HTTPException(status_code=403, detail="Store is closed. Come back during happy hour")
  return storeConfig.get('isOpen')
