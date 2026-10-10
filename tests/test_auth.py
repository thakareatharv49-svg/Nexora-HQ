from src.nexora_hq.auth import create_session, hash_password, verify_password, verify_session


def test_scrypt_password_hash_verifies_only_the_correct_password():
    encoded = hash_password("correct horse battery staple")
    assert encoded.startswith("scrypt$16384$8$1$")
    assert verify_password("correct horse battery staple", encoded)
    assert not verify_password("wrong password", encoded)
    assert not verify_password("wrong password", "malformed")


def test_signed_session_rejects_tampering_and_expiry():
    secret = "test-secret-that-is-long-enough-for-session-signing"
    token = create_session(secret, now=1_000)
    assert verify_session(token, secret, now=1_001)
    assert not verify_session(token + "tampered", secret, now=1_001)
    assert not verify_session(token, secret, now=1_000 + 8 * 60 * 60)
    assert not verify_session(None, secret, now=1_001)
