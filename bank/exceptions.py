"""
Custom exceptions for the Banking System.
Using specific exceptions instead of generic ones makes error handling
clearer and easier to debug in a real-world application.
"""


class BankingError(Exception):
    """Base exception for all banking-related errors."""
    pass


class InsufficientFundsError(BankingError):
    """Raised when a withdrawal/transfer exceeds available balance."""
    def __init__(self, balance, amount):
        message = f"Insufficient funds: balance is {balance}, tried to withdraw {amount}"
        super().__init__(message)


class InvalidAmountError(BankingError):
    """Raised when a deposit/withdrawal amount is invalid (zero/negative)."""
    def __init__(self, amount):
        super().__init__(f"Invalid amount: {amount}. Amount must be greater than 0.")


class AccountNotFoundError(BankingError):
    """Raised when an account number does not exist in the bank."""
    def __init__(self, account_number):
        super().__init__(f"Account '{account_number}' not found.")


class DuplicateAccountError(BankingError):
    """Raised when trying to create an account that already exists."""
    def __init__(self, account_number):
        super().__init__(f"Account '{account_number}' already exists.")


class OverdraftLimitExceededError(BankingError):
    """Raised when a CurrentAccount withdrawal exceeds its overdraft limit."""
    def __init__(self, limit):
        super().__init__(f"Withdrawal exceeds overdraft limit of {limit}.")


class AuthenticationError(BankingError):
    """Raised when a PIN does not match for an account."""
    def __init__(self):
        super().__init__("Incorrect PIN. Transaction denied.")


class WeakPinError(BankingError):
    """Raised when a PIN doesn't meet the minimum security format (4 digits)."""
    def __init__(self):
        super().__init__("PIN must be exactly 4 digits.")


class InvalidKYCError(BankingError):
    """Raised when Aadhaar or PAN fails basic format validation."""
    def __init__(self, message):
        super().__init__(message)


class DuplicateKYCError(BankingError):
    """Raised when the same Aadhaar/PAN is already linked to an existing account.
    One person (identified by Aadhaar + PAN) can hold only one account in this bank."""
    def __init__(self, existing_account_number, existing_owner_name=""):
        who = f" ({existing_owner_name})" if existing_owner_name else ""
        super().__init__(
            f"An account already exists with this Aadhaar/PAN: "
            f"{existing_account_number}{who}. One person can open only one account per bank."
        )
        self.existing_account_number = existing_account_number
        self.existing_owner_name = existing_owner_name
