from app.core.database import SessionLocal
from app.models.company import Company
from app.models.user import User
from app.constants import UserRole, AccountStatus


db = SessionLocal()

try:
    print("Testing User CRUD...")

    # =====================================================
    # Find existing company
    # =====================================================

    company = (
        db.query(Company)
        .order_by(Company.id.desc())
        .first()
    )

    if not company:
        print("No company found in database.")
        raise SystemExit

    print(f"Company found: {company.name}")
    print(f"Company ID: {company.id}")

    # =====================================================
    # CREATE USER
    # =====================================================

    user = User(
        company_id=company.id,

        first_name="MUGONEXT",
        last_name="Admin",
        display_name="MUGONEXT Admin",

        email="admin@mugonext.com",
        phone="+254700000000",

        password_hash="TEMP_HASH_FOR_TESTING",

        role=UserRole.ADMIN,
        account_status=AccountStatus.ACTIVE,

        language="en",
        timezone="Africa/Nairobi",

        profile_completed=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    print("\nCREATE: SUCCESS")
    print(f"Created user ID: {user.id}")
    print(f"Name: {user.full_name}")
    print(f"Email: {user.email}")
    print(f"Company ID: {user.company_id}")
    print(f"Role: {user.role.value}")
    print(f"Status: {user.account_status.value}")

    # =====================================================
    # READ USER
    # =====================================================

    found_user = (
        db.query(User)
        .filter(User.id == user.id)
        .first()
    )

    if not found_user:
        raise Exception("User was not found.")

    print("\nREAD: SUCCESS")
    print(f"Found: {found_user}")
    print(f"Company: {found_user.company.name}")

    # =====================================================
    # UPDATE USER
    # =====================================================

    found_user.display_name = "MUGONEXT Super Admin"
    found_user.phone = "+254711111111"

    db.commit()
    db.refresh(found_user)

    print("\nUPDATE: SUCCESS")
    print(f"Updated name: {found_user.full_name}")
    print(f"Updated phone: {found_user.phone}")

    # =====================================================
    # DELETE USER
    # =====================================================

    user_id = found_user.id

    db.delete(found_user)
    db.commit()

    print("\nDELETE: SUCCESS")

    # =====================================================
    # DELETE VERIFICATION
    # =====================================================

    deleted_user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if deleted_user is None:
        print("DELETE VERIFICATION: SUCCESS")
    else:
        print("DELETE VERIFICATION: FAILED")

finally:
    db.close()
    print("\nDatabase session closed.")