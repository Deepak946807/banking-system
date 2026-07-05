"""
Transaction module: represents a single ledger entry for an account.
"""
from datetime import datetime


class Transaction:
    """Represents a single financial transaction (deposit/withdraw/transfer)."""

    def __init__(self, txn_type: str, amount: float, balance_after: float, note: str = ""):
        self.txn_type = txn_type          # "DEPOSIT", "WITHDRAW", "TRANSFER_IN", "TRANSFER_OUT"
        self.amount = amount
        self.balance_after = balance_after
        self.note = note
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self) -> dict:
        """Convert transaction to a dictionary (for JSON storage)."""
        return {
            "type": self.txn_type,
            "amount": self.amount,
            "balance_after": self.balance_after,
            "note": self.note,
            "timestamp": self.timestamp,
        }

    @staticmethod
    def from_dict(data: dict) -> "Transaction":
        """Rebuild a Transaction object from a dictionary."""
        txn = Transaction(data["type"], data["amount"], data["balance_after"], data.get("note", ""))
        txn.timestamp = data["timestamp"]
        return txn

    def __str__(self):
        return f"[{self.timestamp}] {self.txn_type:<12} ₹{self.amount:>10.2f}  | Balance: ₹{self.balance_after:.2f}  {self.note}"
