from flask import Flask , render_template, request, redirect
import sqlite3
app = Flask(__name__)
def init_db():
    conn = sqlite3.connect("database/fintrack.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS expenses(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        expense_name TEXT,
        amount REAL,
        category TEXT,
        date TEXT
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS BUDGET(
        id INTEGER PRIMARY KEY,
        amount REAL
    )
    """)
    conn.commit()
    conn.close()
init_db()
@app.route("/")
def home():
    return render_template("index.html")
@app.route("/add_expense", methods=["GET", "POST"])
def add_expense():
    if request.method == "POST":
        expense_name = request.form["expense_name"]
        amount = request.form["amount"]
        category = request.form["category"]
        date = request.form["date"]
        print("DATE RECIEVED:", date)
        conn = sqlite3.connect("database/fintrack.db")
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO expenses (expense_name, amount, category, date)
        VALUES(?, ?, ?, ?)
        """, (expense_name, amount, category, date))
        conn.commit()
        conn.close()
        return redirect("/expenses")
    return render_template("add_expense.html")
@app.route("/dashboard")
def dashboard():
    conn = sqlite3.connect("database/fintrack.db")
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(amount) FROM expenses")
    total = cursor.fetchone()[0]
    if total is None:
        total = 0
    cursor.execute("SELECT COUNT(*) FROM expenses")
    expense_count = cursor.fetchone()[0]
    if expense_count > 0:
        average = round(total / expense_count, 2)
    else:
        average = 0
    cursor.execute("SELECT amount FROM budget LIMIT 1")
    result = cursor.fetchone()
    if result:
        budget = result[0]
    else:
        budget = 0
    remaining = budget - total
    conn.close()
    return render_template(
        "dashboard.html",
        total=total,
        budget=budget,
        remaining=remaining,
        count=expense_count,
        average=average
    )
@app.route("/set_budget", methods=["GET", "POST"])
def set_budget():

    if request.method == "POST":

        budget = request.form["budget"]

        conn = sqlite3.connect("database/fintrack.db")
        cursor = conn.cursor()

        cursor.execute("DELETE FROM budget")

        cursor.execute(
            "INSERT INTO budget(id, amount) VALUES(1, ?)",
            (budget,)
        )

        conn.commit()
        conn.close()

        return redirect("/budget")

    return render_template("set_budget.html")
@app.route("/budget")
def budget():
    conn = sqlite3.connect("database/fintrack.db")
    cursor = conn.cursor()
    cursor.execute("SELECT amount FROM budget WHERE id=1")
    budget = cursor.fetchone()
    if budget:
        budget_amount = budget[0]
    else:
        budget_amount = 0
    cursor.execute("SELECT SUM(amount) FROM expenses")
    total = cursor.fetchone()[0]
    if total is None:
        total=0
    remaining = budget_amount - total
    print("Remaining =", remaining)
    conn.close()
    return render_template(
        "budget.html",
        budget=budget_amount,
        total=total,
        remaining=remaining
    )
@app.route("/expenses")
def expenses():
    conn = sqlite3.connect("database/fintrack.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM expenses ORDER BY id DESC")
    expenses = cursor.fetchall()
    conn.close()
    return render_template(
        "expense_history.html",
       expenses=expenses
    )
if __name__ == "__main__":
    app.run(debug=True)