"""
Database Connection Module
Provides functions to establish and manage database connections.
"""

import logging
import psycopg2
from psycopg2.extensions import connection
import streamlit as st

DB_PARAMS = {
    "dbname": st.secrets["DATABASE_NAME"],
    "user": st.secrets["DATABASE_USERNAME"],
    "password": st.secrets["DATABASE_PASSWORD"],
    "host": st.secrets["DATABASE_HOST"],
    "port": st.secrets["DATABASE_PORT"],
}

logger = logging.getLogger(__name__)


def get_connection() -> connection:
    """
    Get a connection to the PostgreSQL database.

    This function uses the connection parameters stored in the Streamlit secrets.

    Returns:
        connection: A PostgreSQL database connection
    """
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        return conn
    except Exception as e:
        logger.error(f"Error connecting to database: {e}")
        raise
