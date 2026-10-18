import math

from fastapi.testclient import TestClient

from app.main import app
from app.core.database import SessionLocal
from app.core.security import create_access_token
from app.models.user import User


# =========================================================
# TEST CLIENT
# =========================================================

client = TestClient(app)


# =========================================================
# GET TEST USER
# =========================================================

def get_test_user():
    db = SessionLocal()

    try:
        user = (
            db.query(User)
            .filter(
                User.email == "authadmin@mugonext.com"
            )
            .first()
        )

        if not user:
            raise RuntimeError(
                "Test user not found."
            )

        return {
            "id": user.id,
            "company_id": user.company_id,
            "email": user.email,
            "role": user.role.value,
        }

    finally:
        db.close()


# =========================================================
# CREATE AUTH TOKEN
# =========================================================

def create_token(user):
    return create_access_token(
        data={
            "sub": str(user["id"]),
            "company_id": user["company_id"],
            "role": user["role"],
        }
    )


# =========================================================
# START TEST
# =========================================================

print("=" * 60)
print("MUGONEXT RECOMMENDATION API TEST")
print("=" * 60)


# =========================================================
# GET USER
# =========================================================

user = get_test_user()

print(
    f"User: {user['email']}"
)

print(
    f"User ID: {user['id']}"
)

print(
    f"Company ID: {user['company_id']}"
)

print(
    f"Role: {user['role']}"
)


# =========================================================
# AUTHENTICATION
# =========================================================

token = create_token(user)

headers = {
    "Authorization": f"Bearer {token}"
}


# =========================================================
# CREATE RECOMMENDATION
# =========================================================

recommendation_payload = {
    "title": "Increase Product A Inventory",
    "category": "inventory",

    "description": (
        "Inventory levels for Product A "
        "are expected to decline."
    ),

    "recommendation": (
        "Increase Product A inventory "
        "before the next demand period."
    ),

    "reasoning": (
        "Historical sales show an increasing "
        "demand trend."
    ),

    "expected_outcome": (
        "Reduce stockout risk and maintain "
        "customer availability."
    ),

    "suggested_action": (
        "Increase the next procurement order "
        "for Product A by approximately 15%."
    ),

    "priority": "high",

    "priority_score": 85.0,

    "impact_score": 90.0,

    "confidence_score": 92.0,

    "estimated_cost": 50000.0,

    "estimated_savings": 120000.0,

    "estimated_revenue_impact": 200000.0,

    "roi_percentage": 140.0,

    "ai_provider": "openai",

    "model_version": "MUGONEXT-1.0",

    "parameters": {
        "forecast_horizon": 30,
        "confidence_threshold": 0.80,
    },

    "source_data": {
        "dataset": "sales_history",
        "observations": 60,
    },

    "ai_explanation": (
        "The recommendation is based on "
        "historical demand trends and forecast "
        "confidence."
    ),
}


response = client.post(
    "/recommendations",
    json=recommendation_payload,
    headers=headers,
)


print()
print("CREATE RECOMMENDATION")
print("Status:", response.status_code)
print("Response:", response.json())


assert response.status_code == 201, response.text

created_recommendation = response.json()

recommendation_id = created_recommendation["id"]


# =========================================================
# VERIFY OWNERSHIP
# =========================================================

assert (
    created_recommendation["company_id"]
    == user["company_id"]
)

assert (
    created_recommendation["user_id"]
    == user["id"]
)


print(
    "COMPANY OWNERSHIP: SUCCESS"
)

print(
    "USER OWNERSHIP: SUCCESS"
)


# =========================================================
# VERIFY PROCESSING STATE
# =========================================================

assert (
    created_recommendation["status"]
    == "completed"
)

assert (
    created_recommendation["progress"]
    == 100
)

assert (
    created_recommendation["is_active"]
    is True
)

assert (
    created_recommendation["is_archived"]
    is False
)


print(
    "RECOMMENDATION PROCESSING STATE: SUCCESS"
)


