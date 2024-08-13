#!/usr/bin/env python3
"""A module for library management routines."""

import hashlib
from datetime import datetime, timedelta
from typing import Union
from sqlalchemy.orm.exc import NoResultFound
from database import Database
from book import Book
from member import Member

def generate_member_id() -> str:
    """Generates a unique member ID."""
    return hashlib.md5(str(datetime.now()).encode()).hexdigest()[:8]

def calculate_due_date(days: int = 14) -> str:
    """Calculates the due date for a book loan."""
    return (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")

class LibraryManager:
    """LibraryManager class to interact with the library database."""

    def __init__(self):
        """Initializes a new LibraryManager instance."""
        self._db = Database()

    def add_book(self, title: str, author: str, isbn: str) -> Book:
        """Adds a new book to the library."""
        try:
            self._db.find_book_by(isbn=isbn)
        except NoResultFound:
            return self._db.add_book(title, author, isbn)
        raise ValueError(f"Book with ISBN {isbn} already exists")

    def register_member(self, name: str, email: str) -> Member:
        """Registers a new library member."""
        try:
            self._db.find_member_by(email=email)
        except NoResultFound:
            member_id = generate_member_id()
            return self._db.add_member(member_id, name, email)
        raise ValueError(f"Member with email {email} already exists")

    def loan_book(self, member_id: str, isbn: str) -> bool:
        """Processes a book loan."""
        try:
            member = self._db.find_member_by(member_id=member_id)
            book = self._db.find_book_by(isbn=isbn)
            if book.is_available:
                due_date = calculate_due_date()
                self._db.update_book(book.id, is_available=False)
                self._db.add_loan(member.id, book.id, due_date)
                return True
            return False
        except NoResultFound:
            return False

    def return_book(self, isbn: str) -> Union[float, None]:
        """Processes a book return, calculates fine if any."""
        try:
            book = self._db.find_book_by(isbn=isbn)
            loan = self._db.find_active_loan_by(book_id=book.id)
            self._db.update_book(book.id, is_available=True)
            self._db.close_loan(loan.id)
            
            due_date = datetime.strptime(loan.due_date, "%Y-%m-%d")
            if datetime.now() > due_date:
                days_overdue = (datetime.now() - due_date).days
                return days_overdue * 0.5  # $0.50 per day
            return 0.0
        except NoResultFound:
            return None

    def get_member_loans(self, member_id: str) -> list:
        """Retrieves all active loans for a member."""
        try:
            member = self._db.find_member_by(member_id=member_id)
            return self._db.get_active_loans_for_member(member.id)
        except NoResultFound:
            return []

    def search_books(self, keyword: str) -> list:
        """Searches for books by title or author."""
        return self._db.search_books(keyword)

    def update_member_info(self, member_id: str, **kwargs) -> bool:
        """Updates a member's information."""
        try:
            member = self._db.find_member_by(member_id=member_id)
            self._db.update_member(member.id, **kwargs)
            return True
        except NoResultFound:
            return False
