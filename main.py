from fastapi import FastAPI, Header, Response, status, Depends
from fastapi.security import HTTPAuthorizationCredentials
from uuid import UUID, uuid4
from typing import Annotated
from random import choice
from datetime import datetime, timedelta
from models import SandBox, Operation, SandBoxCreate, Status, Size
from store import store
import auth

app = FastAPI()

size_table = {Size.SMALL:"e2-small", Size.MEDIUM:"e2-medium"}

def exists(sandbox_id):
    return any(sb.id == sandbox_id for sb in store.get("sandboxes"))

@app.post("/v1/sandboxes")
def create_sandbox(body: SandBoxCreate, authorization: Annotated[HTTPAuthorizationCredentials, Depends(auth.security)], response: Response):
    if not auth.validate_token(authorization.credentials, "create", "sandboxes"):
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"detail": "token is invalid or does not have the correct access scopes"}
    vm_ip = choice(store.get("ips"))
    store["ips"].remove(vm_ip)
    expiry_utc = datetime.now() + timedelta(days=body.ttl_days)
    etag = body.name + body.owner_email + str(datetime.now())
    etag = etag.replace(" ", "")
    _id = body.id if body.id else uuid4()
    if exists(_id):
        response.status_code = status.HTTP_200_OK
        return {"detail": f"sandbox exists with id {_id}"}
    new_op = Operation(timestamp = datetime.now(), id=uuid4(), sandbox_id=_id, rg_name=f"rg-{body.name}", status=Status.CREATING) 
    store["operations"].append(new_op)
    new_op2 = Operation(timestamp = datetime.now(), id=uuid4(), sandbox_id=_id, rg_name=new_op.rg_name, status=Status.READY)
    store["operations"].append(new_op2)
    sandbox = SandBox(id=_id, rg_name=new_op.rg_name, vm_size=size_table.get(body.size), nsg_id=f"rg-{body.name}-nsg", expiry_utc=expiry_utc, etag=etag, allowed_cidrs=body.allowed_cidrs, vm_public_ip=vm_ip)
    store["sandboxes"].append(sandbox)
    response.status_code = status.HTTP_202_ACCEPTED
    return new_op2

@app.get("/v1/sandboxes/{uuid}")
def get_sandbox(uuid: UUID, authorization: Annotated[HTTPAuthorizationCredentials, Depends(auth.security)], response: Response):
    if not auth.validate_token(authorization.credentials, "list", "sandboxes"):
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"detail": "token is invalid or does not have the correct access scopes"}
    for sb in store.get("sandboxes"):
        if sb.id == uuid:
            response.status_code = status.HTTP_200_OK
            return sb
    response.status_code = status.HTTP_404_NOT_FOUND
    return {"detail": f"no sandbox matching id {uuid}"}

@app.patch("/v1/sandboxes/{uuid}")
def patch_sandbox(if_match: Annotated[str | None, Header()], uuid: UUID, body: SandBoxCreate, authorization: Annotated[HTTPAuthorizationCredentials, Depends(auth.security)], response: Response):
    if not auth.validate_token(authorization.credentials, "update", "sandboxes"):
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"detail": "token is invalid or does not have the correct access scopes"}
    for sb in store["sandboxes"]:
        if not uuid:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"detail": "no sandbox ID specified"}
        if sb.id == uuid:
            if sb.etag != if_match:
                response.status_code = status.HTTP_412_PRECONDITION_FAILED
                return {"detail": "resource version mismatch"}
            new_size = size_table.get(body.size)
            new_expiry_utc = datetime.now() + timedelta(body.ttl_days)
            if sb.vm_size == new_size and sb.expiry_utc == new_expiry_utc:
                response.status_code = status.HTTP_200_OK
                return {"detail": "resource unchanged"}
            response.status_code = status.HTTP_202_ACCEPTED
            new_etag = body.name + body.owner_email + str(datetime.now())
            update_op = Operation(timestamp = datetime.now(), id=uuid4(), sandbox_id=uuid, rg_name=sb.rg_name, status=Status.UPDATING)
            store["operations"].append(update_op)
            sb.expiry_utc = new_expiry_utc
            sb.etag = new_etag
            sb.vm_size = new_size
            update_op2 = Operation(timestamp = datetime.now(), id=uuid4(), sandbox_id=uuid, rg_name=sb.rg_name, status=Status.READY)
            store["operations"].append(update_op2)
            return update_op
    response.status_code = status.HTTP_404_NOT_FOUND
    return {"detail": f"no sandbox matching id {uuid}"}

@app.delete("/v1/sandboxes/{uuid}")
def delete_sandbox(uuid: UUID, authorization: Annotated[HTTPAuthorizationCredentials, Depends(auth.security)], response: Response):
    if not auth.validate_token(authorization.credentials, "delete", "sandboxes"):
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"detail": "token is invalid or does not have the correct access scopes"}
    if not uuid:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"detail": "no sandbox ID specified"}
    for sb in store["sandboxes"]:
        if sb.id == uuid:
            terminating_op = Operation(timestamp = datetime.now(), id=uuid4(), sandbox_id=uuid, rg_name=sb.rg_name, status=Status.TERMINATING)
            store["operations"].append(terminating_op)
            store["ips"].append(sb.vm_public_ip)
            store["sandboxes"].remove(sb)
            terminated_op = Operation(timestamp = datetime.now(), id=uuid4(), sandbox_id=uuid, rg_name=terminating_op.rg_name, status=Status.TERMINATED)
            store["operations"].append(terminated_op)
            response.status_code = status.HTTP_202_ACCEPTED
            return terminated_op
    response.status_code = status.HTTP_200_OK
    return {"detail": "already deleted"}

@app.get("/v1/operations/{id}")
def get_operations(id: UUID, authorization: Annotated[HTTPAuthorizationCredentials, Depends(auth.security)], response: Response):
    if not auth.validate_token(authorization.credentials, "list", "operations"):
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"detail": "token is invalid or does not have the correct access scopes"}
    if not id:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"detail": "no sandbox ID specified"}
    response.status_code = status.HTTP_200_OK
    return sorted([op for op in store.get("operations") if op.sandbox_id == id], key = lambda o: o.timestamp)
