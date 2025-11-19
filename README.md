# Fundraising Application Setup

To run this application, ensure you have the fund_raising schema and have some sample data in MySQL WorkBench (Discord)

## 1. Configure the Database Connection

Locate the `DB_CONFIG` dictionary in the `FundRaiseDAL/DAL_core.py` file and update the credentials to match your MySQL setup:

* **`user`**: Your MySQL username (e.g., `root`).
* **`password`**: Your MySQL password.
* **`database`**: The name of the MySQL database (`fundraising_db`).

## 2. Run the Application

Execute the main file from your project's root directory:

```bash
python .\main.py