# =========================================================
# VERIFY CONTENT
# =========================================================

assert (
    created_recommendation["title"]
    == "Increase Product A Inventory"
)

assert (
    created_recommendation["category"]
    == "inventory"
)

assert (
    created_recommendation["priority"]
    == "high"
)

assert (
    created_recommendation["priority_score"]
    == 85.0
)

assert (
    created_recommendation["impact_score"]
    == 90.0
)

assert (
    created_recommendation["confidence_score"]
    == 92.0
)


print(
    "RECOMMENDATION CONTENT: SUCCESS"
)


# =========================================================
# LIST RECOMMENDATIONS
# =========================================================

response = client.get(
    "/recommendations",
    headers=headers,
)


print()
print("LIST RECOMMENDATIONS")
print("Status:", response.status_code)


assert response.status_code == 200, response.text

recommendation_list = response.json()

print(
    "Total recommendations:",
    recommendation_list["total"],
)

assert (
    recommendation_list["page"]
    == 1
)

assert (
    recommendation_list["page_size"]
    == 20
)

assert (
    recommendation_list["pages"]
    == math.ceil(
        recommendation_list["total"] / 20
    )
)

assert any(
    item["id"] == recommendation_id
    for item in recommendation_list["items"]
)


print(
    "LIST RECOMMENDATIONS: SUCCESS"
)


# =========================================================
# COMPANY DATA FILTERING
# =========================================================

for item in recommendation_list["items"]:

    assert (
        item["company_id"]
        == user["company_id"]
    )


print(
    "COMPANY DATA FILTERING: SUCCESS"
)


# =========================================================
# FILTER BY PRIORITY
# =========================================================

response = client.get(
    "/recommendations",
    params={
        "priority": "high",
    },
    headers=headers,
)


print()
print("FILTER BY PRIORITY")
print("Status:", response.status_code)


assert response.status_code == 200, response.text

priority_results = response.json()

assert all(
    item["priority"] == "high"
    for item in priority_results["items"]
)


print(
    "PRIORITY FILTER: SUCCESS"
)


# =========================================================
# FILTER BY CATEGORY
# =========================================================

response = client.get(
    "/recommendations",
    params={
        "category": "inventory",
    },
    headers=headers,
)


print()
print("FILTER BY CATEGORY")
print("Status:", response.status_code)


assert response.status_code == 200, response.text

category_results = response.json()

assert all(
    item["category"] == "inventory"
    for item in category_results["items"]
)


print(
    "CATEGORY FILTER: SUCCESS"
)


# =========================================================
# FILTER BY STATUS
# =========================================================

response = client.get(
    "/recommendations",
    params={
        "status": "completed",
    },
    headers=headers,
)


print()
print("FILTER BY STATUS")
print("Status:", response.status_code)


assert response.status_code == 200, response.text

status_results = response.json()

assert all(
    item["status"] == "completed"
    for item in status_results["items"]
)


print(
    "STATUS FILTER: SUCCESS"
)


# =========================================================
# GET SINGLE RECOMMENDATION
# =========================================================

response = client.get(
    f"/recommendations/{recommendation_id}",
    headers=headers,
)


print()
print("GET SINGLE RECOMMENDATION")
print("Status:", response.status_code)


assert response.status_code == 200, response.text

single_recommendation = response.json()

assert (
    single_recommendation["id"]
    == recommendation_id
)

assert (
    single_recommendation["company_id"]
    == user["company_id"]
)


print(
    "GET RECOMMENDATION: SUCCESS"
)


# =========================================================
# UPDATE RECOMMENDATION
# =========================================================

update_payload = {
    "title": "Updated Product A Inventory Recommendation",

    "description": (
        "Updated recommendation description."
    ),

    "priority": "critical",

    "priority_score": 95.0,
}


response = client.patch(
    f"/recommendations/{recommendation_id}",
    json=update_payload,
    headers=headers,
)


print()
print("UPDATE RECOMMENDATION")
print("Status:", response.status_code)


