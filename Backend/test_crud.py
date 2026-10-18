from app.core.database import SessionLocal
from app.models.company import Company

db = SessionLocal()

try:
    print("Testing database CRUD...")

    # ==========================
    # CREATE
    # ==========================

    company = Company(
        name="MUGONEXT CRUD Test",
        slug="mugonext-crud-test",
        email="crud@mugonext.com",
        country="Kenya",
    )

    db.add(company)
    db.commit()
    db.refresh(company)

    print("CREATE: SUCCESS")
    print(f"Created company ID: {company.id}")

    # ==========================
    # READ
    # ==========================

    found_company = (
        db.query(Company)
        .filter(Company.id == company.id)
        .first()
    )

    print("READ: SUCCESS")
    print(f"Found: {found_company.name}")

    # ==========================
    # UPDATE
    # ==========================

    found_company.name = "MUGONEXT Updated Company"

    db.commit()
    db.refresh(found_company)

    print("UPDATE: SUCCESS")
    print(f"Updated name: {found_company.name}")

    # ==========================
    # DELETE
    # ==========================

    db.delete(found_company)
    db.commit()

    print("DELETE: SUCCESS")

    # ==========================
    # VERIFY DELETE
    # ==========================

    deleted_company = (
        db.query(Company)
        .filter(Company.id == company.id)
        .first()
    )

    if deleted_company is None:
        print("DELETE VERIFICATION: SUCCESS")
    else:
        print("DELETE VERIFICATION: FAILED")

finally:
    db.close()
    print("Database session closed.")