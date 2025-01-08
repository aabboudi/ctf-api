from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum
from datetime import datetime

from pydantic.config import ConfigDict

class RoleEnum(str, Enum):
  player = "player"
  admin = "admin"
  superadmin = "superadmin"

class ExtraItem(BaseModel):
  refUsername: str = Field(..., example="johndoe")
  refNccid: str = Field(..., example="123456")
  incValue: int = Field(..., ge=0, example=5)

class UserProfile(BaseModel):
  firstname: str = Field(..., example="john")
  lastname: str = Field(..., example="doe")
  role: RoleEnum | None = Field(example="player", default=None)
  username: str = Field(..., example="johndoe")
  nccid: str = Field(..., example="123456")
  extra: Optional[List[ExtraItem]] | None = Field(
    default=None,
    example=[{
      "refUsername": "johndoe",
      "refNccid": "123456",
      "incValue": 5,
      "createdAt": "2021-01-01T00:00:00.000Z",
    }],
  )
  createdAt: datetime | None = Field(deafult=None, example="2025-01-01 10:00:00")
  updatedAt: datetime | None = Field(deafult=None, example="2025-01-01 10:00:00")


class PlayerProfile(UserProfile):
  ncchash: str | None = Field(example="5436dpiueaydiuh", default=None)
  ipaddr: str | None = Field(example="127.0.0.1", default=None)
  macaddr: str | None = Field(example="00:00:00:00:00:00", default=None)
  level: int = Field(ge=0, example=0, default=0)
  hints: int = Field(ge=0, example=3, default=0)
  mines: int = Field(ge=0, example=3, default=0)
  lifelines: int = Field(ge=0, example=3, default=0)
  score: int = Field(ge=0, example=0, default=0)

class AdminProfile(UserProfile):
  password: str = Field(..., example="securepassword123")
