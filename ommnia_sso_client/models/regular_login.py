from enum import Enum
from typing import Annotated, Literal, Optional, Union
from pydantic import BaseModel, Field


class RegularLoginRequest(BaseModel):
    email: str
    password: str
    token: str


class RegularLoginFailureCode(Enum):
    USER_NOT_FOUND = "USER_NOT_FOUND"
    WRONG_PASSWORD = "WRONG_PASSWORD"
    USER_NOT_ACTIVE = "USER_NOT_ACTIVE"
    INSUFFICIENT_PERMISSIONS = "INSUFFICIENT_PERMISSIONS"
    INVALID_TOKEN = "INVALID_TOKEN"
    SESSION_NOT_FOUND = "SESSION_NOT_FOUND"
    SESSION_COMLETED = "SESSION_COMPLETED"
    SESSION_EXPIRED = "SESSION_EXPIRED"


class RegularLoginFailureResponse(BaseModel):
    typename: Literal["RegularLoginFailureResponse"] = "RegularLoginFailureResponse"
    code: RegularLoginFailureCode
    message: Optional[str]


class RegularLoginSuccessResponse(BaseModel):
    typename: Literal["RegularLoginSuccessResponse"] = "RegularLoginSuccessResponse"
    token: str


RegularLoginResponse = Annotated[
    Union[RegularLoginFailureResponse, RegularLoginSuccessResponse],
    Field(discriminator="typename"),
]
