"""
Banking System - Web Application (Flask)
Reuses the existing OOP `bank` package as the business logic layer.
"""
import os
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for, flash
from bank import Bank, BankingError
from bank.config import (
    BANK_NAME, BANK_TAGLINE, BANK_ESTD_YEAR, BANK_HEAD_OFFICE,
    BANK_SUPPORT_EMAIL, BANK_SUPPORT_PHONE,
)

app = Flask(__name__)
app.secret_key = "dev-secret-key-change-in-production"
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB max upload (photo)

# IMPORTANT: use an absolute path for the data file. A relative path like
# "data/accounts.json" resolves against whatever folder the server happens
# to be *launched* from — if you start the app from a different folder next
# time, Flask silently creates a brand-new empty data file and all existing
# accounts appear to "disappear" (deposits/withdrawals then fail with
# "Account not found"). Anchoring it to this file's own folder fixes that.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
bank = Bank(data_file=os.path.join(BASE_DIR, "data", "accounts.json"))

UPLOAD_FOLDER = os.path.join(app.static_folder, "uploads")
ALLOWED_PHOTO_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.context_processor
def inject_branding():
    """Makes bank branding available in every template automatically."""
    return dict(
        BANK_NAME=BANK_NAME,
        BANK_TAGLINE=BANK_TAGLINE,
        BANK_ESTD_YEAR=BANK_ESTD_YEAR,
        BANK_HEAD_OFFICE=BANK_HEAD_OFFICE,
        BANK_SUPPORT_EMAIL=BANK_SUPPORT_EMAIL,
        BANK_SUPPORT_PHONE=BANK_SUPPORT_PHONE,
    )


@app.route("/")
def index():
    accounts = bank.list_accounts()
    query = request.args.get("q", "").strip()
    if query:
        q_lower = query.lower()
        q_digits = "".join(ch for ch in query if ch.isdigit())   # for Aadhaar search
        q_upper = query.upper()                                   # for PAN search
        accounts = [
            a for a in accounts
            if q_lower in a.account_number.lower()
            or q_lower in a.owner_name.lower()
            or (len(q_digits) >= 4 and q_digits in (a.aadhar or ""))
            or (len(q_upper) >= 4 and q_upper in (a.pan or ""))
        ]

    # "KYC Duplicate Check" box: look up how many accounts already exist
    # for a given Aadhaar/PAN, without needing to create a new account.
    kyc_check = None
    check_aadhar = request.args.get("check_aadhar", "").strip()
    check_pan = request.args.get("check_pan", "").strip()
    if check_aadhar or check_pan:
        matches = bank.find_by_kyc(check_aadhar, check_pan)
        kyc_check = {"matches": matches, "aadhar": check_aadhar, "pan": check_pan}

    breakdown = bank.account_type_breakdown()
    return render_template(
        "index.html",
        accounts=accounts,
        total=bank.total_deposits(),
        breakdown=breakdown,
        query=query,
        kyc_check=kyc_check,
    )


@app.route("/create", methods=["GET", "POST"])
def create_account():
    if request.method == "POST":
        try:
            name = request.form["owner_name"].strip()
            acc_type = request.form["acc_type"]
            initial_deposit = float(request.form.get("initial_deposit") or 0)
            pin = request.form["pin"].strip()
            email = request.form.get("email", "").strip()
            phone = request.form.get("phone", "").strip()
            address = request.form.get("address", "").strip()
            dob = request.form.get("dob", "").strip()
            nominee = request.form.get("nominee", "").strip()
            aadhar = request.form.get("aadhar", "").strip()
            pan = request.form.get("pan", "").strip()

            extra = {}
            if acc_type == "current":
                extra["overdraft_limit"] = float(request.form.get("overdraft_limit") or 5000)

            acc = bank.create_account(
                name, acc_type, initial_deposit, pin=pin,
                email=email, phone=phone, address=address,
                dob=dob, nominee=nominee, aadhar=aadhar, pan=pan, **extra,
            )

            # Optional photo upload — saved only after the account (and its
            # unique account number) has been successfully created.
            photo_file = request.files.get("photo")
            if photo_file and photo_file.filename:
                ext = os.path.splitext(photo_file.filename)[1].lower()
                if ext in ALLOWED_PHOTO_EXTENSIONS:
                    filename = secure_filename(f"{acc.account_number}{ext}")
                    photo_file.save(os.path.join(UPLOAD_FOLDER, filename))
                    acc.photo = f"uploads/{filename}"
                    bank.save()
                else:
                    flash("Photo skipped: only JPG, PNG or WEBP images are allowed.", "error")

            flash(f"Account created successfully! Account Number: {acc.account_number}", "success")
            return redirect(url_for("account_detail", acc_no=acc.account_number))

        except (BankingError, ValueError) as e:
            flash(str(e), "error")
            return redirect(url_for("create_account"))

    return render_template("create_account.html")


@app.route("/account/<acc_no>")
def account_detail(acc_no):
    try:
        acc = bank.get_account(acc_no)
        return render_template("account_detail.html", account=acc)
    except BankingError as e:
        flash(str(e), "error")
        return redirect(url_for("index"))


@app.route("/account/<acc_no>/deposit", methods=["POST"])
def deposit(acc_no):
    try:
        amount = float(request.form["amount"])
        bank.deposit(acc_no, amount)
        flash(f"₹{amount:.2f} deposited successfully.", "success")
    except (BankingError, ValueError) as e:
        flash(str(e), "error")
    return redirect(url_for("account_detail", acc_no=acc_no))


@app.route("/account/<acc_no>/withdraw", methods=["POST"])
def withdraw(acc_no):
    try:
        amount = float(request.form["amount"])
        pin = request.form["pin"]
        bank.withdraw(acc_no, amount, pin)
        flash(f"₹{amount:.2f} withdrawn successfully.", "success")
    except (BankingError, ValueError) as e:
        flash(str(e), "error")
    return redirect(url_for("account_detail", acc_no=acc_no))


@app.route("/account/<acc_no>/transfer", methods=["POST"])
def transfer(acc_no):
    try:
        to_acc = request.form["to_account"].strip()
        amount = float(request.form["amount"])
        pin = request.form["pin"]
        bank.transfer(acc_no, to_acc, amount, pin)
        flash(f"₹{amount:.2f} transferred to {to_acc} successfully.", "success")
    except (BankingError, ValueError) as e:
        flash(str(e), "error")
    return redirect(url_for("account_detail", acc_no=acc_no))


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
