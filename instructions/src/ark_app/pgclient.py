"""
Module for managing PostgreSQL database connections and queries.

The module is intended to be used where there is a need to interact with
PostgreSQL databases. It simplifies connection handling and querying by
abstracting the details of psycopg2 connection management.

Classes:
    DatabaseManager: Context manager for handling database connections and cursor.
    PgClient: Manages PostgreSQL database connections and queries.
"""
import psycopg2


class DatabaseManager:
    """
    Context manager for handling database connections.

    Attributes:
        client: A psycopg2 database connection object.
    """

    def __init__(self, client):
        """
        Initialize the DatabaseManager with a psycopg2 client.

        Args:
            client: A psycopg2 database connection object.
        """
        self.client = client

    def __enter__(self):
        """
        Enter the runtime.

        Returns:
            A cursor object used to perform database operations.
        """
        self.cur = self.client.cursor()
        return self.cur

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Exit the runtime and close the database connection.

        Args:
            exc_type: Exception type.
            exc_value: Exception value.
            traceback: Traceback object.

        This method handles the closing of the cursor and the connection.
        """
        self.cur.close()
        self.client.close()


class PgClient:
    """
    PostgreSQL database client.

    Attributes:
        _host: Database host address.
        _user: Database user.
        _password: Password for the database user.
        _db: Database name.
        _port: Port number for the database.
    """

    def __init__(self, host: str, user: str, password: str, db: str, port: int = 5432):
        """
        Initialize the PostgreSQL client with connection parameters.

        Args:
            host: Database host address.
            user: Database user.
            password: Password for the database user.
            db: Database name.
            port: Port number for the database.
        """
        self._host = host
        self._user = user
        self._password = password
        self._db = db
        self._port = port
        self.client = None

    def set_client(self):
        """
        Establish a connection to the PostgreSQL database.

        This method sets up the client attribute with a psycopg2 connection object.
        """
        self.client = psycopg2.connect(
            host=self._host,
            port=self._port,
            user=self._user,
            password=self._password,
            dbname=self._db
        )

    def get_time_value(self, table: str):
        """
        Retrieve time and value data from a specified table.

        Args:
            table: The name of the table to query.

        Returns:
            A list of tuples containing the time and value data from the table.
        """
        self.set_client()
        with DatabaseManager(self.client) as cur:
            cur.execute(f""" SELECT time, value FROM "{table}" """)
            data = cur.fetchall()
            return data
