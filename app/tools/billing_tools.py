"""Billing and invoice tools."""

from __future__ import annotations

from app.data.mock_invoices import INVOICES


def lookup_invoice(invoice_id: str | None = None, customer_id: str | None = None) -> dict:
    """Look up mock invoice data."""

    if not invoice_id and not customer_id:
        return {"found": False, "error": "invoice_id or customer_id is required"}

    if invoice_id:
        invoice = INVOICES.get(invoice_id)
        if invoice:
            return {"found": True, "invoice": dict(invoice)}

    if customer_id:
        invoices = [dict(invoice) for invoice in INVOICES.values() if invoice["customer_id"] == customer_id]
        if invoices:
            return {"found": True, "invoices": invoices}

    return {"found": False, "error": "invoice not found"}


def check_refund_eligibility(invoice_id: str) -> dict:
    """Check if a mock invoice is eligible for refund."""

    invoice = INVOICES.get(invoice_id)
    if not invoice:
        return {"eligible": False, "invoice_id": invoice_id, "reason": "invoice not found"}

    if invoice["status"] != "paid":
        return {"eligible": False, "invoice_id": invoice_id, "reason": "invoice is not paid"}

    if invoice["duplicate_charge"]:
        return {"eligible": True, "invoice_id": invoice_id, "reason": "duplicate charge detected"}

    if invoice["days_since_payment"] <= 14:
        return {"eligible": True, "invoice_id": invoice_id, "reason": "within 14-day refund window"}

    return {"eligible": False, "invoice_id": invoice_id, "reason": "outside 14-day refund window"}


def create_refund_ticket(customer_id: str, invoice_id: str, reason: str) -> dict:
    """Create a mock refund support ticket."""

    return {
        "created": True,
        "ticket_id": f"refund_{customer_id}_{invoice_id}",
        "ticket_type": "refund",
        "customer_id": customer_id,
        "invoice_id": invoice_id,
        "reason": reason,
        "status": "open",
    }

