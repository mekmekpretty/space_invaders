import mysql.connector
from mysql.connector import Error


# =========================================================
# DATABASE CONNECTION
# =========================================================

def create_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            database="melca_db",
            user="root",
            password=""
        )

        if connection.is_connected():
            return connection

    except Error as e:
        print(f"Database Connection Error: {e}")

    return None


def get_db_connection():
    return create_connection()


# =========================================================
# DATABASE SETUP
# =========================================================

def setup_database():
    conn = create_connection()

    if not conn:
        return False

    cursor = conn.cursor()

    try:
        # -------------------------------------------------
        # PLAYERS TABLE
        # -------------------------------------------------

        cursor.execute("SHOW TABLES LIKE 'players'")
        players_exists = cursor.fetchone()

        if not players_exists:
            cursor.execute("""
                CREATE TABLE players (
                    player_id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) NOT NULL UNIQUE,
                    email VARCHAR(100) NULL UNIQUE,
                    password VARCHAR(255) NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

        else:
            cursor.execute("SHOW COLUMNS FROM players")
            columns = [row[0] for row in cursor.fetchall()]

            if "email" not in columns:
                cursor.execute("""
                    ALTER TABLE players
                    ADD COLUMN email VARCHAR(100) NULL
                """)

            if "password" not in columns:
                cursor.execute("""
                    ALTER TABLE players
                    ADD COLUMN password VARCHAR(255) NULL
                """)

        # -------------------------------------------------
        # SCORES TABLE
        # -------------------------------------------------

        cursor.execute("SHOW TABLES LIKE 'scores'")
        scores_exists = cursor.fetchone()

        if not scores_exists:
            cursor.execute("""
                CREATE TABLE scores (
                    score_id INT AUTO_INCREMENT PRIMARY KEY,
                    player_id INT NOT NULL,
                    score INT NOT NULL DEFAULT 0,
                    date_added TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

                    FOREIGN KEY (player_id)
                    REFERENCES players(player_id)
                    ON DELETE CASCADE
                )
            """)

        else:
            cursor.execute("SHOW COLUMNS FROM scores")
            score_columns = [row[0] for row in cursor.fetchall()]

            if "date_added" not in score_columns:
                cursor.execute("""
                    ALTER TABLE scores
                    ADD COLUMN date_added
                    TIMESTAMP NOT NULL
                    DEFAULT CURRENT_TIMESTAMP
                """)

        conn.commit()

        return True

    except Error as e:
        print(f"Database Setup Error: {e}")
        conn.rollback()
        return False

    finally:
        cursor.close()
        conn.close()


# =========================================================
# REGISTER PLAYER
# =========================================================

def register_player(username, email, password):

    conn = get_db_connection()

    if not conn:
        return False, "DATABASE CONNECTION FAILED"

    cursor = conn.cursor()

    try:
        username = username.strip()
        email = email.strip().lower()

        # -------------------------------------------------
        # CHECK USERNAME
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT player_id
            FROM players
            WHERE LOWER(username) = LOWER(%s)
            LIMIT 1
            """,
            (username,)
        )

        username_exists = cursor.fetchone()

        if username_exists:
            return False, "USERNAME ALREADY EXISTS"

        # -------------------------------------------------
        # CHECK EMAIL
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT player_id
            FROM players
            WHERE LOWER(email) = LOWER(%s)
            LIMIT 1
            """,
            (email,)
        )

        email_exists = cursor.fetchone()

        if email_exists:
            return False, "EMAIL ALREADY EXISTS"

        # -------------------------------------------------
        # CREATE ACCOUNT
        # -------------------------------------------------

        cursor.execute(
            """
            INSERT INTO players
            (
                username,
                email,
                password
            )
            VALUES
            (
                %s,
                %s,
                %s
            )
            """,
            (
                username,
                email,
                password
            )
        )

        conn.commit()

        return True, "ACCOUNT CREATED"

    except Error as e:

        conn.rollback()

        print(f"Registration Error: {e}")

        error_text = str(e).lower()

        if "username" in error_text:
            return False, "USERNAME ALREADY EXISTS"

        if "email" in error_text:
            return False, "EMAIL ALREADY EXISTS"

        if "duplicate" in error_text:
            return False, "USERNAME OR EMAIL ALREADY EXISTS"

        return False, "DATABASE ERROR"

    finally:
        cursor.close()
        conn.close()


# =========================================================
# LOGIN PLAYER
# =========================================================

def login_player(username_or_email, password):

    conn = get_db_connection()

    if not conn:
        print("Login Error: Database connection failed")
        return None

    cursor = conn.cursor(dictionary=True)

    try:

        identifier = username_or_email.strip()

        # -------------------------------------------------
        # LOGIN USING USERNAME OR EMAIL
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                player_id,
                username,
                email,
                password
            FROM players
            WHERE LOWER(username) = LOWER(%s)
               OR LOWER(email) = LOWER(%s)
            LIMIT 1
            """,
            (
                identifier,
                identifier
            )
        )

        player = cursor.fetchone()

        if not player:
            return None

        # -------------------------------------------------
        # CHECK PASSWORD
        # -------------------------------------------------

        if player["password"] != password:
            return None

        # Do not return password
        player.pop("password", None)

        return player

    except Error as e:

        print(f"Login Error: {e}")

        return None

    finally:
        cursor.close()
        conn.close()


# =========================================================
# SAVE SCORE
# =========================================================

