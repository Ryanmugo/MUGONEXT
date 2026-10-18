from app.core.security import (
    hash_password,
    verify_password,
)


password = "MUGONEXT123!"

hashed = hash_password(password)

print("Password hashing test")
print("Original:", password)
print("Hashed:", hashed)

assert hashed != password
assert verify_password(password, hashed)
assert not verify_password("WrongPassword", hashed)

print("HASH: SUCCESS")
print("VERIFY CORRECT PASSWORD: SUCCESS")
print("VERIFY WRONG PASSWORD: SUCCESS")