import uuid
from pathlib import Path

import numpy as np
import pandas as pd

from fastapi.testclient import TestClient

from app.main import app
from app.core.database import SessionLocal
from app.core.security import create_access_token

from app.models.user import User
from app.models.upload import Upload

from app.constants import (
    FileType,
    StorageProvider,
    UploadSource,
)


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
# CREATE REAL TEST DATASET + UPLOAD
# =========================================================

def create_test_upload(user):
    """
    Creates a real CSV file containing enough historical
    observations for MUGONEXT forecasting.

    Dataset:
        60 daily observations

    Columns:
        date
        sales
        product
        quantity
        region

    60 observations are intentional because the forecasting
    feature engineer uses lag_30 and rolling windows.
    """

    db = SessionLocal()

    try:

        # -----------------------------------------------------
        # STORAGE DIRECTORY
        # -----------------------------------------------------

        storage_dir = Path(
            "storage/uploads"
        )

        storage_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        # -----------------------------------------------------
        # UNIQUE FILE
        # -----------------------------------------------------

        filename = (
            f"company7_forecast_test_"
            f"{uuid.uuid4().hex}.csv"
        )

        storage_path = (
            storage_dir / filename
        )

        # -----------------------------------------------------
        # GENERATE 60 DAYS OF DATA
        # -----------------------------------------------------

        number_of_rows = 60

        dates = pd.date_range(
            start="2026-01-01",
            periods=number_of_rows,
            freq="D",
        )

        # Deterministic random generator.
        # This makes the test reproducible.
        rng = np.random.default_rng(42)

        # -----------------------------------------------------
        # TREND
        # -----------------------------------------------------

        trend = (
            np.arange(number_of_rows)
            * 1500
        )

        # -----------------------------------------------------
        # WEEKLY SEASONALITY
        # -----------------------------------------------------

        weekly_pattern = np.array(
            [
                0,
                5000,
                8000,
                3000,
                -2000,
                -5000,
                -3000,
            ],
            dtype=float,
        )

        weekly_effect = np.tile(
            weekly_pattern,
            9,
        )[:number_of_rows]

        # -----------------------------------------------------
        # RANDOM NOISE
        # -----------------------------------------------------

        noise = rng.normal(
            loc=0,
            scale=1500,
            size=number_of_rows,
        )

        # -----------------------------------------------------
        # SALES
        # -----------------------------------------------------

        sales = (
            100000
            + trend
            + weekly_effect
            + noise
        )

        sales = np.maximum(
            sales,
            1000,
        )

        # -----------------------------------------------------
        # QUANTITY
        # -----------------------------------------------------

        quantity = np.maximum(
            1,
            np.round(
                sales / 1000
            ),
        ).astype(int)

        # -----------------------------------------------------
        # PRODUCT
        # -----------------------------------------------------

        products = np.array(
            [
                "Product A",
                "Product B",
                "Product C",
            ]
        )

        product_values = np.resize(
            products,
            number_of_rows,
        )

        # -----------------------------------------------------
        # REGION
        # -----------------------------------------------------

        regions = np.array(
            [
                "Nairobi",
                "Mombasa",
                "Kisumu",
                "Nakuru",
            ]
        )

        region_values = np.resize(
            regions,
            number_of_rows,
        )

        # -----------------------------------------------------
        # BUILD DATAFRAME
        # -----------------------------------------------------

        dataframe = pd.DataFrame(
            {
                "date": dates,
                "sales": np.round(
                    sales,
                    2,
                ),
                "product": product_values,
                "quantity": quantity,
                "region": region_values,
            }
        )

        # -----------------------------------------------------
        # WRITE REAL CSV
        # -----------------------------------------------------

        dataframe.to_csv(
            storage_path,
            index=False,
        )

        # -----------------------------------------------------
        # VERIFY FILE
        # -----------------------------------------------------

        if not storage_path.exists():
            raise RuntimeError(
                "Test CSV file was not created."
            )

        verification_df = pd.read_csv(
            storage_path
        )

        if len(verification_df) != 60:
            raise RuntimeError(
                "Test CSV does not contain "
                "the expected 60 observations."
            )

        # -----------------------------------------------------
        # CREATE DATABASE UPLOAD
        # -----------------------------------------------------

        upload = Upload(
            user_id=user["id"],
            company_id=user["company_id"],

            original_filename=(
                "forecast_sales_data.csv"
            ),

            stored_filename=filename,

            file_extension=FileType.CSV,

            mime_type="text/csv",

            file_size=storage_path.stat().st_size,

            storage_path=str(
                storage_path
            ),

            storage_provider=(
                StorageProvider.LOCAL
            ),

            dataset_name=(
                "Forecast Test Dataset"
            ),

            dataset_version=1,

            description=(
                "Upload created specifically "
                "for forecast API testing."
            ),

            rows=len(dataframe),

            columns=len(
                dataframe.columns
            ),

            column_metadata={
                "date": "datetime",
                "sales": "float",
                "product": "string",
                "quantity": "integer",
                "region": "string",
            },

            target_column="sales",

            date_column="date",

            encoding="utf-8",

            delimiter=",",

            status="completed",

            upload_source=UploadSource.WEB,

            progress=100,

            validation_passed=True,

            missing_values_count=0,

            duplicate_rows_count=0,

            data_quality_score=95.0,

            data_drift_detected=False,

            preview_generated=True,

            is_processed=True,

            is_archived=False,

            embedding_generated=False,

            vector_indexed=False,

            rag_ready=False,

            recommendation_generated=False,

            forecast_generated=False,
        )

        db.add(upload)

        db.commit()

        db.refresh(upload)

        return upload.id

    finally:
        db.close()


