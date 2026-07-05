# Banking System (OOP + Web Project)

A professional Banking System built in Python: an OOP core engine, a CLI, and a
Flask web application — all sharing the same business logic.

## Concepts Demonstrated
- **Abstraction** — `Account` is an abstract base class (`abc.ABC`)
- **Inheritance** — `SavingsAccount` and `CurrentAccount` extend `Account`
- **Polymorphism** — each subclass implements `withdraw()` differently
- **Encapsulation** — balance/account number are protected, exposed via `@property`
- **Custom Exceptions** — clean, specific error handling
- **Persistence** — accounts saved/loaded from `data/accounts.json`
- **Unit Testing** — `unittest` based test suite (11 tests)
- **Web layer** — Flask app with server-rendered HTML (Jinja2), reusing the
  exact same `bank` package as the CLI — no duplicated business logic
- **Security** — 4-digit transaction PIN, SHA-256 hashed (never stored in plaintext),
  required for withdrawals & transfers
- **KYC customer profile** — email, phone, address, date of birth, nominee
- **Analytics** — live doughnut chart (Chart.js) showing Savings vs Current split
- **Search** — filter accounts by name or account number from the dashboard
- **Branding config** — `bank/config.py` centralizes the bank's name, tagline,
  branch address and support contact, used everywhere via Flask's context processor

## File Structure
```
banking_system/
├── main.py                  # CLI entry point
├── app.py                   # Flask web app entry point
├── requirements.txt         # Python dependencies (Flask)
├── bank/                    # Core OOP business logic (used by both CLI & web)
│   ├── __init__.py
│   ├── account.py           # Account, SavingsAccount, CurrentAccount
│   ├── bank.py               # Bank manager class
│   ├── transaction.py        # Transaction ledger entries
│   ├── exceptions.py         # Custom exceptions
│   └── storage.py            # JSON persistence layer
├── templates/                # Jinja2 HTML templates
│   ├── base.html             # Shared layout, navbar, flash messages
│   ├── index.html            # Dashboard - list of accounts
│   ├── create_account.html   # New account form
│   ├── account_detail.html   # Statement + deposit/withdraw/transfer forms
│   └── 404.html
├── static/
│   ├── style.css             # Ledger-inspired styling
│   └── script.js             # Form UX (overdraft toggle, flash auto-hide)
├── data/
│   └── accounts.json         # Auto-created data file (shared by CLI & web)
├── tests/
│   └── test_account.py       # Unit tests
└── README.md
```

## How to Run

### Web App (recommended)
```bash
pip install -r requirements.txt
python3 app.py
```
Then open **http://localhost:5000** in your browser.

### CLI Version
```bash
python3 main.py
```

### Tests
```bash
python3 -m unittest discover tests -v
```

## Web App Routes
| Route | Method | Description |
|---|---|---|
| `/` | GET | Dashboard — all accounts + totals |
| `/create` | GET/POST | Create a new account |
| `/account/<acc_no>` | GET | Account detail + statement |
| `/account/<acc_no>/deposit` | POST | Deposit money |
| `/account/<acc_no>/withdraw` | POST | Withdraw money |
| `/account/<acc_no>/transfer` | POST | Transfer to another account |

## Example Usage (as a library)
```python
from bank import Bank

bank = Bank(name="My Bank")
acc = bank.create_account("Rahul Sharma", "savings", initial_deposit=5000)
bank.deposit(acc.account_number, 2000)
bank.withdraw(acc.account_number, 500)
acc.print_statement()
```

## Possible Extensions
- Add a `FixedDepositAccount` (locked balance, higher interest)
- Add password/PIN authentication per account
- Replace JSON storage with SQLite for a real database
- Add a Flask/FastAPI REST API layer on top of `Bank`
- Add a GUI using Tkinter or a web frontend
# banking-system
