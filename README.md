# 🏋️ Titan Gym & Fitness Management System

A desktop management application built with **Python**, **Tkinter (ttk)**, and **MySQL / SQLite**. Designed with a modern dark theme inspired by Catppuccin Mocha, offering complete CRUD operations, real-time search filtering, membership status tracking, and automated validation.

---

## ✨ Features

- **Modern Dark UI**: Ergonomic dark aesthetic using Catppuccin Mocha design tokens with high-contrast inputs and reactive feedback.
- **Member Management (CRUD)**:
  - Add new members with instant field validation (phone formatting, email syntax, unique constraints).
  - Update membership details, active plans, and subscription statuses.
  - Delete members with confirmation safeguards.
- **Search & Quick Filtering**: Real-time filtering by Member ID, Full Name, Phone Number, or Membership Plan.
- **Flexible Database Engine**:
  - **MySQL (Production)**: Seamless connection with automatic table initialization via `schema.sql`.
  - **Local SQLite / Demo Fallback**: Works out-of-the-box even without a local MySQL service running.
- **Automated Verification**: Built-in test suite (`test_suite.py`) validating all database interactions and edge-case constraints.

---

## 📁 Project Structure

```text
gym_project/
├── app.py              # Main Tkinter graphical user interface application
├── db_helper.py        # Database manager with dual-mode (MySQL & SQLite fallback)
├── schema.sql          # MySQL database initialization script and seed records
├── test_suite.py       # Automated integration and CRUD test suite
├── requirements.txt    # Python package dependencies
├── run_app.bat         # Windows batch runner for one-click startup
├── .env.example        # Template for MySQL connection credentials
├── .gitignore          # Git exclusion rules
└── README.md           # Project documentation
```

---

## 🚀 Getting Started

### 1. Prerequisites
- **Python 3.10+** installed on your system.
- *(Optional)* **MySQL Server 8.0+** (if you want to use MySQL instead of the built-in local engine).

### 2. Clone the Repository
```bash
git clone https://github.com/<YOUR_USERNAME>/<YOUR_REPOSITORY>.git
cd <YOUR_REPOSITORY>
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. (Optional) Configure MySQL
If you are using MySQL:
1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
2. Update `.env` with your MySQL credentials:
   ```env
   MYSQL_HOST=127.0.0.1
   MYSQL_PORT=3306
   MYSQL_USER=root
   MYSQL_PASSWORD=your_password
   MYSQL_DATABASE=gym_db
   ```
3. Import the database schema:
   ```bash
   mysql -u root -p < schema.sql
   ```

*Note: If MySQL is not detected or credentials are not supplied, the app automatically runs in local storage mode so you can test immediately without any database setup.*

---

## 🖥️ Running the Application

### On Windows
Double-click `run_app.bat` or run:
```powershell
python app.py
```

### On macOS / Linux
```bash
python3 app.py
```

---

## 🧪 Running Tests

Verify all database logic, integrity rules, and search filters:
```bash
python test_suite.py
```

---

## 📜 License
Distributed under the MIT License. See `LICENSE` for more information.
