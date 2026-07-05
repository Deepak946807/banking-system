"""
Bank module: the central manager class that holds and operates on all accounts.
"""
import re
from .account import SavingsAccount, CurrentAccount
from .exceptions import (
    AccountNotFoundError, DuplicateAccountError, InvalidKYCError, DuplicateKYCError,
)
from .storage import Storage
from .config import BANK_NAME, BANK_SWIFT_PREFIX

PAN_REGEX = re.compile(r"^[A-Z]{5}[0-9]{4}[A-Z]$")


class Bank:
    def __init__(self, name=BANK_NAME, data_file="data/accounts.json"):
        self.name = name
        self.storage = Storage(data_file)
        self.accounts = self.storage.load()   # dict: account_number -> Account
        self._next_id = self._compute_next_id()

    def _compute_next_id(self):
        if not self.accounts:
            return 1001
        nums = [int(a.split("-")[-1]) for a in self.accounts if a.split("-")[-1].isdigit()]
        return max(nums, default=1000) + 1

    def _generate_account_number(self):
        """Generate a unique account number. Guaranteed unique even if the
        internal counter and the accounts on disk somehow drift apart."""
        acc_no = f"{BANK_SWIFT_PREFIX}-{self._next_id}"
        self._next_id += 1
        while acc_no in self.accounts:               # safety net against collisions
            acc_no = f"{BANK_SWIFT_PREFIX}-{self._next_id}"
            self._next_id += 1
        return acc_no

    # ---------- KYC (Aadhaar/PAN) helpers ----------
    @staticmethod
    def _normalize_aadhar(aadhar: str) -> str:
        return "".join(ch for ch in str(aadhar or "") if ch.isdigit())

    @staticmethod
    def _normalize_pan(pan: str) -> str:
        return str(pan or "").strip().upper()

    def _validate_kyc(self, aadhar: str, pan: str):
        """Validate Aadhaar/PAN format. Returns normalized (aadhar, pan)."""
        aadhar_n = self._normalize_aadhar(aadhar)
        pan_n = self._normalize_pan(pan)
        if len(aadhar_n) != 12:
            raise InvalidKYCError("Aadhaar number must be exactly 12 digits.")
        if not PAN_REGEX.match(pan_n):
            raise InvalidKYCError("PAN must be in the format ABCDE1234F (5 letters, 4 digits, 1 letter).")
        return aadhar_n, pan_n

    def find_by_kyc(self, aadhar: str = "", pan: str = ""):
        """Return all existing accounts that match this Aadhaar and/or PAN.
        Used both to block duplicate account creation and to power the
        'KYC Duplicate Check' box on the dashboard."""
        aadhar_n = self._normalize_aadhar(aadhar)
        pan_n = self._normalize_pan(pan)
        matches = []
        for acc in self.accounts.values():
            acc_aadhar = self._normalize_aadhar(acc.aadhar)
            acc_pan = self._normalize_pan(acc.pan)
            same_aadhar = bool(aadhar_n) and acc_aadhar == aadhar_n
            same_pan = bool(pan_n) and acc_pan == pan_n
            if same_aadhar or same_pan:
                matches.append(acc)
        return matches

    def create_account(self, owner_name: str, acc_type: str = "savings",
                        initial_deposit: float = 0.0, pin: str = "1234",
                        email: str = "", phone: str = "", address: str = "",
                        dob: str = "", nominee: str = "",
                        aadhar: str = "", pan: str = "", photo: str = "", **kwargs):
        # One person (identified by Aadhaar + PAN) can only hold ONE account
        # in this bank. This is what stops the "2 accounts, same name/pin"
        # problem: the check is keyed on the KYC identity, not on name/pin.
        aadhar_n, pan_n = self._validate_kyc(aadhar, pan)
        existing = self.find_by_kyc(aadhar_n, pan_n)
        if existing:
            dup = existing[0]
            raise DuplicateKYCError(dup.account_number, dup.owner_name)

        acc_no = self._generate_account_number()
        if acc_no in self.accounts:
            raise DuplicateAccountError(acc_no)

        common_kwargs = dict(
            email=email, phone=phone, address=address,
            dob=dob, nominee=nominee, pin=pin,
            aadhar=aadhar_n, pan=pan_n, photo=photo,
        )

        if acc_type.lower() == "savings":
            account = SavingsAccount(acc_no, owner_name, initial_deposit,
                                      interest_rate=kwargs.get("interest_rate", 0.04),
                                      **common_kwargs)
        elif acc_type.lower() == "current":
            account = CurrentAccount(acc_no, owner_name, initial_deposit,
                                      overdraft_limit=kwargs.get("overdraft_limit", 5000.0),
                                      **common_kwargs)
        else:
            raise ValueError("account type must be 'savings' or 'current'")

        self.accounts[acc_no] = account
        self.save()
        return account

    def get_account(self, account_number: str):
        if account_number not in self.accounts:
            raise AccountNotFoundError(account_number)
        return self.accounts[account_number]

    def authenticate(self, account_number: str, pin: str) -> bool:
        acc = self.get_account(account_number)
        return acc.verify_pin(pin)

    def deposit(self, account_number: str, amount: float):
        acc = self.get_account(account_number)
        acc.deposit(amount)
        self.save()

    def withdraw(self, account_number: str, amount: float, pin: str):
        acc = self.get_account(account_number)
        acc.require_pin(pin)
        acc.withdraw(amount)
        self.save()

    def transfer(self, from_acc: str, to_acc: str, amount: float, pin: str):
        sender = self.get_account(from_acc)
        receiver = self.get_account(to_acc)
        sender.require_pin(pin)
        sender.withdraw(amount, note=f"Transfer to {to_acc}")
        receiver.deposit(amount, note=f"Transfer from {from_acc}")
        self.save()

    def list_accounts(self):
        return list(self.accounts.values())

    def total_deposits(self):
        return sum(acc.balance for acc in self.accounts.values())

    def account_type_breakdown(self):
        breakdown = {}
        for acc in self.accounts.values():
            breakdown[acc.account_type()] = breakdown.get(acc.account_type(), 0) + 1
        return breakdown

    def save(self):
        self.storage.save(self.accounts)
