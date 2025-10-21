from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
from enum import Enum 

class Status(str, Enum):
    CREATING = "Creating"
    READY = "Ready"
    TERMINATING = "Terminating"
    TERMINATED = "Terminated"
    UPDATING = "Updating"
    ERROR = "Error"

class Size(str, Enum):
    SMALL = "small" #Standard_B2s
    MEDIUM = "medium" #Standard_B4ms

class SandBoxCreate(BaseModel):
    name: str
    owner_email: str = Field(pattern="^[a-zA-Z0-9._-]+@[a-zA-Z0-9_.-]+.[a-z]{2,3}$")
    size: Size
    ttl_days: int = Field(gt=0, le=30)
    allowed_cidrs: list[str]
    etag: str | None = None

class Operation(BaseModel):
    id: UUID
    rg_name: str
    vm_public_ip: str = Field(pattern="^[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}$")
    username: str | None = "azureuser"
    expiry_utc: datetime
    etag: str
    status: Status

class SandBox(BaseModel):
    id: UUID
    rg_name: str
    nsg_id: str
    expiry_utc: datetime
    etag: str
    allowed_cidrs: list[str]
    vm_public_ip: str = Field(pattern="^[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}$")