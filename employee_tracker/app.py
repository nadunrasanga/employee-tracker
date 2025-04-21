from flask import Flask, render_template, request, jsonify
import sqlite3, os

app = Flask(__name__)
DATABASE = 'db/availability.db'
DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
EMPLOYEES = ['Alice', 'Bob', 'Charlie']

def init_db():
    os.makedirs('db', exist_ok=True)
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS availability (
                    employee TEXT,
                    day TEXT,
                    status TEXT
                )''')
    for emp in EMPLOYEES:
        for day in DAYS:
            c.execute('INSERT OR IGNORE INTO availability VALUES (?, ?, ?)', (emp, day, 'OUT'))
    conn.commit()
    conn.close()

@app.route('/')
def index():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT * FROM availability')
    data = c.fetchall()
    conn.close()
    table = {emp: {} for emp in EMPLOYEES}
    for emp, day, status in data:
        table[emp][day] = status
    return render_template('index.html', table=table, days=DAYS)

@app.route('/toggle', methods=['POST'])
def toggle():
    emp = request.form['employee']
    day = request.form['day']
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT status FROM availability WHERE employee=? AND day=?', (emp, day))
    current = c.fetchone()[0]
    new_status = 'IN' if current == 'OUT' else 'OUT'
    c.execute('UPDATE availability SET status=? WHERE employee=? AND day=?', (new_status, emp, day))
    conn.commit()
    conn.close()
    return jsonify({'status': new_status})

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=10000)