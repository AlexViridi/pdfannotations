
from enum import IntEnum
from pydantic import BaseModel, ValidationError, validator
import uuid
from typing import List, Optional, Annotated


class StatusEnum(IntEnum):
    new = 1
    working = 2
    done_annotated = 3
    done_nothing_found = 4
    error = 5

class Documentdetails(BaseModel):
    originalname: str
    newname: str
    id: uuid.UUID
    status: StatusEnum
    errordetails: str



class Annotationjob(BaseModel):
    #id: uuid.UUID | None = None
    id: uuid.UUID = None
    explanations: list
    documentdetails: Optional[list[Documentdetails]]

    @validator('explanations')
    def explanation_must_contain_at_least_one_Value(cls, thelist):
        if thelist is None or len(thelist) < 1:
            raise ValueError('explanations must contain at least one value ')
        return thelist