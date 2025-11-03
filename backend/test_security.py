"""
Test security utilities.
"""
from uuid import uuid4
from app.settings import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_user_id_from_token,
    hash_password,
    validate_password_strength,
    verify_password,
    settings
)

def check_environment():
    if settings.ENVIRONMENT == "production":
        raise RuntimeError("Cannot generate tests in production!")

def test_password_hashing():
    """Test password hashing and verification."""
    print("Testing password hashing...")

    password = "my_super_secret_password"
    hashed = hash_password(password)

    print(f"Original: {password}")
    print(f"Hashed: {hashed}")
    # Test correct password
    assert verify_password(password, hashed), "Correct password verified"
    print("Correct password verified")
    # test wrong password
    assert not verify_password("wrong_password", hashed), "Wrong password rejected"
    print("Wrong password rejected")

def test_jwt_tokens():
    """TYest JWT token creation and decoding."""
    print("\nTesting JWT tokens...")

    user_id = uuid4()
    username = "clara"

    # Create tokens
    access_token = create_access_token(user_id, username)
    refresh_token = create_refresh_token(user_id)

    print(f"Access token: {access_token[:50]}...")
    print(f"Refresh token: {refresh_token[:50]}...")

    # Decode access token
    payload = decode_token(access_token)
    assert payload is not None, "Token decoded successfully"
    if payload.get("type") == "access":
        assert "username" in payload, "Username exists in payload"
        assert payload["username"] == username, "Username matches"
    print(f"Decoded payload: {payload}")

    # Extract user ID
    extracted_id = get_user_id_from_token(access_token)
    assert extracted_id == user_id, "User ID matches"
    print(f"Extracted user ID: {extracted_id}")

def test_password_validation():
    """test password strength validation."""
    print("\nTesting password validation...")

    # Bad password, too short
    valid, msg = validate_password_strength("short")
    assert not valid
    print(f"Too short password: {msg}")

    # Good password
    valid, msg = validate_password_strength("good_password")
    assert valid
    print("Good password accepted")

    # Bad password, too long
    valid, msg = validate_password_strength("x" * 51)
    print(f"Too long password: {msg}")

if __name__ == "__main__":
    check_environment()
    test_password_hashing()
    test_jwt_tokens()
    test_password_validation()
    print("\nAll security tests passed!")
