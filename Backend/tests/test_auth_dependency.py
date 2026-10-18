from app.core.database import SessionLocal
from app.core.security import create_access_token, decode_access_token
from app.models.user import User


print("Testing authentication dependency...")

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

    print("USER FOUND")
    print(f"User ID: {user.id}")
    print(f"Email: {user.email}")
    print(f"Company ID: {user.company_id}")
    print(f"Role: {user.role.value}")
    print(f"Status: {user.account_status.value}")

    token = create_access_token(
        {
            "sub": str(user.id),
            "company_id": user.company_id,
            "role": user.role.value,
        }
    )

    print("\nTOKEN CREATION: SUCCESS")

    payload = decode_access_token(token)

    if not payload:
        print("TOKEN DECODING: FAILED")
        raise SystemExit

    print("TOKEN DECODING: SUCCESS")
    print(f"Payload: {payload}")

    decoded_user_id = int(payload["sub"])

    authenticated_user = (
        db.query(User)
        .filter(User.id == decoded_user_id)
        .first()
    )

    if not authenticated_user:
        print("CURRENT USER LOOKUP: FAILED")
        raise SystemExit

    print("CURRENT USER LOOKUP: SUCCESS")
    print(f"Authenticated user: {authenticated_user}")

    if not authenticated_user.is_active:
        print("ACCOUNT STATUS: FAILED")
        raise SystemExit

    print("ACCOUNT STATUS: ACTIVE")
    print("\nAUTHENTICATION DEPENDENCY TEST: SUCCESS")

finally:
    db.close()
    print("\nDatabase session closed.")