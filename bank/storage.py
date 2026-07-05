"""
Storage module: handles saving/loading bank data to/from a JSON file.
Keeping persistence separate from business logic = clean architecture.
"""
import json
import os
from .account import SavingsAccount, CurrentAccount
from .transaction import Transaction


class Storage:
    def __init__(self, filepath="data/accounts.json"):
        self.filepath = filepath
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)

    def save(self, accounts: dict):
        data = {acc_no: acc.to_dict() for acc_no, acc in accounts.items()}
        with open(self.filepath, "w") as f:
            json.dump(data, f, indent=4)

    def load(self) -> dict:
        if not os.path.exists(self.filepath):
            return {}

        with open(self.filepath, "r") as f:
            raw = json.load(f)

        accounts = {}
        for acc_no, info in raw.items():
            kwargs = dict(
                email=info.get("email", ""),
                phone=info.get("phone", ""),
                address=info.get("address", ""),
                dob=info.get("dob", ""),
                nominee=info.get("nominee", ""),
                aadhar=info.get("aadhar", ""),
                pan=info.get("pan", ""),
                photo=info.get("photo", ""),
                opened_on=info.get("opened_on"),
            )
            if info["account_type"] == "Savings":
                acc = SavingsAccount(info["account_number"], info["owner_name"], info["balance"], **kwargs)
            else:
                acc = CurrentAccount(info["account_number"], info["owner_name"], info["balance"], **kwargs)

            # Restore the original PIN hash directly (avoids re-validating a plaintext PIN)
            if info.get("pin_hash"):
                acc._pin_hash = info["pin_hash"]

            acc._transactions = [Transaction.from_dict(t) for t in info.get("transactions", [])]
            accounts[acc_no] = acc

        return accounts
