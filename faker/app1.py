import csv
import random
from datetime import datetime, timedelta
from faker import Faker

fake = Faker()

# -----------------------------------
# CONFIG
# -----------------------------------
CUSTOMER_CSV = "r_mobile_customers.csv"
CALL_RECORD_CSV = "r_mobile_call_records.csv"

MIN_CALLS_PER_CUSTOMER = 20
MAX_CALLS_PER_CUSTOMER = 80

# Generate calls in the last N days
DAYS_BACK = 60

# -----------------------------------
# HELPERS
# -----------------------------------

def load_customers(csv_path):
    """Load customers from the R-Mobile customers CSV."""
    customers = []
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            customers.append(row)
    return customers

def random_call_datetime(days_back=DAYS_BACK):
    """Return a random datetime within the last `days_back` days."""
    now = datetime.now()
    start = now - timedelta(days=days_back)
    # Random number of seconds between start and now
    random_seconds = random.randint(0, int((now - start).total_seconds()))
    return start + timedelta(seconds=random_seconds)

def generate_call_record(call_id, customer):
    """
    Generate a single fake call record for a given customer.
    Assumes customer has 'customer_id' and 'phone_number' fields.
    """
    call_time = random_call_datetime()

    # Call duration in seconds (0 for missed)
    is_missed = random.random() < 0.1  # 10% missed calls
    duration_seconds = 0 if is_missed else random.randint(10, 3600)  # up to 1 hour

    # Call type
    call_type = random.choices(
        population=["outgoing", "incoming", "missed"],
        weights=[0.5, 0.4, 0.1],
        k=1
    )[0]

    # Basic roaming flag (small percentage of roaming calls)
    is_roaming = random.random() < 0.05

    # Cost (very rough model)
    # e.g. 0.01 per second domestic, 0.03 per second roaming, none if missed
    if is_missed:
        cost = 0.0
    else:
        rate = 0.03 if is_roaming else 0.01
        cost = round(duration_seconds * rate, 2)

    record = {
        "call_id": call_id,
        "customer_id": customer["customer_id"],
        "customer_phone": customer["phone_number"],
        "other_party_phone": fake.phone_number(),
        "call_type": call_type,             # incoming / outgoing / missed
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
    """Generate a list of call records for all customers."""
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
    """Save call records to CSV."""
    if not call_records:
        print("No call records to save.")
        return

    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=call_records[0].keys())
        writer.writeheader()
        writer.writerows(call_records)

# -----------------------------------
# MAIN
# -----------------------------------

if __name__ == "__main__":
    customers = load_customers(CUSTOMER_CSV)
    print(f"Loaded {len(customers)} customers.")

    call_records = generate_call_records(customers)
    print(f"Generated {len(call_records)} call records.")

    save_call_records(call_records)
    print(f"Saved call records to {CALL_RECORD_CSV}.")
