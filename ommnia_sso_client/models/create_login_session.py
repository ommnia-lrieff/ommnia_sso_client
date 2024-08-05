from typing import Annotated, Literal, Optional, Union
from pydantic import BaseModel, Field
from enum import Enum


class CreateLoginSessionFailureCode(Enum):
    INVALID_REQUEST_TOKEN = "INVALID_REQUEST_TOKEN"
    SERVER_ERROR = "SERVER_ERROR"


class CreateLoginSessionFailureResponse(BaseModel):
    typename: Literal["CreateLoginSessionFailureResponse"] = "CreateLoginSessionFailureResponse"
    code: CreateLoginSessionFailureCode
    message: Optional[str]


class CreateLoginSessionSuccessResponse(BaseModel):
    typename: Literal["CreateLoginSessionSuccessResponse"] = "CreateLoginSessionSuccessResponse"
    token: str


CreateLoginSessionResponse = Annotated[
    Union[CreateLoginSessionFailureResponse, CreateLoginSessionSuccessResponse],
    Field(discriminator="typename"),
]
