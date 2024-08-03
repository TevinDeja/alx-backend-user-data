#!/usr/bin/env python3
"""
A module for securing user credentials
"""
import bcrypt


def hash_password(password: str) -> bytes:
    """
    Generates a salted hash of the input password
    """
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())


def is_valid(hashed_password: bytes, password: str) -> bool:
    """
    Verifies if the provided password matches the stored hash
    """
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password)