# =========================================================
# START TEST
# =========================================================

print("=" * 60)
print("MUGONEXT FORECAST API TEST")
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

token = create_token(
    user
)

headers = {
    "Authorization": (
        f"Bearer {token}"
    )
}


# =========================================================
# CREATE TEST UPLOAD
# =========================================================

upload_id = create_test_upload(
    user
)

print(
    f"Using Test Upload ID: {upload_id}"
)


# =========================================================
# CREATE FORECAST
# =========================================================

forecast_payload = {
    "name": "Sales Forecast Test",

    "upload_id": upload_id,

    "description": (
        "MUGONEXT forecast integration test"
    ),

    "forecast_model": "auto",

    "target_column": "sales",

    "date_column": "date",

    "forecast_periods": 30,

    "frequency": "daily",
}


response = client.post(
    "/forecasts/",
    json=forecast_payload,
    headers=headers,
)


print()
print("CREATE FORECAST")
print(
    "Status:",
    response.status_code,
)
print(
    "Response:",
    response.json(),
)


assert response.status_code == 201, (
    response.text
)


created_forecast = response.json()

forecast_id = (
    created_forecast["id"]
)


assert (
    created_forecast["company_id"]
    == user["company_id"]
)

assert (
    created_forecast["user_id"]
    == user["id"]
)

assert (
    created_forecast["upload_id"]
    == upload_id
)


print(
    "CREATE FORECAST: SUCCESS"
)

print(
    "COMPANY OWNERSHIP: SUCCESS"
)


# =========================================================
# VERIFY GENERATED FORECAST DATA
# =========================================================

assert (
    created_forecast["status"]
    == "completed"
)

assert (
    created_forecast["progress"]
    == 100
)

assert (
    created_forecast["target_column"]
    == "sales"
)

assert (
    created_forecast["date_column"]
    == "date"
)

assert (
    created_forecast["forecast_periods"]
    == 30
)

assert (
    len(
        created_forecast["predictions"]
    )
    == 30
)


print(
    "PREDICTIONS: SUCCESS"
)

