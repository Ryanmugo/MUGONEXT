from app.core.database import SessionLocal
from app.models.user import User
from app.constants import UserRole
from app.api.dependencies.auth import (
    require_owner,
    require_admin,
    require_manager,
    require_analyst,
)


print("Testing RBAC...")

db = SessionLocal()

try:
    user = (
        db.query(User)
        .filter(User.email == "authadmin@mugonext.com")
        .first()
    )

    if not user:
        print("USER NOT FOUND")
        raise SystemExit

    print(f"User: {user.email}")
    print(f"Role: {user.role.value}")

    # Admin test
    admin_user = require_admin(current_user=user)
    print("ADMIN ACCESS: SUCCESS")

    # Manager test
    manager_user = require_manager(current_user=user)
    print("MANAGER ACCESS: SUCCESS")

    # Analyst test
    analyst_user = require_analyst(current_user=user)
    print("ANALYST ACCESS: SUCCESS")

    # Owner should fail because this user is an admin
    try:
        require_owner(current_user=user)
        print("OWNER ACCESS: UNEXPECTED SUCCESS")
    except Exception as exc:
        print("OWNER ACCESS: CORRECTLY DENIED")
        print(f"Reason: {exc.detail}")

    print("\nRBAC TEST: SUCCESS")

finally:
    db.close()
    print("\nDatabase session closed.")