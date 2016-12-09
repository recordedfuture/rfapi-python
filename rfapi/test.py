import rfapi
from rfapi.query import BaseQuery, ReferenceQuery

q = rfapi.ApiClient()

ent = q.get_entity("B_FAG")
ent.test = 1
ent.apa = {"bepa": 1}
print(ent)


q = BaseQuery({
    "entities": {
        "type": "AttackVector"
    }
})
print(q)

q = ReferenceQuery({
    "type": "CyberAttack"
})
print(q)

