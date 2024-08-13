#!/usr/bin/env python3
"""
UserManager Module
"""
from database import Database
from random import randint
from account import Account
from cryptography.fernet import Fernet
from typing import Optional
from sqlalchemy.orm.exc import NoResultFound

def generate_account_number() -> str:
    """
    Generate a random 10-digit account number
    """
    return str(randint(1000000000, 9999999999))

def encrypt_pin(pin: str) -> bytes:
    """
    Encrypt the PIN using Fernet
    """
    key = Fernet.generate_key()
    f = Fernet(key)
    return f.encrypt(pin.encode())

class UserManager:
    """
    UserManager class to handle user account operations
    """
    def __init__(self):
        self._db = Database()

    def create_account(self, name: str, initial_balance: float, pin: str) -> Account:
        """
        Create a new account with name, initial balance, and PIN
        """
        try:
            self._db.find_account_by(name=name)
            raise ValueError(f"Account for {name} already exists")
        except NoResultFound:
            account_number = generate_account_number()
            encrypted_pin = encrypt_pin(pin)
            return self._db.add_account(name, account_number, initial_balance, encrypted_pin)

    def verify_pin(self, account_number: str, pin: str) -> bool:
        """
        Verify the PIN for a given account number
        """
        try:
            account = self._db.find_account_by(account_number=account_number)
            f = Fernet(account.encrypted_pin[:44])
            decrypted_pin = f.decrypt(account.encrypted_pin[44:]).decode()
            return pin == decrypted_pin
        except NoResultFound:
            return False

    def get_balance(self, account_number: str) -> float:
        """
        Get the balance for a given account number
        """
        try:
            account = self._db.find_account_by(account_number=account_number)
            return account.balance
        except NoResultFound:
            raise ValueError("Account not found")

    def deposit(self, account_number: str, amount: float) -> None:
        """
        Deposit money into an account
        """
        try:
            account = self._db.find_account_by(account_number=account_number)
            new_balance = account.balance + amount
            self._db.update_account(account.id, balance=new_balance)
        except NoResultFound:
            raise ValueError("Account not found")

    def withdraw(self, account_number: str, amount: float) -> None:
        """
        Withdraw money from an account
        """
        try:
            account = self._db.find_account_by(account_number=account_number)
            if account.balance < amount:
                raise ValueError("Insufficient funds")
            new_balance = account.balance - amount
            self._db.update_account(account.id, balance=new_balance)
        except NoResultFound:
            raise ValueError("Account not found")

    def close_account(self, account_number: str) -> None:
        """
        Close an account
        """
        try:
            account = self._db.find_account_by(account_number=account_number)
            self._db.delete_account(account.id)
        except NoResultFound:
            raise ValueError("Account not found")
