
from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

EMAIL_ADDRESS = "johnny.giordano87@gmail.com"
EMAIL_PASSWORD = "bxde vovt hqkb aidx"

app = Flask(__name__)
DB = "contracts.db"

def send_email_reminder(to_email, subject, body):
    msg = MIMEMultipart()
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_email
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def index():
    con = get_db()
    contracts = con.execute("SELECT id, name FROM contracts").fetchall()
    return render_template("index.html", contracts=contracts)

@app.route("/contract/<int:id>")
def view_contract(id):
    con = get_db()
    contract = con.execute("SELECT * FROM contracts WHERE id=?", (id,)).fetchone()
    return render_template("detail.html", contract=contract)

@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        data = request.form
        con = get_db()
        con.execute("""INSERT INTO contracts (name, address, email, phone, start_date, due_months, notes, renewal_date)
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                      (data["name"], data["address"], data["email"], data["phone"],
                       data["start_date"], data["due_months"], data["notes"], data["renewal_date"]))
        con.commit()
        return redirect("/")
    return render_template("form.html")

@app.route("/test-email")
def test_email():
    send_email_reminder(
        to_email="johnny@giotechclimatesolutions.com",
        subject="HVAC Service Reminder",
        body="This is a test reminder from your Gio-Tech app!"
    )
    return "Test email sent!"


@app.route("/delete/<int:id>")
def delete(id):
    con = get_db()
    con.execute("DELETE FROM contracts WHERE id=?", (id,))
    con.commit()
    return redirect("/")

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    con = get_db()
    if request.method == "POST":
        data = request.form
        con.execute("""
            UPDATE contracts SET name=?, address=?, email=?, phone=?, start_date=?, due_months=?, notes=?, renewal_date=?
            WHERE id=?
        """, (
            data["name"], data["address"], data["email"], data["phone"],
            data["start_date"], data["due_months"], data["notes"], data["renewal_date"], id
        ))
        con.commit()
        return redirect("/")
    
    contract = con.execute("SELECT * FROM contracts WHERE id=?", (id,)).fetchone()
    return render_template("form.html", contract=contract)
from datetime import datetime

def check_and_send_reminders():
    con = get_db()
    current_month = datetime.now().strftime("%B")  # Correct format for "April"
    contracts = con.execute("SELECT * FROM contracts").fetchall()
    
    for contract in contracts:
        due_months = contract['due_months']
        if due_months and current_month in due_months:
            send_email_reminder(
                to_email="johnny@giotechclimatesolutions.com",
                subject="HVAC Maintenance Due - " + contract["name"],
                body=f"Reminder: {contract['name']} is due for service this month.\n\nNotes: {contract['notes']}\nFilter Sizes or Details: {contract['notes']}"
            )
@app.route("/send-reminders")
def send_reminders():
    check_and_send_reminders()
    return "Reminders sent (if any due)!"

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)