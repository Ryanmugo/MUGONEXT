from app.core.security import (
    create_access_token,
    decode_access_token,
)


print("Testing JWT...")

payload = {
    "sub": "1",
    "company_id": 7,
    "role": "admin",
}

token = create_access_token(payload)

print("CREATE TOKEN: SUCCESS")
print(f"Token: {token}")

decoded = decode_access_token(token)

assert decoded is not None
assert decoded["sub"] == "1"
assert decoded["company_id"] == 7
assert decoded["role"] == "admin"

print("DECODE TOKEN: SUCCESS")
print(f"Decoded: {decoded}")

print("JWT TEST: SUCCESS")