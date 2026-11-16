import re
from getpass import getpass

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from department_ai.infrastructure.database.session import SessionLocal
from department_ai.modules.identity.infrastructure.models import (
    Organization,
    OrganizationMembership,
    User,
)
from department_ai.modules.identity.infrastructure.security import hash_password


def main() -> None:
    email = input("Administrator email: ").strip().casefold()
    full_name = input("Administrator name: ").strip()
    organization_name = input("Organization name: ").strip()
    organization_slug = input("Organization slug [department]: ").strip().lower() or "department"
    password = getpass("Password (at least 12 characters): ")
    password_confirmation = getpass("Repeat password: ")

    if "@" not in email or not full_name or not organization_name:
        raise SystemExit("Enter a valid email, administrator name, and organization name.")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", organization_slug):
        raise SystemExit("Organization slug must contain lowercase letters, numbers, and hyphens.")
    if len(password) < 12 or len(password) > 1024:
        raise SystemExit("Password must be between 12 and 1024 characters.")
    if password != password_confirmation:
        raise SystemExit("Passwords do not match.")

    encoded_password = hash_password(password)
    try:
        with SessionLocal.begin() as session:
            existing_admin = session.scalar(
                select(OrganizationMembership.user_id)
                .where(OrganizationMembership.role == "admin")
                .limit(1)
            )
            if existing_admin is not None:
                raise SystemExit("An administrator already exists; bootstrap is disabled.")

            organization = Organization(name=organization_name, slug=organization_slug)
            user = User(
                email=email,
                full_name=full_name,
                password_hash=encoded_password,
            )
            session.add_all([organization, user])
            session.flush()
            session.add(
                OrganizationMembership(
                    user_id=user.id,
                    organization_id=organization.id,
                    role="admin",
                )
            )
    except IntegrityError:
        raise SystemExit("That email or organization slug is already in use.") from None

    print(f"Created administrator {email} for {organization_name}.")


if __name__ == "__main__":
    main()
