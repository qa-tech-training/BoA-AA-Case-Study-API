from random import randint
store = {
    "sandboxes": [], 
    "operations": [], 
    "ips": [".".join(str(randint(0,255)) for i in range(4)) for i in range(100)]
}
