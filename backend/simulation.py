# ---------------------------------------------------
# Modeling & Simulation Project - Ice Cream Shop    |
# Team Members:                                     |
# 1. Armia Gamal            - ID: 352250706         |
# 2. Sara Essam             - ID: 352250785         |
# 3. Shada Ayman            - ID: 352250738         |
# 4. Salsabel esmail        - ID: 352250787         |
# 5. Sherif karam           - ID: 352250808         |
# 6. Ziad Walid Mokhtar     - ID: 352250783         |
# 7. Peter Bolbol           - ID: 352250738         |
# Debartment: CS & Statistics                       |
# Under the supervision of: Dr. Hesham - Dr. Alaa   |
# ---------------------------------------------------

import pandas as pd
import simpy
import json

data = pd.read_excel("icecream_data.xlsx")

avg_cone = data[data["order"] == "cone"]["scoops"].mean()
avg_sun = data[data["order"] == "sundae"]["scoops"].mean()

def fix_order(row):
    if row["order"] not in ["cone", "sundae"]:
        return "cone" if abs(row["scoops"] - avg_cone) <= abs(row["scoops"] - avg_sun) else "sundae"
    return row["order"]

data["order"] = data.apply(fix_order, axis=1)

events = []

class Customer:
    def __init__(self, cid, arrival, order, scoops):
        self.cid = cid
        self.arrival = arrival
        self.order = order
        self.scoops = scoops
        self.finish_time = None

    def process(self, env, cashiers):
        yield env.timeout(self.arrival - env.now)

        events.append({
            "time": round(env.now, 2),
            "type": "ARRIVED",
            "customer": self.cid
        })

        cashier_id = yield cashiers.get()

        start = env.now
        wait = start - self.arrival

        service_time = (
            2 + self.scoops if self.order == "cone"
            else 4 + self.scoops * 1.5
        )

        events.append({
            "time": round(env.now, 2),
            "type": "START",
            "customer": self.cid,
            "order": self.order,
            "scoops": int(self.scoops),
            "wait": round(wait, 2),
            "service": round(service_time, 2),
            "cashier": cashier_id
        })

        yield env.timeout(service_time)

        self.finish_time = env.now

        events.append({
            "time": round(env.now, 2),
            "type": "FINISH",
            "customer": self.cid,
            "order": self.order,
            "scoops": int(self.scoops),
            "total": round(self.finish_time - self.arrival, 2),
            "cashier": cashier_id
        })

        yield cashiers.put(cashier_id)

env = simpy.Environment()

cashiers = simpy.Store(env)
cashiers.put(1)
cashiers.put(2)

customers = []

for _, row in data.iterrows():
    c = Customer(
        row["customer_id"],
        row["arrival_time"],
        row["order"],
        row["scoops"]
    )
    customers.append(c)
    env.process(c.process(env, cashiers))

env.run()

data["finish_time"] = [c.finish_time for c in customers]
data.to_csv("icecream_data_update.csv", index=False)

with open("events.json", "w", encoding="utf-8") as f:
    json.dump(events, f, indent=2)

print("events.json saved")
print("icecream_data_update.csv saved")