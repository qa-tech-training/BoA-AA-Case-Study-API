from fastapi.security import HTTPBearer
import json

security = HTTPBearer()

tokfile = open('valid_tokens.json', 'r')
valid_tokens = json.load(tokfile)
tokfile.close()

def validate_token(token, op, resource):
    global valid_tokens
    for t in valid_tokens:
        if t["token"] == token:
            return f"{resource}:{op}" in t["scopes"]
    return False
