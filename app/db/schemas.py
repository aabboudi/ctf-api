from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from app.db.partials import ExtraItem

class UserProfile(BaseModel):
  firstname: str = Field(..., example="john")
  lastname: str = Field(..., example="doe")
  isAdmin: bool = Field(default=False, description="Indicates if the entity is active")
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
  createdAt: datetime | None = Field(deafult=None, example="2025-01-25T17:16:50.555+00:00")
  updatedAt: datetime | None = Field(deafult=None, example="2025-01-25T17:16:50.555+00:00")


class PlayerProfile(UserProfile):
  ncchash: str | None = Field(example="5436dpiueaydiuh", default=None)
  ipaddr: str = Field(example="127.0.0.1", default=None)
  macaddr: str = Field(example="00:00:00:00:00:00", default=None)
  level: int | None = Field(ge=0, example=0, default=0)
  hints: int | None = Field(ge=0, example=3, default=0)
  mines: int | None = Field(ge=0, example=3, default=0)
  lifelines: int | None = Field(ge=0, example=3, default=0)
  score: int | None = Field(ge=0, example=0, default=0)

class AdminProfile(UserProfile):
  password: str = Field(..., example="securepassword123")
