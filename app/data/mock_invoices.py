"""Mock invoice records."""

INVOICES = {
    "inv_1001": {
        "invoice_id": "inv_1001",
        "customer_id": "cust_001",
        "amount": 49.99,
        "status": "paid",
        "duplicate_charge": True,
        "days_since_payment": 3,
    },
    "inv_1002": {
        "invoice_id": "inv_1002",
        "customer_id": "cust_002",
        "amount": 19.99,
        "status": "paid",
        "duplicate_charge": False,
        "days_since_payment": 30,
    },
    "inv_1003": {
        "invoice_id": "inv_1003",
        "customer_id": "cust_003",
        "amount": 99.99,
        "status": "failed",
        "duplicate_charge": False,
        "days_since_payment": 0,
    },
}

