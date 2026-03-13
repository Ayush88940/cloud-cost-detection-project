import pandas as pd
import random

teams = ["Development","Operations","Data","R&D"]

data = []

for team in teams:
    for i in range(1,5):
        data.append({
            "team": team,
            "employee": f"{team}_Emp{i}",
            "cpu_usage": random.randint(10,80),
            "ram_usage": random.randint(2,16)
        })

df = pd.DataFrame(data)

df.to_csv("company_usage.csv", index=False)

print("Sample data generated.")