from faker import Faker
import random
import csv

fake = Faker()

# Define sample phone plans
PLANS = [
    {"name": "R-Basic", "monthly_cost": 29.99, "data_gb": 5},
    {"name": "R-Plus",  "monthly_cost": 49.99, "data_gb": 20},
    {"name": "R-Max",   "monthly_cost": 79.99, "data_gb": 100},
    {"name": "R-Unlimited", "monthly_cost": 99.99, "data_gb": -1},  # -1 means unlimited
]

def generate_customer(id):
    plan = random.choice(PLANS)
    
    # Random usage: keep under limits unless unlimited
    if plan["data_gb"] == -1:
        data_used = round(random.uniform(20, 150), 2)
    else:
        data_used = round(random.uniform(0, plan["data_gb"] * 1.5), 2)

    # Generate call/text usage
    minutes_used = random.randint(50, 2000)
    text_messages = random.randint(100, 5000)

    customer = {
        "customer_id": id,
        "full_name": fake.name(),
        "email": fake.email(),
        "phone_number": fake.phone_number(),
        "address": fake.address().replace("\n", ", "),
        "plan_name": plan["name"],
        "monthly_cost": plan["monthly_cost"],
        "data_limit_gb": plan["data_gb"],
        "data_used_gb": data_used,
        "minutes_used": minutes_used,
        "text_messages": text_messages,
        "is_over_data": plan["data_gb"] != -1 and data_used > plan["data_gb"]
    }

    return customer

def generate_customers(n=100):
    return [generate_customer(i+1) for i in range(n)]

def save_to_csv(customers, filename="r_mobile_customers.csv"):
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=customers[0].keys())
        writer.writeheader()
        writer.writerows(customers)

if __name__ == "__main__":
    customers = generate_customers(500)
    save_to_csv(customers)
    print("Generated 50 fake R-Mobile customers and saved to r_mobile_customers.csv.")
