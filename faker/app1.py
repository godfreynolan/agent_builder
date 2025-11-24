import sqlite3
import pandas as pd
from pathlib import Path

# -----------------------
# FILE PATHS
# -----------------------
PLANS_FILE = "r_mobile_plans.xlsx"
CUSTOMERS_FILE = "r_mobile_customers.csv"
CALLS_FILE = "r_mobile_call_records.csv"
DB_FILE = "r_mobile.db"


def load_data():
    plans_df = pd.read_excel(PLANS_FILE)
    customers_df = pd.read_csv(CUSTOMERS_FILE)
    calls_df = pd.read_csv(CALLS_FILE)
    return plans_df, customers_df, calls_df


def create_connection(db_file):
    conn = sqlite3.connect(db_file)
    # Enable foreign keys
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def create_tables(conn):
    cur = conn.cursor()

    # Drop tables if they already exist (optional, for clean reruns)
    cur.execute("DROP TABLE IF EXISTS call_records;")
    cur.execute("DROP TABLE IF EXISTS customers;")
    cur.execute("DROP TABLE IF EXISTS plans;")

    # plans table
    cur.execute(
        """
        CREATE TABLE plans (
            plan_id INTEGER PRIMARY KEY,
            plan_name TEXT UNIQUE NOT NULL,
            plan_type TEXT,
            monthly_price_usd REAL,
            data_gb INTEGER,
            talk_minutes INTEGER,
            text_messages INTEGER,
            hotspot_data_gb INTEGER,
            international_minutes INTEGER,
            roaming_data_gb INTEGER,
            overage_per_gb_usd REAL,
            contract_length_months INTEGER
        );
        """
    )

    # customers table
    cur.execute(
        """
        CREATE TABLE customers (
            customer_id INTEGER PRIMARY KEY,
            full_name TEXT,
            email TEXT,
            phone_number TEXT,
            address TEXT,
            plan_id INTEGER,
            monthly_cost REAL,
            data_limit_gb REAL,
            data_used_gb REAL,
            minutes_used INTEGER,
            text_messages INTEGER,
            is_over_data INTEGER,
            FOREIGN KEY (plan_id) REFERENCES plans(plan_id)
        );
        """
    )

    # call_records table
    cur.execute(
        """
        CREATE TABLE call_records (
            call_id INTEGER PRIMARY KEY,
            customer_id INTEGER NOT NULL,
            customer_phone TEXT,
            other_party_phone TEXT,
            call_type TEXT,
            start_time TEXT,
            duration_seconds INTEGER,
            is_missed INTEGER,
            is_roaming INTEGER,
            cell_tower_city TEXT,
            cell_tower_country TEXT,
            cost_usd REAL,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        );
        """
    )

    conn.commit()


def insert_plans(conn, plans_df):
    cur = conn.cursor()
    rows = [
        (
            int(row["plan_id"]),
            row["plan_name"],
            row.get("plan_type"),
            float(row.get("monthly_price_usd", 0) or 0),
            int(row.get("data_gb", 0) or 0),
            int(row.get("talk_minutes", 0) or 0),
            int(row.get("text_messages", 0) or 0),
            int(row.get("hotspot_data_gb", 0) or 0),
            int(row.get("international_minutes", 0) or 0),
            int(row.get("roaming_data_gb", 0) or 0),
            float(row.get("overage_per_gb_usd", 0) or 0),
            int(row.get("contract_length_months", 0) or 0),
        )
        for _, row in plans_df.iterrows()
    ]

    cur.executemany(
        """
        INSERT INTO plans (
            plan_id, plan_name, plan_type, monthly_price_usd,
            data_gb, talk_minutes, text_messages,
            hotspot_data_gb, international_minutes, roaming_data_gb,
            overage_per_gb_usd, contract_length_months
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """,
        rows,
    )
    conn.commit()


def insert_customers(conn, plans_df, customers_df):
    cur = conn.cursor()

    # Map plan_name -> plan_id from the plans sheet
    plan
