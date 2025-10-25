from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from uuid import UUID
from enum import Enum 
import re

class Status(str, Enum):
    CREATING = "Creating"
    READY = "Ready"
    TERMINATING = "Terminating"
    TERMINATED = "Terminated"
    UPDATING = "Updating"
    ERROR = "Error"

class Size(str, Enum):
    SMALL = "small" #e2-small
    MEDIUM = "medium" #e2-medium

class SandBoxCreate(BaseModel):
    name: str
    owner_email: str = Field(pattern="^[a-zA-Z0-9._-]+@[a-zA-Z0-9_.-]+.[a-z]{2,3}$")
    size: Size
    ttl_days: int = Field(gt=0, le=30)
    allowed_cidrs: list[str]
    id: UUID | None = None

    @field_validator("allowed_cidrs")
    @classmethod
    def validate_cidrs(cls, value):
        valid_cidr = re.compile("^[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}/[0-9]{1,2}$")
        if not all(valid_cidr.match(cidr) for cidr in value):
            raise ValueError("invalid cidr range in allowed_cidrs")
        return value

class Operation(BaseModel):
    id: UUID
    sandbox_id: UUID
    rg_name: str
    username: str | None = "clouduser"
    status: Status
    timestamp: datetime

class SandBox(BaseModel):
    id: UUID
    vm_size: str
    rg_name: str
    nsg_id: str
    expiry_utc: datetime
    etag: str
    allowed_cidrs: list[str]
    vm_public_ip: str = Field(pattern="^[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}$")
