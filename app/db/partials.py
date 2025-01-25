from enum import Enum
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime

class ExtraItem(BaseModel):
  refUsername: str = Field(..., example="johndoe")
  refNccid: str = Field(..., example="123456")
  incValue: int = Field(..., ge=0, example=5)

class FlagType(str, Enum):
  main = "main"
  side = "side"

class CapturedBy(BaseModel):
  id: int = Field(..., description="ID of the capturer")
  nccid: str = Field(..., description="Username of the capturer")
  capturedAt: datetime = Field(..., description="Timestamp of when it was captured")

class FlagInput(BaseModel):
  flag: str = Field(min_length=10, description="Flag must be at least 10 characters long")
  score: int = Field(gt=0, example=1, default=10, description="Score must be greater than 0")
  type: FlagType

class Flag(BaseModel):
  flagInput: FlagInput
  capturedBy: List[CapturedBy] | None = Field(
    default_factory=list,
    description="List of capturers, each with id, username, and timestamp. Can be empty.",
  )

# Request body schema
class AddPointsRequest(BaseModel):
  nccid: str
  score: int

# Define the request body schema using Pydantic
class SubmitFlagRequest(BaseModel):
  flag: str

class AuthenticateRequest(BaseModel):
  macaddr: str = Field(..., example="00:00:00:00:00:00")
  ipaddr: str = Field(..., example="10.10.10.1")
