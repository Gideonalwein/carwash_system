import sqlite3

def init_db():
    conn = sqlite3.connect("database/carwash.db")
    cur = conn.cursor()
 
    cur.execute("""CREATE TABLE IF NOT EXISTS car_wash_sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                car_type TEXT,
                plate_number TEXT,
                price REAL,
                payment_method TEXT,
                payment_status TEXT)""")


    
    cur.execute("""CREATE TABLE IF NOT EXISTS drinks_sales (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT,
                    drink_name TEXT,
                    quantity INTEGER,
                    unit_price REAL,
                    total_price REAL,
                    payment_method TEXT)""")
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
