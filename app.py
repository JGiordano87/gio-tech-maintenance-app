
from flask import Flask, render_template, request, redirect, url_for
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask_sqlalchemy import SQLAlchemy
import os

EMAIL_ADDRESS = "johnny.giordano87@gmail.com"
EMAIL_PASSWORD = "bxd..."

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from sqlalchemy import Column, Integer, String, Date, Text
from flask_sqlalchemy import SQLAlchemy

class Contract(db.Model):
    __tablename__ = 'contracts'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(50))
    start_date = db.Column(db.Date)
    due_months = db.Column(db.String(100))
    notes = db.Column(db.Text)
    renewal_date = db.Column(db.Date)

def send_email_reminder(to_email, subject, body):
    msg = MIMEMultipart()
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_email
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)

@app.route("/")
def index():
    contracts = Contract.query.with_entities(Contract.id, Contract.name).all()
    return render_template("index.html", contracts=contracts)

@app.route("/contract/<int:id>")
def view_contract(id):
    contract = Contract.query.get_or_404(id)
    return render_template("detail.html", contract=contract)

@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        data = request.form
        new_contract = Contract(
            name=data["name"],
            address=data["address"],
            email=data["email"],
            phone=data["phone"],
            start_date=data["start_date"],
            due_months=data["due_months"],
            notes=data["notes"],
            renewal_date=data["renewal_date"]
        )
        db.session.add(new_contract)
        db.session.commit()
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
    contract = Contract.query.get_or_404(id)
    db.session.delete(contract)
    db.session.commit()
    return redirect("/")

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    contract = Contract.query.get_or_404(id)
    if request.method == "POST":
        data = request.form
        contract.name = data["name"]
        contract.address = data["address"]
        contract.email = data["email"]
        contract.phone = data["phone"]
        contract.start_date = data["start_date"]
        contract.due_months = data["due_months"]
        contract.notes = data["notes"]
        contract.renewal_date = data["renewal_date"]
        db.session.commit()
        return redirect("/")
    return render_template("form.html", contract=contract)
    
    contract = con.execute("SELECT * FROM contracts WHERE id=?", (id,)).fetchone()
    return render_template("form.html", contract=contract)

from datetime import datetime

def check_and_send_reminders():
    current_month = datetime.now().strftime("%B")   # "April"
    current_month_number = datetime.now().strftime("%m")  # "04"

    contracts = Contract.query.all()

    for contract in contracts:
        name = contract.name
        notes = contract.notes
        due_months = contract.due_months
        renewal_date = contract.renewal_date

        # Service Reminder
        if due_months and current_month in due_months:
            send_email_reminder(
                to_email="johnny@giotechclimatesolutions.com",
                subject=f"HVAC Maintenance Due - {name}",
                body=f"Reminder: {name} is due for service this month.\n\nNotes: {notes}\nFilter Sizes or Details: {notes}"
            )

        # Contract Renewal Reminder
        if renewal_date:
            try:
                renewal_month = renewal_date.strftime("%m")
                if renewal_month == current_month_number:
                    send_email_reminder(
                        to_email="johnny@giotechclimatesolutions.com",
                        subject=f"Contract Renewal Reminder - {name}",
                        body=f"The service contract for {name} is set to renew this month.\n\nNotes: {notes}"
                    )
            except Exception as e:
                print(f"Error parsing renewal_date for {name}: {e}")


@app.route("/send-reminders")
def send_reminders():
    check_and_send_reminders()
    return "Reminders sent (if any due)!"

@app.route("/init-db")
def init_db():
    with app.app_context():
        db.create_all()
    return "Database initialized!"

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
