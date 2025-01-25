from fastapi import Depends, HTTPException
from app.db.config import SECRET_KEY, ALGORITHM, players_collection
from app.lib.hash import oauth2_scheme
from jose import JWTError, jwt

# Validate user token
def get_current_user(token: str = Depends(oauth2_scheme)):
  try:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    ncchash: str = payload.get("sub")
    if ncchash is None:
      raise HTTPException(
        status_code=401,
        detail="Invalid token",
        headers={"WWW-Authenticate": "Bearer"},
      )
    return ncchash
  except JWTError:
    raise HTTPException(
      status_code=401,
      detail="Could not validate credentials",
      headers={"WWW-Authenticate": "Bearer"},
    )

# Validate admin token
def verify_admin_user(ncchash: str = Depends(get_current_user)):
  if not ncchash:
    raise HTTPException(status_code=403, detail="Invalid token")
  
  profile = players_collection.find_one({"ncchash": ncchash}, {"_id": 0})
  if not profile["isAdmin"]:
    raise HTTPException(status_code=403, detail="Insufficient privileges")

  return profile["nccid"]
