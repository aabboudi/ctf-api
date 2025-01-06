from pydantic import BaseModel, Field


class AuthenticateRequest(BaseModel):
    macaddr: str = Field(..., example="00:00:00:00:00:00")
    ipaddr: str = Field(..., example="10.10.10.1")
    