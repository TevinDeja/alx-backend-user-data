#!/usr/bin/env python3
"""Module for handling sensitive data in logs."""

import os
import re
import logging
from typing import List
import mysql.connector

SENSITIVE_FIELDS = ["name", "email", "phone", "ssn", "password"]

def obscure_data(fields: List[str], obscure_with: str, text: str, delimiter: str) -> str:
    """Obscures specified fields in a text string."""
    pattern = r'({})=[^{}]*'.format('|'.join(fields), delimiter)
    return re.sub(pattern, r'\1=' + obscure_with, text)

def setup_logger() -> logging.Logger:
    """Sets up and returns a logger for sensitive data."""
    logger = logging.getLogger("sensitive_data")
    handler = logging.StreamHandler()
    handler.setFormatter(SensitiveDataFormatter(SENSITIVE_FIELDS))
    logger.setLevel(logging.INFO)
    logger.propagate = False
    logger.addHandler(handler)
    return logger

def db_connect() -> mysql.connector.connection.MySQLConnection:
    """Establishes a database connection using environment variables."""
    return mysql.connector.connect(
        host=os.getenv("DATA_DB_HOST", "localhost"),
        database=os.getenv("DATA_DB_NAME", ""),
        user=os.getenv("DATA_DB_USER", "root"),
        password=os.getenv("DATA_DB_PASS", ""),
        port=3306
    )

def process_user_data():
    """Retrieves and logs user data from the database."""
    fields = "name,email,phone,ssn,password,ip,last_login,user_agent"
    query = f"SELECT {fields} FROM users;"
    logger = setup_logger()
    conn = db_connect()
    
    with conn.cursor() as cursor:
        cursor.execute(query)
        for row in cursor.fetchall():
            record = '; '.join(f"{col}={val}" for col, val in zip(fields.split(','), row))
            logger.info(record)

class SensitiveDataFormatter(logging.Formatter):
    """Custom formatter to obscure sensitive data in log records."""
    
    OBSCURED = "***"
    LOG_FORMAT = "[SENSITIVE] %(name)s %(levelname)s %(asctime)-15s: %(message)s"
    SEPARATOR = ";"
    
    def __init__(self, fields: List[str]):
        super().__init__(self.LOG_FORMAT)
        self.fields = fields
    
    def format(self, record: logging.LogRecord) -> str:
        """Formats the log record, obscuring sensitive fields."""
        formatted = super().format(record)
        return obscure_data(self.fields, self.OBSCURED, formatted, self.SEPARATOR)

if __name__ == "__main__":
    process_user_data()
