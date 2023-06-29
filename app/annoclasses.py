
from enum import IntEnum
from pydantic import BaseModel, ValidationError, validator
import uuid
from typing import List, Optional, Annotated
from datetime import datetime


class StatusEnum(IntEnum):
    new = 1
    working = 2
    done_not_annotated = 3
    done_annotated = 4
    error = 99
   
class JobStatusEnum(IntEnum):
    empty = 1
    working = 2
    done = 3

class Documentdetails(BaseModel):
    originalname: str
    newname: str
    id: uuid.UUID
    status: StatusEnum
    errordetails: str
    created: datetime = None
    changed: datetime = None
    finished: datetime = None



class Annotationjob(BaseModel):
    id: uuid.UUID = None
    explanations: list
    documentdetails: Optional[list[Documentdetails]]
    status: JobStatusEnum = None

    @validator('explanations')
    def explanation_must_contain_at_least_one_Value(cls, thelist):
        if thelist is None or len(thelist) < 1:
            raise ValueError('explanations must contain at least one value ')
        return thelist