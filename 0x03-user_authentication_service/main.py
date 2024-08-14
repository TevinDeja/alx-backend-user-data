#!/usr/bin/env python3
"""End-to-end integration test
"""
import requests


def register_user(email: str, password: str) -> None:
    """
    Register a new user.
    
    Args:
        email (str): The user's email.
        password (str): The user's password.
    
    Raises:
        AssertionError: If the registration fails or returns unexpected response.
    """
    response = requests.post('http://localhost:5000/users', data={'email': email, 'password': password})
    assert response.status_code == 200, f"Failed to register user. Status code: {response.status_code}"
    assert response.json() == {"email": email, "message": "user created"}, "Unexpected response payload"


def log_in_wrong_password(email: str, password: str) -> None:
    """
    Attempt to log in with a wrong password.
    
    Args:
        email (str): The user's email.
        password (str): An incorrect password.
    
    Raises:
        AssertionError: If the login doesn't fail as expected.
    """
    response = requests.post('http://localhost:5000/sessions', data={'email': email, 'password': password})
    assert response.status_code == 401, f"Expected 401, got {response.status_code}"


def log_in(email: str, password: str) -> str:
    """
    Log in a user.
    
    Args:
        email (str): The user's email.
        password (str): The user's password.
    
    Returns:
        str: The session ID for the logged-in user.
    
    Raises:
        AssertionError: If the login fails or returns unexpected response.
    """
    response = requests.post('http://localhost:5000/sessions', data={'email': email, 'password': password})
    assert response.status_code == 200, f"Failed to log in. Status code: {response.status_code}"
    assert 'session_id' in response.json(), "No session_id in response"
    return response.json()['session_id']


def profile_unlogged() -> None:
    """
    Attempt to access profile without being logged in.
    
    Raises:
        AssertionError: If the request doesn't fail as expected.
    """
    response = requests.get('http://localhost:5000/profile')
    assert response.status_code == 403, f"Expected 403, got {response.status_code}"


def profile_logged(session_id: str) -> None:
    """
    Access profile while logged in.
    
    Args:
        session_id (str): The session ID of the logged-in user.
    
    Raises:
        AssertionError: If the profile access fails or returns unexpected response.
    """
    response = requests.get('http://localhost:5000/profile', cookies={'session_id': session_id})
    assert response.status_code == 200, f"Failed to get profile. Status code: {response.status_code}"
    assert 'email' in response.json(), "No email in response"


def log_out(session_id: str) -> None:
    """
    Log out a user.
    
    Args:
        session_id (str): The session ID of the logged-in user.
    
    Raises:
        AssertionError: If the logout fails or returns unexpected response.
    """
    response = requests.delete('http://localhost:5000/sessions', cookies={'session_id': session_id})
    assert response.status_code == 200, f"Failed to log out. Status code: {response.status_code}"
    assert response.json() == {"message": "Bienvenue"}, "Unexpected response payload"


def reset_password_token(email: str) -> str:
    """
    Request a password reset token.
    
    Args:
        email (str): The email of the user requesting a password reset.
    
    Returns:
        str: The reset token.
    
    Raises:
        AssertionError: If the request fails or returns unexpected response.
    """
    response = requests.post('http://localhost:5000/reset_password', data={'email': email})
    assert response.status_code == 200, f"Failed to get reset token. Status code: {response.status_code}"
    assert 'reset_token' in response.json(), "No reset_token in response"
    return response.json()['reset_token']

def update_password(email: str, reset_token: str, new_password: str) -> None:
    """
    Update a user's password using a reset token.
    
    Args:
        email (str): The user's email.
        reset_token (str): The reset token obtained from reset_password_token().
        new_password (str): The new password to set.
    
    Raises:
        AssertionError: If the password update fails or returns unexpected response.
    """
    response = requests.put('http://localhost:5000/reset_password', 
                            data={'email': email, 'reset_token': reset_token, 'new_password': new_password})
    assert response.status_code == 200, f"Failed to update password. Status code: {response.status_code}"
    assert response.json() == {"email": email, "message": "Password updated"}, "Unexpected response payload"

EMAIL = "guillaume@holberton.io"
PASSWD = "b4l0u"
NEW_PASSWD = "t4rt1fl3tt3"

if __name__ == "__main__":
    register_user(EMAIL, PASSWD)
    log_in_wrong_password(EMAIL, NEW_PASSWD)
    profile_unlogged()
    session_id = log_in(EMAIL, PASSWD)
    profile_logged(session_id)
    log_out(session_id)
    reset_token = reset_password_token(EMAIL)
    update_password(EMAIL, reset_token, NEW_PASSWD)
    log_in(EMAIL, NEW_PASSWD)
