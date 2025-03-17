import streamlit as st

def calculate_balances(expenses):
    """Calculate correct balances after expense splitting."""
    if not expenses:
        return {}

    paid_amounts = {}  # Tracks how much each person paid
    owed_amounts = {}  # Tracks how much each person should contribute

    for expense in expenses:
        payer = expense["Payer"]
        amount = expense["Expense"]
        participants = expense["Participants"]

        if not participants:
            continue  # Skip invalid expenses

        # ✅ Ensure payer is included in the split
        if payer not in participants:
            participants.append(payer)

        # Track the amount each person owes for this expense
        split_amount = amount / len(participants)

        for person in participants:
            owed_amounts[person] = owed_amounts.get(person, 0) + split_amount

        # Track how much the payer actually paid
        paid_amounts[payer] = paid_amounts.get(payer, 0) + amount

    # Compute final balances (Paid - Owed)
    balances = {}
    all_people = set(paid_amounts.keys()).union(set(owed_amounts.keys()))

    for person in all_people:
        total_paid = paid_amounts.get(person, 0)
        total_owed = owed_amounts.get(person, 0)
        balances[person] = round(total_paid - total_owed, 2)

    return balances

def main():
    st.set_page_config(page_title="Expense Splitter", page_icon="💸")
    st.title("💸 Expense Splitter")

    if "expenses" not in st.session_state:
        st.session_state.expenses = []

    st.subheader("📜 Current Expenses")

    if st.session_state.expenses:
        expense_data = []
        for expense in st.session_state.expenses:
            expense_data.append({
                "Payer": expense["Payer"],
                "Amount (₹)": expense["Expense"],
                "Split Between": ", ".join(expense["Participants"]),
                "Notes": expense["Notes"]
            })
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

    # Balance Calculation
    if st.session_state.expenses:
        st.subheader("💰 Who Owes Whom?")
        balances = calculate_balances(st.session_state.expenses)

        for person, balance in balances.items():
            if balance > 0:
                st.success(f"✅ **{person} is owed ₹{balance}**")
            elif balance < 0:
                st.error(f"❌ **{person} owes ₹{-balance}**")
            else:
                st.info(f"ℹ️ **{person} is settled up**")

if __name__ == "__main__":
    main()
