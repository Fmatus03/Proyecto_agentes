SENSITIVE_PERMISSIONS = {"costs:read", "financial:read", "smtp:update", "users:write"}


def require_permission(user_permissions: set[str], required: str) -> None:
    if "*" in user_permissions or required in user_permissions:
        return
    raise PermissionError("permission_denied")


def can_view_costs(user_permissions: set[str]) -> bool:
    return "*" in user_permissions or "costs:read" in user_permissions or "financial:read" in user_permissions
