from fastapi.testclient import TestClient

from app.main import app
from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import create_access_token


client = TestClient(app)


def get_test_user():
    db = SessionLocal()

    try:
        user = (
            db.query(User)
            .filter(User.email == "authadmin@mugonext.com")
            .first()
        )

        if not user:
            raise RuntimeError("Test user not found.")

        return {
            "id": user.id,
            "company_id": user.company_id,
            "email": user.email,
            "role": user.role.value,
        }

    finally:
        db.close()


def create_token(user):
    return create_access_token(
        data={
            "sub": str(user["id"]),
            "company_id": user["company_id"],
            "role": user["role"],
        }
    )


print("=" * 60)
print("MUGONEXT UPLOAD API TEST")
print("=" * 60)


user = get_test_user()

print(f"User: {user['email']}")
print(f"User ID: {user['id']}")
print(f"Company ID: {user['company_id']}")
print(f"Role: {user['role']}")

token = create_token(user)

headers = {
    "Authorization": f"Bearer {token}"
}


upload_payload = {
    "original_filename": "sales_data.csv",
    "stored_filename": "company7_sales_test_v2.csv",
    "file_extension": "csv",
    "mime_type": "text/csv",
    "file_size": 1024,
    "storage_path": "uploads/company7/sales_data_v2.csv",
    "dataset_name": "Sales Test Dataset",
    "description": "MUGONEXT upload integration test",
    "rows": 100,
    "columns": 5,
    "column_metadata": {
        "date": "datetime",
        "sales": "float",
        "product": "string",
        "quantity": "integer",
        "region": "string",
    },
    "target_column": "sales",
    "date_column": "date",
    "encoding": "utf-8",
    "storage_provider": "local",
    "upload_source": "web",
}

response = client.post(
    "/uploads/",
    json=upload_payload,
    headers=headers,
)

print("\nCREATE UPLOAD")
print("Status:", response.status_code)
print("Response:", response.json())

assert response.status_code == 201, response.text

created_upload = response.json()

upload_id = created_upload["id"]

assert created_upload["company_id"] == user["company_id"]
assert created_upload["user_id"] == user["id"]

print("CREATE UPLOAD: SUCCESS")


response = client.get(
    "/uploads/",
    headers=headers,
)

print("\nLIST UPLOADS")
print("Status:", response.status_code)

assert response.status_code == 200, response.text

uploads = response.json()

print("Uploads returned:", len(uploads))

assert any(
    upload["id"] == upload_id
    for upload in uploads
)

assert all(
    upload["company_id"] == user["company_id"]
    for upload in uploads
)

print("LIST UPLOADS: SUCCESS")
print("COMPANY DATA FILTERING: SUCCESS")


response = client.get(
    f"/uploads/{upload_id}",
    headers=headers,
)

print("\nGET SINGLE UPLOAD")
print("Status:", response.status_code)

assert response.status_code == 200, response.text

single_upload = response.json()

assert single_upload["id"] == upload_id
assert single_upload["company_id"] == user["company_id"]

print("GET UPLOAD: SUCCESS")


response = client.put(
    f"/uploads/{upload_id}",
    json={
        "dataset_name": "Updated Sales Dataset",
        "description": "Updated by integration test",
        "target_column": "sales",
    },
    headers=headers,
)

print("\nUPDATE UPLOAD")
print("Status:", response.status_code)

assert response.status_code == 200, response.text

updated_upload = response.json()

assert updated_upload["dataset_name"] == "Updated Sales Dataset"

print("UPDATE UPLOAD: SUCCESS")


response = client.delete(
    f"/uploads/{upload_id}",
    headers=headers,
)

print("\nARCHIVE UPLOAD")
print("Status:", response.status_code)

assert response.status_code == 204, response.text

print("ARCHIVE UPLOAD: SUCCESS")


response = client.get(
    f"/uploads/{upload_id}",
    headers=headers,
)

print("\nGET ARCHIVED UPLOAD")
print("Status:", response.status_code)

assert response.status_code == 404

print("ARCHIVED UPLOAD HIDDEN: SUCCESS")


print("\n" + "=" * 60)
print("UPLOAD API TEST: SUCCESS")
print("=" * 60)
