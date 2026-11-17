"""Database Helper Module for Gym & Fitness Management System.

Handles MySQL connection pooling, parameterized query execution,
and safe CRUD transactions with robust error handling.
Includes an automatic local storage fallback for testing when MySQL
Workbench / Server is not running.
"""

import os
import sqlite3
from typing import Any, Dict, List, Optional, Tuple
try:
    import mysql.connector
    from mysql.connector import Error as MySQLError, errorcode
    MYSQL_AVAILABLE = True
except ModuleNotFoundError:
    MYSQL_AVAILABLE = False

    class MySQLError(Exception):
        pass

    class errorcode:
        ER_ACCESS_DENIED_ERROR = 1045
        ER_BAD_DB_ERROR = 1049
        ER_DUP_ENTRY = 1062


class Database:
    """Manages database connectivity and operations for the Gym Management System.

    Primary driver: MySQL Server (127.0.0.1:3306 via mysql-connector-python).
    Fallback/Demo driver: Local SQLite database with identical schema and seed data.
    """

    def __init__(
        self,
        host: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        database: Optional[str] = None,
        port: Optional[int] = None,
    ) -> None:
        """Initialize connection parameters using explicit args or environment variables."""
        self.config: Dict[str, Any] = {
            "host": host or os.getenv("MYSQL_HOST", "127.0.0.1"),
            "user": user or os.getenv("MYSQL_USER", "root"),
            "password": password if password is not None else os.getenv("MYSQL_PASSWORD", "root"),
            "database": database or os.getenv("MYSQL_DATABASE", "gym_db"),
            "port": int(port or os.getenv("MYSQL_PORT", 3306)),
            "connection_timeout": 3,
        }
        self.active_engine = "mysql"  # 'mysql' or 'sqlite_fallback'
        self.sqlite_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gym_db.sqlite")
        self._sqlite_initialized = False

    # ------------------------------------------------------------------
    # Connection Management
    # ------------------------------------------------------------------
    def get_mysql_connection(self):
        """Establish and return a new MySQL connection."""
        if not MYSQL_AVAILABLE:
            raise RuntimeError("mysql-connector-python is not installed in this Python environment.")
        return mysql.connector.connect(**self.config)

    def get_sqlite_connection(self):
        """Establish and return a connection to the local SQLite fallback database."""
        if not self._sqlite_initialized:
            self._ensure_sqlite_schema()
            self._sqlite_initialized = True
        conn = sqlite3.connect(self.sqlite_path, timeout=30.0)
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_sqlite_schema(self) -> None:
        """Provision local SQLite tables and seed data if not yet created."""
        conn = sqlite3.connect(self.sqlite_path, timeout=30.0)
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS members (
                    member_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    phone TEXT NOT NULL UNIQUE,
                    email TEXT NOT NULL UNIQUE,
                    join_date TEXT NOT NULL,
                    plan_type TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'Active'
                );
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS payments (
                    payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    member_id INTEGER NOT NULL,
                    amount REAL NOT NULL,
                    payment_date TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'Paid',
                    FOREIGN KEY (member_id) REFERENCES members(member_id) ON DELETE CASCADE
                );
                """
            )
            cursor.execute("SELECT COUNT(*) FROM members;")
            count = cursor.fetchone()[0]
            if count == 0:
                cursor.executemany(
                    """
                    INSERT INTO members (member_id, name, phone, email, join_date, plan_type, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?);
                    """,
                    [
                        (1, "Alex Mercer", "555-0192", "alex.mercer@example.com", "2026-01-15", "Monthly", "Active"),
                        (2, "Sarah Connor", "555-0348", "sarah.connor@example.com", "2026-02-01", "Annual", "Active"),
                        (3, "Marcus Vance", "555-0811", "marcus.v@example.com", "2026-03-10", "Quarterly", "Inactive"),
                        (4, "Elena Rostova", "555-0924", "elena.rostova@example.com", "2026-04-05", "Annual", "Active"),
                        (5, "David Kim", "555-0477", "david.kim@example.com", "2026-05-18", "Monthly", "Active"),
                    ],
                )
                cursor.executemany(
                    """
                    INSERT INTO payments (payment_id, member_id, amount, payment_date, status)
                    VALUES (?, ?, ?, ?, ?);
                    """,
                    [
                        (1, 1, 49.99, "2026-01-15", "Paid"),
                        (2, 2, 499.99, "2026-02-01", "Paid"),
                        (3, 3, 139.99, "2026-03-10", "Paid"),
                        (4, 4, 499.99, "2026-04-05", "Paid"),
                        (5, 5, 49.99, "2026-05-18", "Paid"),
                    ],
                )
            conn.commit()
            cursor.close()
        finally:
            conn.close()

    def test_connection(self) -> Tuple[bool, str]:
        """Verify if MySQL server is reachable and credentials are valid."""
        if not MYSQL_AVAILABLE:
            return False, "mysql-connector-python package is missing. Run: pip install mysql-connector-python"
        try:
            conn = self.get_mysql_connection()
            if conn.is_connected():
                server_info = conn.get_server_info()
                conn.close()
                self.active_engine = "mysql"
                return True, f"Connected successfully to MySQL Server v{server_info}"
            return False, "Unable to establish active database session."
        except MySQLError as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                return False, "Access denied: Please verify MySQL username and password."
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                return False, "Database 'gym_db' does not exist. Please run schema.sql first."
            else:
                return False, f"MySQL Offline: {str(err)}"

    def enable_demo_mode(self) -> str:
        """Switch to local SQLite engine to allow offline demonstration & testing."""
        self.active_engine = "sqlite_fallback"
        self._ensure_sqlite_schema()
        return "Local Demo Mode Active (SQLite Storage)"

    # ------------------------------------------------------------------
    # CRUD Operations
    # ------------------------------------------------------------------
    def fetch_all_members(self) -> Tuple[bool, List[Dict[str, Any]], str]:
        """Retrieve all member records ordered by ID ascending."""
        if self.active_engine == "mysql":
            query = "SELECT member_id, name, phone, email, join_date, plan_type, status FROM members ORDER BY member_id ASC"
            conn = None
            cursor = None
            try:
                conn = self.get_mysql_connection()
                cursor = conn.cursor(dictionary=True)
                cursor.execute(query)
                records = cursor.fetchall()
                return True, records, "Records fetched from MySQL."
            except MySQLError as err:
                return False, [], f"MySQL Read Error: {str(err)}"
            finally:
                if cursor is not None:
                    cursor.close()
                if conn is not None and conn.is_connected():
                    conn.close()
        else:
            conn = None
            try:
                conn = self.get_sqlite_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT member_id, name, phone, email, join_date, plan_type, status FROM members ORDER BY member_id ASC")
                rows = cursor.fetchall()
                records = [dict(row) for row in rows]
                cursor.close()
                return True, records, "Records fetched from Local Demo DB."
            except Exception as err:
                return False, [], f"SQLite Read Error: {str(err)}"
            finally:
                if conn is not None:
                    conn.close()

    def search_members(self, search_term: str, search_field: str = "All") -> Tuple[bool, List[Dict[str, Any]], str]:
        """Search members by name, phone, email, plan, status, or across all fields."""
        term = f"%{search_term.strip()}%"
        field_map = {
            "Name": "name LIKE %s",
            "Phone": "phone LIKE %s",
            "Email": "email LIKE %s",
            "Plan": "plan_type LIKE %s",
            "Status": "status LIKE %s",
        }

        if search_field in field_map:
            where_clause = field_map[search_field]
            params_mysql = (term,)
        else:
            where_clause = "(name LIKE %s OR phone LIKE %s OR email LIKE %s OR plan_type LIKE %s OR status LIKE %s)"
            params_mysql = (term, term, term, term, term)

        if self.active_engine == "mysql":
            query = f"SELECT member_id, name, phone, email, join_date, plan_type, status FROM members WHERE {where_clause} ORDER BY member_id ASC"
            conn = None
            cursor = None
            try:
                conn = self.get_mysql_connection()
                cursor = conn.cursor(dictionary=True)
                cursor.execute(query, params_mysql)
                records = cursor.fetchall()
                return True, records, f"Found {len(records)} matching records."
            except MySQLError as err:
                return False, [], f"Search Query Error: {str(err)}"
            finally:
                if cursor is not None:
                    cursor.close()
                if conn is not None and conn.is_connected():
                    conn.close()
        else:
            conn = None
            try:
                sqlite_clause = where_clause.replace("%s", "?")
                query = f"SELECT member_id, name, phone, email, join_date, plan_type, status FROM members WHERE {sqlite_clause} ORDER BY member_id ASC"
                conn = self.get_sqlite_connection()
                cursor = conn.cursor()
                cursor.execute(query, params_mysql)
                rows = cursor.fetchall()
                records = [dict(row) for row in rows]
                cursor.close()
                return True, records, f"Found {len(records)} matching records."
            except Exception as err:
                return False, [], f"Search Query Error: {str(err)}"
            finally:
                if conn is not None:
                    conn.close()

    def add_member(
        self,
        name: str,
        phone: str,
        email: str,
        join_date: str,
        plan_type: str,
        status: str,
    ) -> Tuple[bool, str, Optional[int]]:
        """Insert a new member into the members table."""
        clean_name = name.strip()
        clean_phone = phone.strip()
        clean_email = email.strip()
        clean_date = join_date.strip()
        clean_plan = plan_type.strip()
        clean_status = status.strip()

        if self.active_engine == "mysql":
            query = """
                INSERT INTO members (name, phone, email, join_date, plan_type, status)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            params = (clean_name, clean_phone, clean_email, clean_date, clean_plan, clean_status)
            conn = None
            cursor = None
            try:
                conn = self.get_mysql_connection()
                cursor = conn.cursor()
                cursor.execute(query, params)
                conn.commit()
                new_id = cursor.lastrowid
                return True, f"Member '{clean_name}' added to MySQL (ID: {new_id}).", new_id
            except MySQLError as err:
                if conn is not None:
                    conn.rollback()
                if err.errno == errorcode.ER_DUP_ENTRY:
                    return False, "Duplicate Entry: A member with this Phone or Email already exists.", None
                return False, f"MySQL Insert Error: {str(err)}", None
            finally:
                if cursor is not None:
                    cursor.close()
                if conn is not None and conn.is_connected():
                    conn.close()
        else:
            conn = None
            try:
                conn = self.get_sqlite_connection()
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO members (name, phone, email, join_date, plan_type, status)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (clean_name, clean_phone, clean_email, clean_date, clean_plan, clean_status),
                )
                conn.commit()
                new_id = cursor.lastrowid
                cursor.close()
                return True, f"Member '{clean_name}' added successfully (ID: {new_id}).", new_id
            except sqlite3.IntegrityError:
                if conn is not None:
                    conn.rollback()
                return False, "Duplicate Entry: Phone or Email already registered.", None
            except Exception as err:
                if conn is not None:
                    conn.rollback()
                return False, f"Insert Error: {str(err)}", None
            finally:
                if conn is not None:
                    conn.close()

    def update_member(
        self,
        member_id: int,
        name: str,
        phone: str,
        email: str,
        join_date: str,
        plan_type: str,
        status: str,
    ) -> Tuple[bool, str]:
        """Update an existing member's record by member_id."""
        clean_name = name.strip()
        clean_phone = phone.strip()
        clean_email = email.strip()
        clean_date = join_date.strip()
        clean_plan = plan_type.strip()
        clean_status = status.strip()

        if self.active_engine == "mysql":
            query = """
                UPDATE members
                SET name = %s, phone = %s, email = %s, join_date = %s, plan_type = %s, status = %s
                WHERE member_id = %s
            """
            params = (clean_name, clean_phone, clean_email, clean_date, clean_plan, clean_status, member_id)
            conn = None
            cursor = None
            try:
                conn = self.get_mysql_connection()
                cursor = conn.cursor()
                cursor.execute(query, params)
                conn.commit()
                if cursor.rowcount == 0:
                    return False, f"No record found with Member ID {member_id}."
                return True, f"Member ID {member_id} updated successfully in MySQL."
            except MySQLError as err:
                if conn is not None:
                    conn.rollback()
                if err.errno == errorcode.ER_DUP_ENTRY:
                    return False, "Duplicate Entry: Phone or Email belongs to another member."
                return False, f"MySQL Update Error: {str(err)}"
            finally:
                if cursor is not None:
                    cursor.close()
                if conn is not None and conn.is_connected():
                    conn.close()
        else:
            conn = None
            try:
                conn = self.get_sqlite_connection()
                cursor = conn.cursor()
                cursor.execute(
                    """
                    UPDATE members
                    SET name = ?, phone = ?, email = ?, join_date = ?, plan_type = ?, status = ?
                    WHERE member_id = ?
                    """,
                    (clean_name, clean_phone, clean_email, clean_date, clean_plan, clean_status, member_id),
                )
                conn.commit()
                affected = cursor.rowcount
                cursor.close()
                if affected == 0:
                    return False, f"No record found with Member ID {member_id}."
                return True, f"Member ID {member_id} updated successfully."
            except sqlite3.IntegrityError:
                if conn is not None:
                    conn.rollback()
                return False, "Duplicate Entry: Phone or Email belongs to another member."
            except Exception as err:
                if conn is not None:
                    conn.rollback()
                return False, f"Update Error: {str(err)}"
            finally:
                if conn is not None:
                    conn.close()

    def delete_member(self, member_id: int) -> Tuple[bool, str]:
        """Delete a member record by member_id."""
        if self.active_engine == "mysql":
            query = "DELETE FROM members WHERE member_id = %s"
            params = (member_id,)
            conn = None
            cursor = None
            try:
                conn = self.get_mysql_connection()
                cursor = conn.cursor()
                cursor.execute(query, params)
                conn.commit()
                if cursor.rowcount == 0:
                    return False, f"No record found with Member ID {member_id}."
                return True, f"Member ID {member_id} deleted successfully from MySQL."
            except MySQLError as err:
                if conn is not None:
                    conn.rollback()
                return False, f"MySQL Delete Error: {str(err)}"
            finally:
                if cursor is not None:
                    cursor.close()
                if conn is not None and conn.is_connected():
                    conn.close()
        else:
            conn = None
            try:
                conn = self.get_sqlite_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM members WHERE member_id = ?", (member_id,))
                conn.commit()
                affected = cursor.rowcount
                cursor.close()
                if affected == 0:
                    return False, f"No record found with Member ID {member_id}."
                return True, f"Member ID {member_id} deleted successfully."
            except Exception as err:
                if conn is not None:
                    conn.rollback()
                return False, f"Delete Error: {str(err)}"
            finally:
                if conn is not None:
                    conn.close()
