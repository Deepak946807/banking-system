"""
Account module: demonstrates Abstraction, Encapsulation, Inheritance & Polymorphism.
Now includes KYC-style customer details and PIN-based transaction security.
"""
import hashlib
from abc import ABC, abstractmethod
from datetime import datetime
from .transaction import Transaction
from .exceptions import (
    InsufficientFundsError,
    InvalidAmountError,
    OverdraftLimitExceededError,
    AuthenticationError,
    WeakPinError,
)


class Account(ABC):
    """
    Abstract base class for all account types.
    Cannot be instantiated directly - forces subclasses to define account behavior.
    """

    def __init__(self, account_number: str, owner_name: str, balance: float = 0.0,
                 email: str = "", phone: str = "", address: str = "",
                 dob: str = "", nominee: str = "", pin: str = "1234",
                 aadhar: str = "", pan: str = "", photo: str = "",
                 opened_on: str = None):
        self._account_number = account_number      # Encapsulation: protected attrs
        self._owner_name = owner_name
        self._balance = float(balance)
        self._transactions: list[Transaction] = []

        # KYC / customer details
        self.email = email
        self.phone = phone
        self.address = address
        self.dob = dob
        self.nominee = nominee
        self.aadhar = aadhar          # 12-digit Aadhaar number (digits only, normalized by Bank)
        self.pan = pan                # 10-char PAN (uppercase, normalized by Bank)
        self.photo = photo            # relative path under /static, e.g. "uploads/UNTY-1001.jpg"
        self.opened_on = opened_on or datetime.now().strftime("%Y-%m-%d")

        # Security
        self._pin_hash = None
        self.set_pin(pin)

    # ---------- Encapsulated read-only properties ----------
    @property
    def account_number(self):
        return self._account_number

    @property
    def owner_name(self):
        return self._owner_name

    @property
    def balance(self):
        return self._balance

    @property
    def transactions(self):
        return list(self._transactions)   # return a copy, protect internal list

    # ---------- Security ----------
    @staticmethod
    def _hash_pin(pin: str) -> str:
        return hashlib.sha256(pin.encode()).hexdigest()

    def set_pin(self, pin: str):
        pin = str(pin).strip()
        if not (pin.isdigit() and len(pin) == 4):
            raise WeakPinError()
        self._pin_hash = self._hash_pin(pin)

    def verify_pin(self, pin: str) -> bool:
        return self._pin_hash == self._hash_pin(str(pin).strip())

    def require_pin(self, pin: str):
        """Raise AuthenticationError if the given PIN is wrong."""
        if not self.verify_pin(pin):
            raise AuthenticationError()

    # ---------- Masked KYC display helpers (never show full Aadhaar/PAN in UI) ----------
    @property
    def masked_aadhar(self):
        a = "".join(ch for ch in (self.aadhar or "") if ch.isdigit())
        return f"XXXX-XXXX-{a[-4:]}" if len(a) == 12 else (a or "—")

    @property
    def masked_pan(self):
        p = (self.pan or "").strip().upper()
        return f"{p[:2]}XXXXX{p[-1:]}" if len(p) == 10 else (p or "—")

    # ---------- Common operations ----------
    def deposit(self, amount: float, note: str = ""):
        if amount <= 0:
            raise InvalidAmountError(amount)
        self._balance += amount
        self._transactions.append(Transaction("DEPOSIT", amount, self._balance, note))

    @abstractmethod
    def withdraw(self, amount: float, note: str = ""):
        """Each account type implements its own withdrawal rules (Polymorphism)."""
        raise NotImplementedError

    @abstractmethod
    def account_type(self) -> str:
        """Returns a human-readable account type name."""
        raise NotImplementedError

    def print_statement(self):
        print(f"\n--- Statement for {self._account_number} ({self._owner_name}) ---")
        if not self._transactions:
            print("No transactions yet.")
        for txn in self._transactions:
            print(txn)
        print(f"Current Balance: ₹{self._balance:.2f}\n")

    def to_dict(self) -> dict:
        return {
            "account_number": self._account_number,
            "owner_name": self._owner_name,
            "balance": self._balance,
            "account_type": self.account_type(),
            "email": self.email,
            "phone": self.phone,
            "address": self.address,
            "dob": self.dob,
            "nominee": self.nominee,
            "aadhar": self.aadhar,
            "pan": self.pan,
            "photo": self.photo,
            "opened_on": self.opened_on,
            "pin_hash": self._pin_hash,
            "transactions": [t.to_dict() for t in self._transactions],
        }

    def __str__(self):
        return f"{self.account_type()} | {self._account_number} | {self._owner_name} | ₹{self._balance:.2f}"


class SavingsAccount(Account):
    """Savings account: no overdraft allowed, earns interest."""

    def __init__(self, account_number, owner_name, balance=0.0, interest_rate=0.04, **kwargs):
        super().__init__(account_number, owner_name, balance, **kwargs)
        self.interest_rate = interest_rate

    def withdraw(self, amount: float, note: str = ""):
        if amount <= 0:
            raise InvalidAmountError(amount)
        if amount > self._balance:
            raise InsufficientFundsError(self._balance, amount)
        self._balance -= amount
        self._transactions.append(Transaction("WITHDRAW", amount, self._balance, note))

    def apply_interest(self):
        interest = self._balance * self.interest_rate
        self.deposit(interest, note="Interest credited")
        return interest

    def account_type(self) -> str:
        return "Savings"


class CurrentAccount(Account):
    """Current account: allows overdraft up to a limit, no interest."""

    def __init__(self, account_number, owner_name, balance=0.0, overdraft_limit=5000.0, **kwargs):
        super().__init__(account_number, owner_name, balance, **kwargs)
        self.overdraft_limit = overdraft_limit

    def withdraw(self, amount: float, note: str = ""):
        if amount <= 0:
            raise InvalidAmountError(amount)
        available = self._balance + self.overdraft_limit
        if amount > available:
            raise OverdraftLimitExceededError(self.overdraft_limit)
        self._balance -= amount
        self._transactions.append(Transaction("WITHDRAW", amount, self._balance, note))

    def account_type(self) -> str:
        return "Current"
