from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class PlayerProfile(BaseModel):
  fname: str = Field(..., example="John")
  lname: str = Field(..., example="Doe")
  username: str = Field(..., example="johndoe")
  nccid: str = Field(..., example="ncc25-0001")
  ncchash: Optional[str] = None
  macaddr: str = Field(..., example="00:00:00:00:00:00")
  ipaddr: str = Field(..., example="10.10.10.1")

  score: int = Field(..., ge=0, example=0)
  level: int = Field(..., ge=0, example=0)
  lifelines: int = Field(..., ge=0, example=3)
  hints: int = Field(..., ge=0, example=3)
  mines: int = Field(..., ge=0, example=3)

  createdAt: datetime = Field(..., example="2021-01-01T00:00:00.000Z")
  updatedAt: datetime = Field(..., example="2021-01-01T00:00:00.000Z")
