import streamlit as st
from typing import List, Dict

def process_expenses(expenses: List[Dict[str, any]]) -> Dict[str, float]:
    """
    Processes a list of expenses and calculates how much each participant owes.

    Args:
        expenses (List[Dict[str, any]]): List of expense dictionaries containing Payer, Expense, and Participants.

    Returns:
        Dict[str, float]: Dictionary mapping each person to their owed amount.
    """

    paid_amounts = {}
    owed_amounts = {}

    for expense in expenses:
        payer = expense["Payer"]
        amount = expense["Expense"]
        participants = expense["Participants"]

        if not participants:
            continue  # Skip invalid expenses

        if payer not in participants:
            participants.append(payer)

        split_amount = amount / len(participants)

        for person in participants:
            owed_amounts[person] = owed_amounts.get(person, 0) + split_amount

        paid_amounts[payer] = paid_amounts.get(payer, 0) + amount
    
    return update_balances(paid_amounts, owed_amounts)

def update_balances(paid_amounts: Dict[str, float], owed_amounts: Dict[str, float]) -> Dict[str, float]:
    """
    Computes the final balance for each person.

    Args:
        paid_amounts (Dict[str, float]): Dictionary tracking how much each person paid.
        owed_amounts (Dict[str, float]): Dictionary tracking how much each person owes.

    Returns:
        Dict[str, float]: Final balances after accounting for payments and owed amounts.
    """
    
    balances = {}
    all_people = set(paid_amounts.keys()).union(set(owed_amounts.keys()))

    for person in all_people:
        total_paid = paid_amounts.get(person, 0)
        total_owed = owed_amounts.get(person, 0)
        balances[person] = round(total_paid - total_owed, 2)
    
    return balances

def main():
    """Streamlit app for managing and calculating shared expenses."""
    st.set_page_config(page_title="Expense Splitter", page_icon="💸")
    st.title("💸 Expense Splitter")

    if "expenses" not in st.session_state:
        st.session_state.expenses = []

    st.subheader("📜 Current Expenses")

    if st.session_state.expenses:
        expense_data = [
            {
                "Payer": expense["Payer"],
                "Amount (₹)": expense["Expense"],
                "Split Between": ", ".join(expense["Participants"]),
                "Notes": expense["Notes"]
            }
            for expense in st.session_state.expenses
        ]
        st.table(expense_data)
    else:
        st.write("No expenses added yet.")

    with st.sidebar.form("Expenses Form"):
        st.write("➕ Add an expense:")
        expense = st.number_input("Amount Paid (₹)", min_value=0.0, format="%.2f")
        payer = st.text_input("Paid By")
        participants = st.text_input("Participants (comma-separated)")
        notes = st.text_area("Notes")
        submit = st.form_submit_button("Add Expense")

        if submit and expense > 0 and payer and participants:
            participants_list = [p.strip() for p in participants.split(",")]
            new_expense = {
                "Expense": float(expense),  
                "Payer": payer,
                "Participants": participants_list,
                "Notes": notes,
            }
            st.session_state.expenses.append(new_expense)
            st.rerun()

    if st.session_state.expenses:
        st.subheader("💰 Who Owes Whom?")
        balances = process_expenses(st.session_state.expenses)

        for person, balance in balances.items():
            if balance > 0:
                st.success(f"✅ **{person} is owed ₹{balance}**")
            elif balance < 0:
                st.error(f"❌ **{person} owes ₹{-balance}**")
            else:
                st.info(f"ℹ️ **{person} is settled up**")

if __name__ == "__main__":
    main()
