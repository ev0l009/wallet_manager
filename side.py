trxs = [
    {"amt": 50, "status": "exp"},
    {"amt": 25, "status": "inc"},
    {"amt": 50, "status": "rev"},
    {"amt": 1200, "status": "inc"},
    {"amt": 350, "status": "exp"},
    {"amt": 80, "status": "exp"},
    {"amt": 80, "status": "rev"},
    {"amt": 45, "status": "exp"},
    {"amt": 500, "status": "inc"},
    {"amt": 150, "status": "exp"},
    {"amt": 300, "status": "inc"},
    {"amt": 300, "status": "rev"},
    {"amt": 65, "status": "exp"},
    {"amt": 200, "status": "exp"},
    {"amt": 950, "status": "inc"},
    {"amt": 110, "status": "exp"},
    {"amt": 110, "status": "rev"},
    {"amt": 40, "status": "exp"},
    {"amt": 750, "status": "inc"},
    {"amt": 220, "status": "exp"}
]

net_inc = sum([
    t["amt"] for t in trxs
    if t["status"] = "inc"
])
net_exp = sum([
    t["amt"] for t in trxs
    if t["status"] = "exp"
])

bal = net_inc-net_exp

print(bal)