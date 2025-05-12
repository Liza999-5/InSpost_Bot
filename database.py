import sqlite3
from datetime import date

file_db = "./db/database.db"


def init_db():
    with sqlite3.connect(file_db) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS nutrition (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                calories REAL,
                proteins REAL,
                fats REAL,
                carbs REAL,
                UNIQUE(user_id, date)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS meals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                name TEXT NOT NULL,
                calories REAL NOT NULL,
                proteins REAL NOT NULL,
                fats REAL NOT NULL,
                carbs REAL NOT NULL
            )
        """)
        
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            calories REAL NOT NULL DEFAULT 2380,
            proteins REAL NOT NULL DEFAULT 88,
            fats REAL NOT NULL DEFAULT 66,
            carbs REAL NOT NULL DEFAULT 359
    )
""")
        conn.commit()



def checkIsTodayCreate(user_id):
    today = date.today().isoformat()

    with sqlite3.connect(file_db) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 1 FROM nutrition WHERE user_id = ? AND date = ?
        """, (user_id, today))
        
        exists = cursor.fetchone()

        if not exists:
            cursor.execute("""
                INSERT INTO nutrition (user_id, date, calories, proteins, fats, carbs)
                VALUES (?, ?, 0, 0, 0, 0)
            """, (user_id, today))
            conn.commit()
          
            
def getNorm(user_id):
    with sqlite3.connect(file_db) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT calories, proteins, fats, carbs
                FROM daily_goals
                WHERE user_id = ?
            """, (user_id,))
            goal = cursor.fetchone()
            return goal
        except:
            return [2380, 88, 66, 359]
    
def setNorm(user_id, c, p, f, ch):
    with sqlite3.connect(file_db) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM daily_goals WHERE user_id = ?", (user_id,))
        existing_record = cursor.fetchone()
        if existing_record:
            cursor.execute("""
                UPDATE daily_goals 
                SET calories = ?, proteins = ?, fats = ?, carbs = ?
                WHERE user_id = ?
            """, (c, p, f, ch, user_id))
        else:
            cursor.execute("""
                INSERT INTO daily_goals (user_id, calories, proteins, fats, carbs)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, c, p, f, ch))
    

def get_daily_stats(user_id):
    checkIsTodayCreate(user_id)
    today = date.today().isoformat()

    with sqlite3.connect(file_db) as conn:
        cursor = conn.cursor()

        # Получаем итоги
        cursor.execute("""
            SELECT calories, proteins, fats, carbs
            FROM nutrition
            WHERE user_id = ? AND date = ?
        """, (user_id, today))
        totals = cursor.fetchone()

        # Получаем все блюда
        cursor.execute("""
            SELECT name, calories, proteins, fats, carbs
            FROM meals
            WHERE user_id = ? AND date = ?
        """, (user_id, today))
        meals = cursor.fetchall()

        return {
            'totals': totals,
            'meals': meals
        }
        
        
def add_meal(user_id, meal_name, calories, proteins, fats, carbs):
    checkIsTodayCreate(user_id)
    today = date.today().isoformat()

    with sqlite3.connect(file_db) as conn:
        cursor = conn.cursor()

        # Добавляем блюдо
        cursor.execute("""
            INSERT INTO meals (user_id, date, name, calories, proteins, fats, carbs)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, today, meal_name, calories, proteins, fats, carbs))

        # Обновляем суммарные значения в nutrition
        cursor.execute("""
            UPDATE nutrition
            SET 
                calories = calories + ?,
                proteins = proteins + ?,
                fats = fats + ?,
                carbs = carbs + ?
            WHERE user_id = ? AND date = ?
        """, (calories, proteins, fats, carbs, user_id, today))

        conn.commit()