import sqlite3
from datetime import date
from pathlib import Path
from datetime import datetime

class sqlite:

    def __init__(self, db_file=None, sql_file=None):
        # Get the path to this file
        current_file = Path(__file__).resolve()

        # Project root = one folder up from models/
        project_root = current_file.parent.parent

        # Default DB path and SQL path
        self.db_file = Path(db_file) if db_file else project_root / "sqldb" / "checkin.db"
        self.sql_file = Path(sql_file) if sql_file else project_root / "sqldb" / "checkin_table.sql"

        # Ensure the sqldb folder exists
        self.db_file.parent.mkdir(parents=True, exist_ok=True)

        print(f"DB path: {self.db_file.resolve()}")
        print(f"SQL path: {self.sql_file.resolve()}")  # check this!
        self._init_db()

    def _init_db(self):
        if not self.sql_file.exists():
            raise FileNotFoundError(f"SQL file not found: {self.sql_file}")
        with open(self.sql_file, "r") as f:
            sql = f.read()
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.executescript(sql)  # run all commands in the SQL file
        conn.commit()
        conn.close()

    def get_user_info(self, username):
        """Get the username, image, total check-in count, and last check-in date for a user."""
        print(f"Get info for user {username}")
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute(
            "SELECT username, image, checkin_count, checkin_date FROM checkins WHERE username=?",
            (username,)
        )
        row = c.fetchone()
        conn.close()
        if row:
            username, image, checkin_count, last_checkin = row
            return username, image, checkin_count, last_checkin
        return None, None, 0, None

    def can_checkin(self, username="default_user"):
        today = date.today().strftime("%Y-%m-%d")
        _, _, _, last_checkin = self.get_user_info(username)

        if not last_checkin:
            # no check-in history → allow
            return True

        # last_checkin comes as "YYYY-MM-DD HH:MM:SS" → take only the date
        last_checkin_date = last_checkin.split(" ")[0]

        return last_checkin_date != today

    def checkin(self, username):
        """Check in a user: create new if not exists, otherwise increment checkin_count and update checkin_date."""
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()

        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        # Check if the user already exists
        c.execute("SELECT checkin_count FROM checkins WHERE username=?", (username,))
        row = c.fetchone()

        if row:
            # User exists → increment count + update date
            new_count = row[0] + 1
            c.execute(
                "UPDATE checkins SET checkin_count=?, checkin_date=? WHERE username=?",
                (new_count, now, username)
            )
        else:
            # New user → insert row
            c.execute(
                "INSERT INTO checkins (username, checkin_date, checkin_count) VALUES (?, ?, ?)",
                (username, now, 1)
            )

        conn.commit()
        conn.close()
        return True, f"Check-in successful! ✅"
