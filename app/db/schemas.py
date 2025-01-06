from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class RoleEnum(str, Enum):
  player = "player"
  admin = "admin"
  superadmin = "superadmin"

class ExtraItem(BaseModel):
  refUsername: str = Field(..., example="johndoe")
  refNccid: str = Field(..., example="123456")
  incValue: int = Field(..., ge=0, example=5)

class UserProfile(BaseModel):
  fname: str = Field(..., example="john")
  lname: str = Field(..., example="doe")
  role: RoleEnum = Field(..., example="player")
  username: str = Field(..., example="johndoe")
  nccid: str = Field(..., example="123456")
  extra: Optional[List[ExtraItem]] = Field(
    ...,
    example=[{
      "refUsername": "johndoe",
      "refNccid": "123456",
      "incValue": 5,
      "createdAt": "2021-01-01T00:00:00.000Z",
    }],
  )


class PlayerProfile(UserProfile):
  macaddr: str = Field(..., example="00:00:00:00:00:00")
  level: int = Field(..., ge=0, example=0)
  hints: int = Field(..., ge=0, example=3)
  mines: int = Field(..., ge=0, example=3)
  lifelines: int = Field(..., ge=0, example=3)
  score: int = Field(..., ge=0, example=0)

class AdminProfile(UserProfile):
  password: str = Field(..., example="securepassword123")
