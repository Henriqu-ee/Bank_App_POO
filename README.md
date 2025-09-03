# Banking-Application  🏦


A complete banking system developed in Python with support for multiple features such as account creation, transfers, transaction history, loan management, bill payments, currency exchange, and more.

## 📂 Summary

- [Features](#features)
- [Prerequisites](#prerequisites)
- [How to Run](#how-to-run)
- [Project Structure](#project-structure)
- [Technologies Used](#technologies-used)
- [Possible Improvements](#possible-improvements)
- [License](#license)

## ⚙️ Prerequisites

- Python 3.8 or higher
- SQLite3 (standard in Python distributions)
- Standard libraries (`os`, `sqlite3`, `requests`, etc.)

---

## 💡 Features

### ✅ Account Management
- Create a new account
- Access an existing account
- Change password
- Close account

### 💸 Banking
- Deposit
- Withdraw
- Transfer between accounts
- Check balance and statement

### 🧑‍💼 Customer Support
- Frequently Asked Questions (FAQ) support system
- Virtual assistant with automatic responses
- User-friendly interface via terminal

### 💰 Savings and Investment Options
- Consult investment plans
- Calculate returns based on different rates
- Simulate returns with compound interest
- Option to invest directly through the system

---

## Project Structure

```bash
bank_app/
│
├── database/
│   ├── db_manager.py              # Manages database connections and basic operations
│   └── db_transaction_manager.py # Handles transaction-specific operations in the database
│
├── models/
│   ├── account.py     # Defines the Account class and related operations
│   ├── transaction.py # Defines the Transaction class and transaction logic
│   └── user.py        # Defines the User class and user-related operations
│
├── services/
│   ├── checkbook_service.py     # Service to request and manage checkbooks
│   ├── currency_service.py      # Handles currency conversion and rates
│   ├── loan_service.py          # Manages loan requests and processing
│   ├── notification_service.py  # Sends notifications to users
│   ├── payment_service.py       # Processes various types of payments
│   ├── support_service.py       # Provides customer support functionalities
│   └── transfer_service.py      # Handles account-to-account money transfers
│
├── utils/
│   └── currency_api.py # Connects to external API for real-time currency rates
│
├── db.sqlite        # SQLite database file storing all persistent data
└── main.py          # Main file to run the application
```

## 🧪 Technologies Used

- [x] Python 3.x

- [x] SQLite (or other relational database)

- [x] (Optional) Flask or Tkinter, if available

- [x] Exchange API (simulated or real)

## 🚀 How to Run

1. Make sure you have Python 3 installed.

2. Clone the repository or download the folder.

3. Navigate to the project folder:

```bash
cd bank_app
```

## 🔧 Possible Improvements

- Add a graphical user interface (GUI) using Tkinter or PyQt
- Implement unit tests with `unittest` or `pytest`
- Integrate real-time notifications via email or SMS
- Add user authentication with encryption
- Deploy the application using Flask for a web version
