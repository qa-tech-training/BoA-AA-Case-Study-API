from fastapi.security import HTTPBearer

security = HTTPBearer()

valid_tokens = [('byy27wsb0gjeodps2kd0re9d.71j0gx1', ["sandboxes:list"]), 
                ('q6zn6o28056ia3hfesl0j4be7p16wcgw', ["sandboxes:list", "sandboxes:create", "operations:list"]), 
                ('0r61bm74t1jiymxnq3qqf2pwvplkj13a', ["sandboxes:list", "sandboxes:create", "sandboxes:delete", "operations:list"]),
                ('ro5b64n4kehaurbuofkfbmnrhvxn0.yk', ["sandboxes:list"]),
                ('mpzn3oqk3ymaijybadhcssh5nf.mpri0', ["sandboxes:list", "operations:list"]),
                ('5vgud9glj60q1xrd.uicpjru.xxr8jhd', ["sandboxes:list", "sandboxes:create", "sandboxes:update", "sandboxes:delete", "operations:list"]),
                ('9nvd5y5.jlyh1e93zmo50nk3wpynxin.', ["sandboxes:create", "operations:list", "sandboxes:delete"]),
                ('4bvnx.c02koyvujjwsn7dan.iw0ow9ej', ["sandboxes:list", "sandboxes:update", "operations:list"]),
                ('jtl.pmxmkvsrnu87m0eywx0vms4u8iv2', ["sandboxes:list"]),
                ('4ryebmgw3q0hdv1ksgr.2rb0f6dvr2j2', ["sandboxes:list"])]

def validate_token(token, op, resource):
    global valid_tokens
    for t in valid_tokens:
        if t[0] == token:
            return f"{resource}:{op}" in t[1]
    return False
