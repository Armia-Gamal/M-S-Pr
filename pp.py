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

data = pd.read_excel(r"c:\Users\Armia Gamal\Downloads\project\icecream_data.xlsx")

avg_cone_scoops = data[data["order"] == "cone"]["scoops"].mean()
avg_sundae_scoops = data[data["order"] == "sundae"]["scoops"].mean()

def fix_order(row):
    order = row["order"]
    scoops = row["scoops"]
    
    if order not in ["cone", "sundae"]:
        if abs(scoops - avg_cone_scoops) <= abs(scoops - avg_sundae_scoops):
            return "cone"
        else:
            return "sundae"

    return order

data["order"] = data.apply(fix_order, axis=1)
print(data)

class Customer:
    
    def __init__(self, customer_id, arrival_time, order, scoops):
        self.customer_id = customer_id
        self.arrival_time = arrival_time
        self.order = order
        self.scoops = scoops
        self.finish_time = None

    def order_sim(self, env, servers):

        yield env.timeout(self.arrival_time - env.now)
        print(f"Time {env.now:.1f}: Customer {self.customer_id} ARRIVED")
        print(f"({self.order}, {self.scoops} scoops)")
        print(f"Queue length: {len(servers.queue)} | ")
        print(f"Busy servers: {servers.count}/2")

        with servers.request() as request:
            yield request

            print(f"Time {env.now:.1f}: Customer {self.customer_id} START service")
            print(f"Server status: {servers.count}/2 busy | ")
            print(f"Queue length: {len(servers.queue)}")

            if self.order == "cone":
                service_time = 2 + self.scoops * 1
            elif self.order == "sundae":
                service_time = 4 + self.scoops * 1.5

            print(f"Current order -> Customer {self.customer_id}, ")
            print(f"{self.order}, {self.scoops} scoops, ")
            print(f"Service time: {service_time:.1f}")

            yield env.timeout(service_time)

            self.finish_time = env.now

            print(f"Time {env.now:.1f}: Customer {self.customer_id} FINISHED service")
            print(f"Server status: {servers.count - 1}/2 busy | ")
            print(f"Queue length: {len(servers.queue)}")
            print("-" * 60)


env = simpy.Environment()
servers = simpy.Resource(env, capacity=2)
input_path = r"c:\Users\Armia Gamal\Downloads\project\icecream_data_update.xlsx"

customers_list = []

for index, row in data.iterrows():
    customer = Customer(
        row["customer_id"],
        row["arrival_time"],
        row["order"],
        row["scoops"]
    )
    customers_list.append(customer)
    env.process(customer.order_sim(env, servers))

env.run()

data["finish_time"] = [c.finish_time for c in customers_list]
data.to_excel(input_path, index=False)
