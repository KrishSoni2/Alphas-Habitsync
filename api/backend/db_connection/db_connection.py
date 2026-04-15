# Sahib Chawla
# Database connection helper

import mysql.connector
import os


def get_db():
    """
    Returns a connection to the MySQL database using
    environment variables for configuration.
    """
    db_connection = mysql.connector.connect(
        host=os.getenv('DB_HOST', 'db'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('MYSQL_ROOT_PASSWORD', 'password'),
        database=os.getenv('DB_NAME', 'HabitSync'),
        port=int(os.getenv('DB_PORT', 3306))
    )
    return db_connection
