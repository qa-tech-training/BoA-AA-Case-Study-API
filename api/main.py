from fastapi import FastAPI, Header, Response, status
from uuid import UUID, uuid4
from typing import Annotated
from random import choice
from datetime import datetime, timedelta
from models import SandBox, Operation, SandBoxCreate, Status, Size
from store import store
import auth

app = FastAPI()

# @app.get("/")
# def info():
#     ...

@app.post("/v1/sandboxes/")
def create_sandbox(body: SandBoxCreate, authorization: Annotated[str, Header()], response: Response):
    auth_info = authorization.split(" ")
    if auth_info[0] != "Bearer":
        response.status_code = status.HTTP_400_BAD_REQUEST
        return "Auth failure: expected Bearer auth"
    if not auth.validate_token(auth_info[1], "create", "sandboxes"):
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return "Unauthorized"
    vm_ip = choice(store.get("ips"))
    store.get("ips").remove(vm_ip)
    expiry_utc = datetime.now() + timedelta(days=body.ttl_days)
    etag = body.name + body.owner_email + str(datetime.now())
    new_op = Operation(_id=uuid4(), rg_name=f"rg-{body.name}", vm_public_ip=vm_ip, expiry_utc=expiry_utc, etag=etag, status=Status.CREATING) 
    response.status_code = status.HTTP_202_ACCEPTED
    return new_op

@app.get("/v1/sandboxes/{uuid}")
def get_sandbox(uuid: str):
    ...

@app.patch("/v1/sandboxes/{uuid}")
def patch_sandbox(uuid: str):
    ...

@app.delete("/v1/sandboxes/{uuid}")
def delete_sandbox(uuid: str):
    ...

@app.get("/v1/operations/{id}")
def get_operations(id: str):
    ...