from __future__ import annotations

import io

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)

EMAIL = "authadmin@mugonext.com"
PASSWORD = "MugoPostgres2026"


def login() -> str:
    response = client.post(
        "/auth/login",
        json={
            "email": EMAIL,
            "password": PASSWORD,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"

    return data["access_token"]


# =========================================================
# AUTHENTICATION
# =========================================================


def test_missing_authentication():
    """
    Protected endpoints must reject requests without
    an Authorization header.
    """

    response = client.get(
        "/companies/"
    )

    assert response.status_code == 401

    assert response.json()["detail"] == (
        "Not authenticated"
    )

    print(
        "MISSING AUTHENTICATION: PASS"
    )


# =========================================================
# UPLOAD VALIDATION
# =========================================================


def test_invalid_upload_extension():
    """
    Unsupported file types must be rejected.
    """

    token = login()

    response = client.post(
        "/uploads/file",
        headers={
            "Authorization": (
                f"Bearer {token}"
            )
        },
        files={
            "file": (
                "invalid.txt",
                io.BytesIO(
                    b"this is not a supported dataset"
                ),
                "text/plain",
            )
        },
        data={
            "dataset_name": (
                "Invalid Extension Test"
            ),
            "target_column": "sales",
            "date_column": "date",
        },
    )

    assert response.status_code == 400

    detail = response.json()["detail"]

    assert (
        "Unsupported dataset format"
        in detail
    )

    print(
        "INVALID FILE EXTENSION: PASS"
    )


def test_missing_target_column():
    """
    Uploads whose requested target column does not
    exist must be rejected.
    """

    token = login()

    csv_data = """date,sales
2026-01-01,100
2026-01-02,110
2026-01-03,120
2026-01-04,130
2026-01-05,140
"""

    response = client.post(
        "/uploads/file",
        headers={
            "Authorization": (
                f"Bearer {token}"
            )
        },
        files={
            "file": (
                "missing_target.csv",
                io.BytesIO(
                    csv_data.encode("utf-8")
                ),
                "text/csv",
            )
        },
        data={
            "dataset_name": (
                "Missing Target Test"
            ),
            "target_column": "revenue",
            "date_column": "date",
        },
    )

    assert response.status_code == 400

    print(
        "MISSING TARGET COLUMN: PASS"
    )


def test_missing_date_column():
    """
    Uploads whose requested date column does not
    exist must be rejected.
    """

    token = login()

    csv_data = """date,sales
2026-01-01,100
2026-01-02,110
2026-01-03,120
2026-01-04,130
2026-01-05,140
"""

    response = client.post(
        "/uploads/file",
        headers={
            "Authorization": (
                f"Bearer {token}"
            )
        },
        files={
            "file": (
                "missing_date.csv",
                io.BytesIO(
                    csv_data.encode("utf-8")
                ),
                "text/csv",
            )
        },
        data={
            "dataset_name": (
                "Missing Date Test"
            ),
            "target_column": "sales",
            "date_column": (
                "transaction_date"
            ),
        },
    )

    assert response.status_code == 400

    print(
        "MISSING DATE COLUMN: PASS"
    )


# =========================================================
# FORECASTING VALIDATION
# =========================================================


def test_insufficient_forecast_history():
    """
    Forecast generation must reject datasets that do
    not contain enough historical observations.
    """

    token = login()

    csv_data = """date,sales
2026-01-01,100
2026-01-02,110
2026-01-03,120
2026-01-04,130
2026-01-05,140
2026-01-06,150
2026-01-07,160
2026-01-08,170
2026-01-09,180
2026-01-10,190
"""

    upload_response = client.post(
        "/uploads/file",
        headers={
            "Authorization": (
                f"Bearer {token}"
            )
        },
        files={
            "file": (
                "insufficient_history.csv",
                io.BytesIO(
                    csv_data.encode("utf-8")
                ),
                "text/csv",
            )
        },
        data={
            "dataset_name": (
                "Insufficient History Test"
            ),
            "target_column": "sales",
            "date_column": "date",
        },
    )

    assert (
        upload_response.status_code
        == 201
    )

    upload_id = (
        upload_response
        .json()["id"]
    )

    forecast_response = client.post(
        "/forecasts/",
        headers={
            "Authorization": (
                f"Bearer {token}"
            )
        },
        json={
            "name": (
                "Insufficient History Forecast"
            ),
            "upload_id": upload_id,
            "description": (
                "Hardening test"
            ),
            "forecast_model": "auto",
            "target_column": "sales",
            "date_column": "date",
            "forecast_periods": 5,
            "frequency": "daily",
        },
    )

    assert (
        forecast_response.status_code
        == 400
    )

    detail = forecast_response.json()[
        "detail"
    ]

    assert (
        "historical observations"
        in detail.lower()
    )

    print(
        "INSUFFICIENT FORECAST HISTORY: PASS"
    )


# =========================================================
# RECOMMENDATION VALIDATION
# =========================================================


def test_nonexistent_forecast():
    """
    Recommendation generation must reject a forecast
    that does not exist for the authenticated company.
    """

    token = login()

    response = client.post(
        "/recommendations/generate",
        headers={
            "Authorization": (
                f"Bearer {token}"
            )
        },
        json={
            "forecast_id": 999999999
        },
    )

    assert response.status_code == 404

    print(
        "NONEXISTENT FORECAST: PASS"
    )


# =========================================================
# RETRIEVAL
# =========================================================


def test_existing_forecast_retrieval():
    """
    Existing forecast #22 should be retrievable by
    the authenticated company.
    """

    token = login()

    response = client.get(
        "/forecasts/22",
        headers={
            "Authorization": (
                f"Bearer {token}"
            )
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == 22

    assert (
        data["status"]
        == "completed"
    )

    print(
        "EXISTING FORECAST RETRIEVAL: PASS"
    )


def test_existing_recommendation_retrieval():
    """
    Existing recommendation #6 should be retrievable
    by the authenticated company.
    """

    token = login()

    response = client.get(
        "/recommendations/6",
        headers={
            "Authorization": (
                f"Bearer {token}"
            )
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == 6

    assert (
        data["status"]
        == "completed"
    )

    print(
        "EXISTING RECOMMENDATION RETRIEVAL: PASS"
    )


# =========================================================
# MAIN
# =========================================================


if __name__ == "__main__":

    print()
    print(
        "MUGONEXT BACKEND HARDENING TESTS"
    )
    print(
        "=" * 45
    )

    test_missing_authentication()

    test_invalid_upload_extension()

    test_missing_target_column()

    test_missing_date_column()

    test_insufficient_forecast_history()

    test_nonexistent_forecast()

    test_existing_forecast_retrieval()

    test_existing_recommendation_retrieval()

    print(
        "=" * 45
    )

    print(
        "ALL HARDENING TESTS PASSED"
    )