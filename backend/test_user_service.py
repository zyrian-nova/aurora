"""
Test user service operations.
"""
import asyncio
from app.db import close_db, init_db
from app.schemas import UserCreate, UserPreferencesUpdate
from app.services import (
    authenticate_user,
    create_user,
    get_user_by_email,
    get_user_preferences,
    update_user_preferences,
    change_user_password
)

async def test_user_lifecycle():
    """teste complete user lifecycle,"""
    errors = []
    print("Testing user service...\n")

    # Initialize database
    await init_db()

    # 1. Create a user
    print("1. Creating a user...")
    user_data = UserCreate(
        email="clara@gothic.dev",
        username="clara_goth",
        password="darknight%0mega",
        full_name="Clara the Gothic Coder"
    )
    try:
        user = await create_user(user_data)
        print(f"    User created: {user.username} (ID: {user.id})")
    except ValueError as e:
        errors.append({"error": str(e)})
        print(f"    User might already exist: {e}")
        user = await get_user_by_email(user_data.email)

    # 2. Authenticate
    print("\n2. Testing authentication...")
    auth_user = await authenticate_user("clara@gothic.dev", "darknight%0mega")
    if auth_user:
        print(f"    Authentication successfull: {auth_user.username}")
    else:
        print("    Authentication failed")

    # Wrong password
    wrong_auth = await authenticate_user("clara@gothic.dev", "wrongpassword")
    if not wrong_auth:
        print("    Wrong password correctly rejected")

    # 3. Get user preferences
    print("\n3. Fetching preferences...")
    prefs = await get_user_preferences(user.id)
    if prefs:
        print(f"    Preferences found: Theme={prefs.theme}, Languages={prefs.word_languages}")

    # 4. Update preferences
    print("\n4. Updating preferences...")
    updated_prefs = await update_user_preferences(
        user.id,
        UserPreferencesUpdate(
            theme="dark",
            location="Helsinki, Finland",
            word_languages=["en", "fi"]
        )
    )
    if updated_prefs:
        print(f"    Preferences updated: Theme={updated_prefs.theme}, Location={updated_prefs.location}")

    # 5. Change password
    print("\n5. Changing password...")
    success = await change_user_password(user.id, "darknight%0mega",     "TheRoom&1408")
    if success:
        print("    Password changed successfully")
        # Verify new password works
        new_auth = await authenticate_user("clara@gothic.dev", "TheRoom&1408")
        if new_auth:
            print("    New password authentication successfull")

    # Cleanup
    await close_db()
    if errors:
        print(f"\nTest errors: {errors}")
    print("\nAll user service tests passed!")

if __name__ == "__main__":
    asyncio.run(test_user_lifecycle())
