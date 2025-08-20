import sqlite3

DB_PATH = "database/carwash.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

# ---------------- Car Wash ----------------
def add_car_sale(date, car_type, price, payment_method):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO car_wash_sales (date, car_type, price, payment_method) VALUES (?,?,?,?)",
                (date, car_type, price, payment_method))
    conn.commit()
    conn.close()
def add_car_sale(date, car_type, plate_number, price, payment_method, payment_status):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""INSERT INTO car_wash_sales 
                (date, car_type, plate_number, price, payment_method, payment_status) 
                VALUES (?,?,?,?,?,?)""",
                (date, car_type, plate_number, price, payment_method, payment_status))
    conn.commit()
    conn.close()
def get_all_car_sales():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM car_wash_sales")
    rows = cur.fetchall()
    conn.close()
    return rows

def update_car_payment_status(sale_id, new_status="Paid"):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE car_wash_sales SET payment_status=? WHERE id=?", (new_status, sale_id))
    conn.commit()
    conn.close()

# ---------------- Drinks ----------------
def add_drink_sale(date, drink_name, qty, unit_price, total, payment_method):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""INSERT INTO drinks_sales 
                (date, drink_name, quantity, unit_price, total_price, payment_method) 
                VALUES (?,?,?,?,?,?)""",
                (date, drink_name, qty, unit_price, total, payment_method))
    conn.commit()
    conn.close()

def get_all_drink_sales():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM drinks_sales")
    rows = cur.fetchall()
    conn.close()
    return rows
