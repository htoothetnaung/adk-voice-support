"""Customer lookup tools."""

from __future__ import annotations

from app.data.mock_customers import CUSTOMERS


def lookup_customer(customer_id: str | None = None, email: str | None = None) -> dict:
    """Look up a mock customer by customer ID or email."""

    if not customer_id and not email:
        return {"found": False, "error": "customer_id or email is required"}

    if customer_id:
        customer = CUSTOMERS.get(customer_id)
        if customer:
            return {"found": True, "customer": dict(customer)}

    if email:
        normalized_email = email.strip().lower()
        for customer in CUSTOMERS.values():
            if customer["email"].lower() == normalized_email:
                return {"found": True, "customer": dict(customer)}

    return {"found": False, "error": "customer not found"}