def save_score(player_id, score):

    conn = get_db_connection()

    if not conn:
        return False

    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            INSERT INTO scores
            (
                player_id,
                score,
                date_added
            )
            VALUES
            (
                %s,
                %s,
                CURRENT_TIMESTAMP
            )
            """,
            (
                player_id,
                score
            )
        )

        conn.commit()

        return True

    except Error as e:

        print(f"Score Error: {e}")

        conn.rollback()

        return False

    finally:
        cursor.close()
        conn.close()


# =========================================================
# LOAD LEADERBOARD
# =========================================================

def load_leaderboard():

    conn = get_db_connection()

    if not conn:
        return []

    cursor = conn.cursor(dictionary=True)

    try:

        cursor.execute(
            """
            SELECT
                p.player_id,
                p.username,
                s.score,
                s.date_added

            FROM players p

            INNER JOIN scores s
                ON s.player_id = p.player_id

            INNER JOIN (
                SELECT
                    player_id,
                    MAX(score) AS highest_score

                FROM scores

                GROUP BY player_id
            ) h

                ON h.player_id = s.player_id
                AND h.highest_score = s.score

            WHERE s.score = (
                SELECT MAX(s2.score)

                FROM scores s2

                WHERE s2.player_id = s.player_id
            )

            ORDER BY
                s.score DESC,
                s.date_added DESC

            LIMIT 10
            """
        )

        rows = cursor.fetchall()

        result = []

        used_players = set()

        for row in rows:

            if row["player_id"] not in used_players:

                result.append(row)

                used_players.add(
                    row["player_id"]
                )

        return result

    except Error as e:

        print(f"Leaderboard Error: {e}")

        return []

    finally:
        cursor.close()
        conn.close()


# =========================================================
# GET PLAYER HIGHEST SCORE
# =========================================================

def get_player_highest_score(player_id):

    conn = get_db_connection()

    if not conn:
        return 0

    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            SELECT COALESCE(MAX(score), 0)

            FROM scores

            WHERE player_id = %s
            """,
            (player_id,)
        )

        result = cursor.fetchone()

        if result:
            return result[0]

        return 0

    except Error as e:

        print(f"Highest Score Error: {e}")

        return 0

    finally:
        cursor.close()
        conn.close()


# =========================================================
# UPDATE PLAYER PROFILE
# =========================================================

def update_player_profile(
    player_id,
    new_username,
    new_email
):

    conn = get_db_connection()

    if not conn:
        return False

    cursor = conn.cursor()

    try:

        new_username = new_username.strip()
        new_email = new_email.strip().lower()

        # -------------------------------------------------
        # CHECK IF ANOTHER PLAYER HAS THE SAME USERNAME
        # OR EMAIL
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT player_id

            FROM players

            WHERE
                (
                    LOWER(username) = LOWER(%s)
                    OR LOWER(email) = LOWER(%s)
                )

                AND player_id != %s

            LIMIT 1
            """,
            (
                new_username,
                new_email,
                player_id
            )
        )

        existing = cursor.fetchone()

        if existing:
            return False

        # -------------------------------------------------
        # UPDATE PROFILE
        # -------------------------------------------------

        cursor.execute(
            """
            UPDATE players

            SET
                username = %s,
                email = %s

            WHERE player_id = %s
            """,
            (
                new_username,
                new_email,
                player_id
            )
        )

        conn.commit()

        return cursor.rowcount > 0

    except Error as e:

        print(f"Profile Error: {e}")

        conn.rollback()

        return False

    finally:
        cursor.close()
        conn.close()


# =========================================================
# DELETE PLAYER
# =========================================================

def delete_player(player_id):

    conn = get_db_connection()

    if not conn:
        return False

    cursor = conn.cursor()

    try:

        # -------------------------------------------------
        # DELETE PLAYER
        #
        # Because scores uses ON DELETE CASCADE,
        # all scores belonging to this player will also
        # be deleted automatically.
        # -------------------------------------------------

        cursor.execute(
            """
            DELETE FROM players

            WHERE player_id = %s
            """,
            (player_id,)
        )

        deleted_rows = cursor.rowcount

        conn.commit()

        if deleted_rows > 0:
            print(
                f"Player {player_id} successfully deleted."
            )
            return True

        print(
            f"No player found with ID {player_id}."
        )

        return False

    except Error as e:

        print(f"Delete Error: {e}")

        conn.rollback()

        return False

    finally:
        cursor.close()
        conn.close()


# =========================================================
# CHECK IF USERNAME EXISTS
# =========================================================

def username_exists(username):

    conn = get_db_connection()

    if not conn:
        return False

    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            SELECT player_id

            FROM players

            WHERE LOWER(username) = LOWER(%s)

            LIMIT 1
            """,
            (username.strip(),)
        )

        return cursor.fetchone() is not None

    except Error as e:

        print(f"Username Check Error: {e}")

        return False

    finally:
        cursor.close()
        conn.close()


# =========================================================
# CHECK IF EMAIL EXISTS
# =========================================================

def email_exists(email):

    conn = get_db_connection()

    if not conn:
        return False

    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            SELECT player_id

            FROM players

            WHERE LOWER(email) = LOWER(%s)

            LIMIT 1
            """,
            (email.strip().lower(),)
        )

        return cursor.fetchone() is not None

    except Error as e:

        print(f"Email Check Error: {e}")

        return False

    finally:
        cursor.close()
        conn.close()


# =========================================================
# RUN DATABASE SETUP
# =========================================================

if __name__ == "__main__":

    if setup_database():
        print("DATABASE READY")
    else:
        print("DATABASE SETUP FAILED")