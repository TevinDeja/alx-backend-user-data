#!/usr/bin/env python3
"""
Module for secure password management
"""
import hashlib
import os

def encrypt_password(password: str) -> bytes:
    """
    Generate a securely hashed version of the input password
    
    Args:
        password (str): The plain text password to hash
    
    Returns:
        bytes: The salted and hashed password
    """
    salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return salt + key

def verify_password(stored_password: bytes, provided_password: str) -> bool:
    """
    Check if the provided password matches the stored hashed password
    
    Args:
        stored_password (bytes): The previously hashed password
        provided_password (str): The password to verify
    
    Returns:
        bool: True if the passwords match, False otherwise
    """
    salt = stored_password[:32]
    key = stored_password[32:]
    new_key = hashlib.pbkdf2_hmac('sha256', provided_password.encode('utf-8'), salt, 100000)
    return key == new_key
