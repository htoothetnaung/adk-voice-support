"""Mock technical issue knowledge base."""

KNOWN_ISSUES = {
    "login": {
        "product_area": "login",
        "title": "OTP delivery delays",
        "status": "investigating",
        "workaround": "Ask the customer to retry after two minutes and confirm email delivery.",
    },
    "mobile_app": {
        "product_area": "mobile_app",
        "title": "Android crash on startup",
        "status": "mitigated",
        "workaround": "Update to the latest app version and clear cached storage.",
    },
    "integration": {
        "product_area": "integration",
        "title": "Webhook retry queue delays",
        "status": "monitoring",
        "workaround": "Verify endpoint health and retry failed webhook events.",
    },
}

