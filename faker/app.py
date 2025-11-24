from faker import Faker
import random
import csv
from datetime import datetime, timedelta

fake = Faker()

# -----------------------------
# CONFIG
# -----------------------------
CUSTOMER_COUNT = 500
CUSTOMER_CSV = "r_mobile_customers.csv"
CALL_RECORD_CSV = "r_mobile_call_records.csv"

MIN_CALLS_PER_CUSTOMER = 20
MAX_CALLS_PER_CUSTOMER = 80
DAYS_BACK = 60  # how far back call records can go


# -----------------------------
# CUSTOMER GENERATION
# -----------------------------

# Define sample phone plans
PLANS = [
    {"name": "R-Basic", "monthly_cost": 29.99, "data_gb": 5},
    {"name": "R-Plus",  "monthly_cost": 49.99, "data_gb": 20},
    {"name": "R-Max",   "monthly_cost": 79.99, "data_gb": 100},
    {"name": "R-Unlimited", "monthly_cost": 99.99, "data_gb": -1},  # -1 means unlimited
]

# Toll-free prefix blacklist
TOLL_FREE_PREFIXES = {800, 833, 844, 855, 866, 877, 888}


def mobile_phone_number():
    """
    Generate a realistic US-style mobile number with:
    - no extensions
    - no toll-free numbers
    Format: NXX-NXX-XXXX (N != 0/1)
    """
    while True:
        area = random.randint(200, 999)
        prefix = random.randint(200, 999)

        # Block toll-free prefixes entirely
        if area in TOLL_FREE_PREFIXES or prefix in TOLL_FREE_PREFIXES:
            continue

        # Otherwise valid
        line = random.randint(1000, 9999)
        return f"{area}-{prefix}-{line}"


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
        "phone_number": mobile_phone_number(),  # clean mobile number
        "address": fake.address().replace("\n", ", "),
        "plan_name": plan["name"],
        "monthly_cost": plan["monthly_cost"],
        "data_limit_gb": plan["data_gb"],
        "data_used_gb": data_used,
        "minutes_used": minutes_used,
        "text_messages": text_messages,
        "is_over_data": plan["data_gb"] != -1 and data_used > plan["data_gb"],
    }

    return customer


def generate_customers(n=CUSTOMER_COUNT):
    return [generate_customer(i + 1) for i in range(n)]


def save_customers_to_csv(customers, filename=CUSTOMER_CSV):
    if not customers:
        print("No customers to save.")
        return

    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=customers[0].keys())
        writer.writeheader()
        writer.writerows(customers)


def load_customers(csv_path=CUSTOMER_CSV):
    customers = []
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            customers.append(row)
    return customers


# -----------------------------
# CALL RECORD GENERATION
# -----------------------------

def random_call_datetime(days_back=DAYS_BACK):
    """Return a random datetime within the last `days_back` days."""
    now = datetime.now()
    start = now - timedelta(days=days_back)
    random_seconds = random.randint(0, int((now - start).total_seconds()))
    return start + timedelta(seconds=random_seconds)


def generate_call_record(call_id, customer):
    """
    Generate a fake call record.
    All phone numbers use our filtered mobile format.
    """
    call_time = random_call_datetime()

    is_missed = random.random() < 0.1  # 10% missed calls
    duration_seconds = 0 if is_missed else random.randint(10, 3600)

    call_type = random.choices(
        population=["outgoing", "incoming", "missed"],
        weights=[0.5, 0.4, 0.1],
        k=1,
    )[0]

    is_roaming = random.random() < 0.05

    if is_missed:
        cost = 0.0
    else:
        rate = 0.03 if is_roaming else 0.01
        cost = round(duration_seconds * rate, 2)

    record = {
        "call_id": call_id,
        "customer_id": customer["customer_id"],
        "customer_phone": customer["phone_number"],
        "other_party_phone": mobile_phone_number(),  # no toll-free either
        "call_type": call_type,
        "start_time": call_time.isoformat(sep=" ", timespec="seconds"),
        "duration_seconds": duration_seconds,
        "is_missed": is_missed,
        "is_roaming": is_roaming,
        "cell_tower_city": fake.city(),
        "cell_tower_country": fake.country(),
        "cost_usd": cost,
    }
    return record


def generate_call_records(customers):
    call_records = []
    call_id = 1

    for customer in customers:
        num_calls = random.randint(MIN_CALLS_PER_CUSTOMER, MAX_CALLS_PER_CUSTOMER)
        for _ in range(num_calls):
            record = generate_call_record(call_id, customer)
            call_records.append(record)
            call_id += 1

    return call_records


def save_call_records(call_records, filename=CALL_RECORD_CSV):
    if not call_records:
        print("No call records to save.")
        return

    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=call_records[0].keys())
        writer.writeheader()
        writer.writerows(call_records)


# -----------------------------
# MAIN
# -----------------------------

if __name__ == "__main__":
    # 1) Generate customers
    customers = generate_customers(CUSTOMER_COUNT)
    save_customers_to_csv(customers)
    print(f"Generated {len(customers)} customers and saved to {CUSTOMER_CSV}.")

    # 2) Generate call records
    customers_loaded = load_customers(CUSTOMER_CSV)
    call_records = generate_call_records(customers_loaded)
    save_call_records(call_records)
    print(f"Generated {len(call_records)} call records and saved to {CALL_RECORD_CSV}.")
