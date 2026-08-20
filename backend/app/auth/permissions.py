class Permissions:
    """Central registry of permission strings used across the platform's services."""

    USERS_READ = "users:read"
    USERS_WRITE = "users:write"
    CHURN_READ = "churn:read"
    CHURN_WRITE = "churn:write"
    CLV_READ = "clv:read"
    FORECASTING_READ = "forecasting:read"
    FRAUD_READ = "fraud:read"
    REPORTS_READ = "reports:read"
    DATASETS_WRITE = "datasets:write"
    ADMIN = "admin:all"


# Seeded into the DB on first run (see app/db/init_db.py). Edit freely —
# this is your source of truth for what each role can do.
DEFAULT_ROLE_PERMISSIONS: dict[str, list[str]] = {
    "admin": [
        Permissions.USERS_READ,
        Permissions.USERS_WRITE,
        Permissions.CHURN_READ,
        Permissions.CHURN_WRITE,
        Permissions.CLV_READ,
        Permissions.FORECASTING_READ,
        Permissions.FRAUD_READ,
        Permissions.REPORTS_READ,
        Permissions.DATASETS_WRITE,
        Permissions.ADMIN,
    ],
    "analyst": [
        Permissions.CHURN_READ,
        Permissions.CLV_READ,
        Permissions.FORECASTING_READ,
        Permissions.REPORTS_READ,
    ],
    "viewer": [
        Permissions.REPORTS_READ,
    ],
}
class Permissions:
    """Central registry of permission strings used across the platform's services."""

    USERS_READ = "users:read"
    USERS_WRITE = "users:write"
    CHURN_READ = "churn:read"
    CHURN_WRITE = "churn:write"
    CLV_READ = "clv:read"
    FORECASTING_READ = "forecasting:read"
    FRAUD_READ = "fraud:read"
    REPORTS_READ = "reports:read"
    DATASETS_WRITE = "datasets:write"
    ADMIN = "admin:all"


# Seeded into the DB on first run (see app/db/init_db.py). Edit freely —
# this is your source of truth for what each role can do.
DEFAULT_ROLE_PERMISSIONS: dict[str, list[str]] = {
    "admin": [
        Permissions.USERS_READ,
        Permissions.USERS_WRITE,
        Permissions.CHURN_READ,
        Permissions.CHURN_WRITE,
        Permissions.CLV_READ,
        Permissions.FORECASTING_READ,
        Permissions.FRAUD_READ,
        Permissions.REPORTS_READ,
        Permissions.DATASETS_WRITE,
        Permissions.ADMIN,
    ],
    "analyst": [
        Permissions.CHURN_READ,
        Permissions.CLV_READ,
        Permissions.FORECASTING_READ,
        Permissions.REPORTS_READ,
    ],
    "viewer": [
        Permissions.REPORTS_READ,
    ],
}