print(
    "Prediction count:",
    len(
        created_forecast[
            "predictions"
        ]
    ),
)


# =========================================================
# VERIFY MODEL METRICS
# =========================================================

assert (
    created_forecast["rmse"]
    is not None
)

assert (
    created_forecast["mape"]
    is not None
)

assert (
    created_forecast["accuracy_score"]
    is not None
)

assert (
    created_forecast["r_squared"]
    is not None
)

assert (
    created_forecast["confidence_score"]
    is not None
)


print(
    "MODEL METRICS: SUCCESS"
)

print(
    "Model:",
    created_forecast[
        "forecast_model"
    ],
)

print(
    "MAPE:",
    created_forecast["mape"],
)

print(
    "R2:",
    created_forecast[
        "r_squared"
    ],
)

print(
    "Accuracy:",
    created_forecast[
        "accuracy_score"
    ],
)

print(
    "Confidence:",
    created_forecast[
        "confidence_score"
    ],
)


# =========================================================
# LIST FORECASTS
# =========================================================

response = client.get(
    "/forecasts/",
    headers=headers,
)


print()
print("LIST FORECASTS")
print(
    "Status:",
    response.status_code,
)


assert response.status_code == 200, (
    response.text
)


forecasts = response.json()

print(
    "Forecasts returned:",
    len(forecasts),
)


assert any(
    forecast["id"]
    == forecast_id
    for forecast in forecasts
)


print(
    "LIST FORECASTS: SUCCESS"
)


# =========================================================
# COMPANY DATA FILTERING
# =========================================================

for forecast in forecasts:

    assert (
        forecast["company_id"]
        == user["company_id"]
    )


print(
    "COMPANY DATA FILTERING: SUCCESS"
)


# =========================================================
# GET SINGLE FORECAST
# =========================================================

response = client.get(
    f"/forecasts/{forecast_id}",
    headers=headers,
)


print()
print("GET SINGLE FORECAST")
print(
    "Status:",
    response.status_code,
)


assert response.status_code == 200, (
    response.text
)


single_forecast = response.json()


assert (
    single_forecast["id"]
    == forecast_id
)

assert (
    single_forecast["company_id"]
    == user["company_id"]
)


print(
    "GET FORECAST: SUCCESS"
)


# =========================================================
# UPDATE FORECAST
# =========================================================

update_payload = {
    "name": "Updated Sales Forecast",
    "description": (
        "Updated MUGONEXT forecast test"
    ),
}


response = client.put(
    f"/forecasts/{forecast_id}",
    json=update_payload,
    headers=headers,
)


print()
print("UPDATE FORECAST")
print(
    "Status:",
    response.status_code,
)


assert response.status_code == 200, (
    response.text
)


updated_forecast = (
    response.json()
)


assert (
    updated_forecast["name"]
    == "Updated Sales Forecast"
)


print(
    "UPDATE FORECAST: SUCCESS"
)


# =========================================================
# ARCHIVE FORECAST
# =========================================================

response = client.post(
    f"/forecasts/{forecast_id}/archive",
    headers=headers,
)


print()
print("ARCHIVE FORECAST")
print(
    "Status:",
    response.status_code,
)


assert response.status_code in (
    200,
    204,
), response.text


print(
    "ARCHIVE FORECAST: SUCCESS"
)


# =========================================================
# GET ARCHIVED FORECAST
# =========================================================

response = client.get(
    f"/forecasts/{forecast_id}",
    headers=headers,
)


print()
print("GET ARCHIVED FORECAST")
print(
    "Status:",
    response.status_code,
)


assert response.status_code == 404, (
    response.text
)


print(
    "ARCHIVED FORECAST HIDDEN: SUCCESS"
)


# =========================================================
# FINAL RESULT
# =========================================================

print()
print("=" * 60)
print("FORECAST API TEST: SUCCESS")
print("=" * 60)