SYSTEM_PERMISSIONS: list[tuple[str, str, str]] = [
    ("dashboard", "read", "View dashboard"),
    ("clients", "read", "View clients"),
    ("clients", "write", "Manage clients"),
    ("inventory", "read", "View inventory"),
    ("inventory", "write", "Manage inventory"),
    ("ppe", "read", "View PPE records"),
    ("ppe", "write", "Manage PPE issuance"),
    ("finance", "read", "View finance"),
    ("finance", "write", "Manage finance"),
    ("quotes", "read", "View quotes"),
    ("quotes", "write", "Manage quotes"),
    ("invoices", "read", "View invoices"),
    ("invoices", "write", "Manage invoices"),
    ("users", "read", "View users"),
    ("users", "write", "Manage users"),
    ("audit", "read", "View audit logs"),
    ("business_cases", "read", "View business cases"),
    ("business_cases", "approve", "Approve business cases"),
    ("trip_requests", "read", "View trip requests"),
    ("trip_requests", "approve", "Approve trip requests"),
    ("employees", "read", "View employees"),
    ("employees", "write", "Manage employees"),
]

SYSTEM_ROLES: dict[str, list[str]] = {
    "super_admin": ["*"],
    "director": [
        "dashboard:read", "clients:read", "clients:write", "inventory:read", "inventory:write",
        "ppe:read", "ppe:write", "finance:read", "finance:write", "quotes:read", "quotes:write",
        "invoices:read", "invoices:write", "users:read", "audit:read",
        "business_cases:read", "business_cases:approve", "trip_requests:read", "trip_requests:approve",
        "employees:read", "employees:write",
    ],
    "finance": [
        "dashboard:read", "clients:read", "inventory:read", "finance:read", "finance:write",
        "quotes:read", "invoices:read", "invoices:write", "business_cases:read",
    ],
    "sales": [
        "dashboard:read", "clients:read", "clients:write", "quotes:read", "quotes:write",
        "invoices:read", "invoices:write",
    ],
    "store": [
        "dashboard:read", "inventory:read", "inventory:write", "ppe:read", "ppe:write",
        "business_cases:read",
    ],
    "technician": [
        "dashboard:read", "clients:read", "inventory:read", "ppe:read", "employees:read",
    ],
    "support": [
        "dashboard:read", "clients:read", "clients:write", "ppe:read",
    ],
    "reception": [
        "dashboard:read", "clients:read", "employees:read",
    ],
    "manager": [
        "dashboard:read", "clients:read", "clients:write", "inventory:read",
        "business_cases:read", "business_cases:approve", "trip_requests:read", "trip_requests:approve",
        "employees:read", "ppe:read",
    ],
}


def permission_key(module: str, action: str) -> str:
    return f"{module}:{action}"
