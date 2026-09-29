import pandas as pd
from sqlalchemy import text

from sqldb import engine

def get_expenses():
    query = """
        SELECT
            ExpenseID,
            ExpenseDate,
            Category,
            Description,
            Amount,
            PaymentMethod,
            CreatedDate,
            ModifiedDate
        FROM dbo.ExpenseTracker
        ORDER BY ExpenseDate DESC, ExpenseID DESC
    """

    with engine.connect() as conn:
        df = pd.read_sql(query, conn)

    return df

def add_expense(expense_date, category, description, amount, payment_method):
    query = text("""
        INSERT INTO dbo.ExpenseTracker
        (
            ExpenseDate,
            Category,
            Description,
            Amount,
            PaymentMethod
        )
        VALUES
        (
            :expense_date,
            :category,
            :description,
            :amount,
            :payment_method
        )
    """)

    with engine.begin() as conn:
        conn.execute(
            query,
            {
                "expense_date": expense_date,
                "category": category,
                "description": description,
                "amount": amount,
                "payment_method": payment_method
            }
        )

    return "Expense added successfully."

def update_expense(
    expense_id,
    expense_date,
    category,
    description,
    amount,
    payment_method
):
    query = text("""
        UPDATE dbo.ExpenseTracker
        SET
            ExpenseDate = :expense_date,
            Category = :category,
            Description = :description,
            Amount = :amount,
            PaymentMethod = :payment_method,
            ModifiedDate = SYSDATETIME()
        WHERE ExpenseID = :expense_id
    """)

    with engine.begin() as conn:
        result = conn.execute(
            query,
            {
                "expense_id": expense_id,
                "expense_date": expense_date,
                "category": category,
                "description": description,
                "amount": amount,
                "payment_method": payment_method
            }
        )

    if result.rowcount == 0:
        return "Expense not found."

    return "Expense updated successfully."

def delete_expense(expense_id):
    query = text("""
        DELETE FROM dbo.ExpenseTracker
        WHERE ExpenseID = :expense_id
    """)

    with engine.begin() as conn:
        result = conn.execute(
            query,
            {
                "expense_id": expense_id
            }
        )

    if result.rowcount == 0:
        return "Expense not found."

    return "Expense deleted successfully."            