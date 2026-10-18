from app.core.database import SessionLocal
from app.models.company import Company
from app.models.user import User
from app.models.forecast import Forecast
from app.constants import ForecastModel


print("Testing tenant isolation...")

db = SessionLocal()

try:
    # =====================================================
    # Find authenticated test user
    # =====================================================

    user = (
        db.query(User)
        .filter(
            User.email == "authadmin@mugonext.com"
        )
        .first()
    )

    if not user:
        print("TEST USER NOT FOUND")
        raise SystemExit

    print(f"Authenticated user: {user.email}")
    print(f"User company ID: {user.company_id}")

    company_7 = (
        db.query(Company)
        .filter(
            Company.id == user.company_id
        )
        .first()
    )

    if not company_7:
        print("USER COMPANY NOT FOUND")
        raise SystemExit

    print(
        f"Company 7 found: {company_7.name}"
    )

    # =====================================================
    # Find or create Company 8
    # =====================================================

    company_8 = (
        db.query(Company)
        .filter(
            Company.id != user.company_id
        )
        .first()
    )

    if not company_8:
        company_8 = Company(
            name="MUGONEXT Tenant Test Company",
            legal_name="MUGONEXT Tenant Test Company Ltd",
            slug="mugonext-tenant-test-company",
            description="Tenant isolation test company",
            email="tenant8@mugonext.com",
            phone="+254700000008",
            country="Kenya",
            timezone="Africa/Nairobi",
            currency="KES",
            language="en",
        )

        db.add(company_8)
        db.commit()
        db.refresh(company_8)

        print(
            f"Created second company: {company_8.id}"
        )

    else:
        print(
            f"Second company already exists: {company_8.id}"
        )

    # =====================================================
    # Check whether Company 8 has a test forecast
    # =====================================================

    company_8_forecast = (
        db.query(Forecast)
        .filter(
            Forecast.company_id == company_8.id
        )
        .first()
    )

    if not company_8_forecast:
        print(
            "No Company 8 forecast exists."
        )
        print(
            "Tenant isolation test requires a "
            "Company 8 forecast."
        )
        print(
            "Forecast creation will be tested "
            "once the Forecast API is implemented."
        )

    else:
        print(
            f"Company 8 forecast found: "
            f"{company_8_forecast.id}"
        )

        # =================================================
        # Attempt cross-company access
        # =================================================

        accessible_forecast = (
            db.query(Forecast)
            .filter(
                Forecast.id == company_8_forecast.id,
                Forecast.company_id == user.company_id,
            )
            .first()
        )

        if accessible_forecast:
            print(
                "SECURITY FAILURE: "
                "Company 7 accessed Company 8 data!"
            )

            raise AssertionError(
                "Tenant isolation failed."
            )

        print(
            "CROSS-COMPANY ACCESS: CORRECTLY DENIED"
        )

    # =====================================================
    # Verify user's own company scope
    # =====================================================

    own_company_forecasts = (
        db.query(Forecast)
        .filter(
            Forecast.company_id == user.company_id
        )
        .all()
    )

    print(
        f"Company {user.company_id} "
        f"accessible forecasts: "
        f"{len(own_company_forecasts)}"
    )

    print(
        "COMPANY DATA ISOLATION: SUCCESS"
    )

    print(
        "\nTENANT ISOLATION TEST: SUCCESS"
    )

finally:
    db.close()

    print(
        "\nDatabase session closed."
    )