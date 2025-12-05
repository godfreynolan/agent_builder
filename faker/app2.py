import sqlite3
from pathlib import Path
from typing import Any, Dict, List

from mcp.server.fastmcp import FastMCP

# Path to your SQLite DB (adjust if needed)
DB_PATH = Path(__file__).parent / "r_mobile.db"

# Create MCP server
mcp = FastMCP("R-Mobile SQLite", json_response=True)


def get_connection() -> sqlite3.Connection:
    """Open a new SQLite connection (short-lived, per call)."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # rows as dict-like objects
    return conn


@mcp.tool()
def run_query(sql: str, limit: int = 50) -> List[Dict[str, Any]]:
    """
    Run a read-only SELECT query against the r_mobile SQLite database.

    Args:
        sql: A SELECT query, e.g. "SELECT * FROM customers LIMIT 10"
        limit: Max number of rows to return.

    Returns:
        List of rows as dicts.
    """
    sql_stripped = sql.strip().upper()
    if not sql_stripped.startswith("SELECT"):
        raise ValueError("Only SELECT queries are allowed for safety.")

    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchmany(limit)

    return [dict(row) for row in rows]


@mcp.tool()
def get_customer_calls(customer_id: int, limit: int = 50) -> List[Dict[str, Any]]:
    """
    Get recent call records for a given customer.

    Args:
        customer_id: ID from the customers table.
        limit: Max number of call records to return.

    Returns:
        Rows from call_records joined with customer info.
    """
    sql = """
        SELECT
            cr.call_id,
            cr.customer_id,
            c.full_name,
            c.phone_number AS customer_phone,
            cr.other_party_phone,
            cr.call_type,
            cr.start_time,
            cr.duration_seconds,
            cr.is_missed,
            cr.is_roaming,
            cr.cell_tower_city,
            cr.cell_tower_country,
            cr.cost_usd
        FROM call_records cr
        JOIN customers c ON c.customer_id = cr.customer_id
        WHERE cr.customer_id = ?
        ORDER BY cr.start_time DESC
        LIMIT ?
    """

    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(sql, (customer_id, limit))
        rows = cur.fetchall()

    return [dict(row) for row in rows]


@mcp.tool()
def get_plan_summary() -> List[Dict[str, Any]]:
    """
    Summarize number of customers and avg data usage per plan.
    """
    sql = """
        SELECT
            p.plan_id,
            p.plan_name,
            p.plan_type,
            p.monthly_price_usd,
            COUNT(c.customer_id) AS customer_count,
            AVG(c.data_used_gb) AS avg_data_used_gb
        FROM plans p
        LEFT JOIN customers c ON c.plan_id = p.plan_id
        GROUP BY p.plan_id, p.plan_name, p.plan_type, p.monthly_price_usd
        ORDER BY p.monthly_price_usd;
    """

    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()

    return [dict(row) for row in rows]


if __name__ == "__main__":
    # Run the MCP server over HTTP (Streamable HTTP transport)
    # Default: listens on http://localhost:8000/mcp
    mcp.run(transport="streamable-http")