assert response.status_code == 200, response.text

updated_recommendation = response.json()

assert (
    updated_recommendation["title"]
    == "Updated Product A Inventory Recommendation"
)

assert (
    updated_recommendation["priority"]
    == "critical"
)

assert (
    updated_recommendation["priority_score"]
    == 95.0
)


print(
    "UPDATE RECOMMENDATION: SUCCESS"
)


# =========================================================
# MARK ACTIONED
# =========================================================

action_payload = {
    "action_taken": True,

    "action_notes": (
        "Procurement team approved the "
        "recommended inventory increase."
    ),
}


response = client.post(
    f"/recommendations/{recommendation_id}/action",
    json=action_payload,
    headers=headers,
)


print()
print("MARK RECOMMENDATION ACTIONED")
print("Status:", response.status_code)


assert response.status_code == 200, response.text

actioned_recommendation = response.json()

assert (
    actioned_recommendation["action_taken"]
    is True
)

assert (
    actioned_recommendation["action_notes"]
    == action_payload["action_notes"]
)

assert (
    actioned_recommendation["action_taken_at"]
    is not None
)


print(
    "MARK ACTIONED: SUCCESS"
)


# =========================================================
# ARCHIVE
# =========================================================

response = client.post(
    f"/recommendations/{recommendation_id}/archive",
    headers=headers,
)


print()
print("ARCHIVE RECOMMENDATION")
print("Status:", response.status_code)


assert response.status_code == 200, response.text

archived_recommendation = response.json()

assert (
    archived_recommendation["is_archived"]
    is True
)

assert (
    archived_recommendation["is_active"]
    is False
)


print(
    "ARCHIVE RECOMMENDATION: SUCCESS"
)


# =========================================================
# VERIFY ARCHIVED RECOMMENDATION HIDDEN
# =========================================================

response = client.get(
    f"/recommendations/{recommendation_id}",
    headers=headers,
)


print()
print("GET ARCHIVED RECOMMENDATION")
print("Status:", response.status_code)


assert response.status_code == 404, response.text


print(
    "ARCHIVED RECOMMENDATION HIDDEN: SUCCESS"
)


# =========================================================
# RESTORE
# =========================================================

response = client.post(
    f"/recommendations/{recommendation_id}/restore",
    headers=headers,
)


print()
print("RESTORE RECOMMENDATION")
print("Status:", response.status_code)


assert response.status_code == 200, response.text

restored_recommendation = response.json()

assert (
    restored_recommendation["is_archived"]
    is False
)

assert (
    restored_recommendation["is_active"]
    is True
)


print(
    "RESTORE RECOMMENDATION: SUCCESS"
)


# =========================================================
# VERIFY RESTORED RECOMMENDATION
# =========================================================

response = client.get(
    f"/recommendations/{recommendation_id}",
    headers=headers,
)


print()
print("GET RESTORED RECOMMENDATION")
print("Status:", response.status_code)


assert response.status_code == 200, response.text


print(
    "RESTORED RECOMMENDATION ACCESS: SUCCESS"
)


# =========================================================
# SOFT DELETE
# =========================================================

response = client.delete(
    f"/recommendations/{recommendation_id}",
    headers=headers,
)


print()
print("DELETE RECOMMENDATION")
print("Status:", response.status_code)


assert response.status_code == 204, response.text


print(
    "SOFT DELETE: SUCCESS"
)


# =========================================================
# VERIFY DELETED RECOMMENDATION HIDDEN
# =========================================================

response = client.get(
    f"/recommendations/{recommendation_id}",
    headers=headers,
)


print()
print("GET DELETED RECOMMENDATION")
print("Status:", response.status_code)


assert response.status_code == 404, response.text


print(
    "DELETED RECOMMENDATION HIDDEN: SUCCESS"
)


# =========================================================
# FINAL RESULT
# =========================================================

print()
print("=" * 60)
print("RECOMMENDATION API TEST: SUCCESS")
print("=" * 60)