import psycopg2


class DatabaseManager:
    def __init__(self, client):
        self.client = client

    def __enter__(self):
        self.cur = self.client.cursor()
        return self.cur

    def __exit__(self, exc_type, exc_value, traceback):
        self.cur.close()
        self.client.close()


class PgClient:
    def __init__(self, host, user, password, db, port=5432):
        self._host = host
        self._user = user
        self._password = password
        self._db = db
        self._port = port
        self.client = None

    def set_client(self):
        self.client = psycopg2.connect(
            host=self._host,
            port=self._port,
            user=self._user,
            password=self._password,
            dbname=self._db
        )

    def get_time_value(self, table):
        self.set_client()
        with DatabaseManager(self.client) as cur:
            cur.execute(f""" SELECT time, value FROM "{table}" """)
            data = cur.fetchall()
            return data