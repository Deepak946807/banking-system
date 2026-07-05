"""
Banking System - Main Entry Point (CLI)
A CLI-based application demonstrating a professional OOP banking system.
"""
import os
from bank import Bank, BankingError
from bank.config import BANK_NAME

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data", "accounts.json")


def print_menu():
    print(f"""
========== {BANK_NAME.upper()} ==========
1. Open Account
2. Deposit
3. Withdraw
4. Transfer
5. View Account / Statement
6. List All Accounts
7. Total Bank Deposits
8. Exit
=====================================""")


def main():
    bank = Bank(data_file=DATA_FILE)

    while True:
        print_menu()
        choice = input("Enter choice: ").strip()

        try:
            if choice == "1":
                name = input("Owner name: ").strip()
                acc_type = input("Account type (savings/current): ").strip().lower()
                deposit = float(input("Initial deposit: ") or 0)
                pin = input("Set a 4-digit PIN: ").strip()
                email = input("Email (optional): ").strip()
                phone = input("Phone (optional): ").strip()
                aadhar = input("Aadhaar Number (12 digits): ").strip()
                pan = input("PAN Number (e.g. ABCDE1234F): ").strip()
                acc = bank.create_account(name, acc_type, deposit, pin=pin, email=email, phone=phone,
                                           aadhar=aadhar, pan=pan)
                print(f"✅ Account created: {acc.account_number}")

            elif choice == "2":
                acc_no = input("Account number: ").strip()
                amount = float(input("Amount to deposit: "))
                bank.deposit(acc_no, amount)
                print("✅ Deposit successful.")

            elif choice == "3":
                acc_no = input("Account number: ").strip()
                amount = float(input("Amount to withdraw: "))
                pin = input("PIN: ").strip()
                bank.withdraw(acc_no, amount, pin)
                print("✅ Withdrawal successful.")

            elif choice == "4":
                from_acc = input("From account: ").strip()
                to_acc = input("To account: ").strip()
                amount = float(input("Amount: "))
                pin = input("PIN: ").strip()
                bank.transfer(from_acc, to_acc, amount, pin)
                print("✅ Transfer successful.")

            elif choice == "5":
                acc_no = input("Account number: ").strip()
                acc = bank.get_account(acc_no)
                acc.print_statement()

            elif choice == "6":
                for acc in bank.list_accounts():
                    print(acc)

            elif choice == "7":
                print(f"💰 Total deposits in bank: ₹{bank.total_deposits():.2f}")

            elif choice == "8":
                print("Thank you for banking with us. Goodbye!")
                break

            else:
                print("❌ Invalid choice, try again.")

        except BankingError as e:
            print(f"❌ Error: {e}")
        except ValueError:
            print("❌ Invalid input. Please enter numbers where required.")


if __name__ == "__main__":
    main()
