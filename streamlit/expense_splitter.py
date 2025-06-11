import streamlit as st
import plotly.express as px
from typing import List, Dict

def process_expenses(expenses: List[Dict[str, any]]) -> Dict[str, float]:
    paid_amounts, owed_amounts = {}, {}
    
    for expense in expenses:
        payer, amount, participants = expense["Payer"], expense["Expense"], expense["Participants"]
        
        if not participants:
            continue
        
        if payer in participants:
            participants.remove(payer)
        
        split_amount = amount / (len(participants) + 1)
        
        for person in participants:
            owed_amounts[person] = owed_amounts.get(person, 0) + split_amount
        
        paid_amounts[payer] = paid_amounts.get(payer, 0) + amount
    
    return update_balances(paid_amounts, owed_amounts)

def update_balances(paid_amounts: Dict[str, float], owed_amounts: Dict[str, float]) -> Dict[str, float]:
    balances = {}
    all_people = set(paid_amounts.keys()).union(set(owed_amounts.keys()))
    
    for person in all_people:
        total_paid = paid_amounts.get(person, 0)
        total_owed = owed_amounts.get(person, 0)
        balances[person] = round(total_paid - total_owed, 2)
    
    return balances

st.set_page_config(page_title="Expense Splitter", page_icon="💸", layout="wide")

st.markdown("<h1 style='text-align: center;'>💸 Expense Splitter</h1>", unsafe_allow_html=True)

if "expenses" not in st.session_state:
    st.session_state.expenses = []

if "success_msg" in st.session_state:
    st.toast(st.session_state.success_msg)
    del st.session_state.success_msg 

tab1, tab2 = st.tabs(["➕ Add Expense", "📜 Expense Summary"])

with tab1:
    st.subheader("➕ Add an Expense")
    
    with st.form("expense_form"):
        col1, col2 = st.columns(2)
        with col1:
            expense = st.number_input("Amount Paid (₹)", min_value=0.0, format="%.f")
            payer = st.text_input("Paid By")
        with col2:
            participants = st.text_input("Participants (comma-separated)")
            notes = st.text_area("Notes (Optional)")

        submit = st.form_submit_button("💾 Add Expense")

        if submit:
            if expense > 0 and payer and participants:
                participants_list = [p.strip() for p in participants.split(",")]
                new_expense = {"Expense": float(expense), "Payer": payer, "Participants": participants_list, "Notes": notes}
                st.session_state.expenses.append(new_expense)
                st.session_state.success_msg = "✅ Expense added successfully!"
                st.rerun()
            else:
                st.toast("Please fill all the fields.", icon="❌")

with tab2:
    st.subheader("📊 Overview")
    
    if st.session_state.expenses:
        expense_data = [
            {"Payer": exp["Payer"], "Amount (₹)": exp["Expense"], "Split Between": ", ".join(exp["Participants"]), "Notes": exp["Notes"]}
            for exp in st.session_state.expenses
        ]
        st.table(expense_data)

        balances = process_expenses(st.session_state.expenses)

        st.subheader("💰 Who Owes Whom?")
        for person, balance in balances.items():
            if balance > 0:
                st.success(f"✅ **{person} is owed ₹{balance}**")
            elif balance < 0:
                st.error(f"❌ **{person} owes ₹{-balance}**")
            else:
                st.info(f"ℹ️ **{person} is settled up**")

        fig = px.pie(
            names=balances.keys(),
            values=[abs(b) for b in balances.values()],
            title="Expense Distribution",
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No expenses added yet.")

    if st.session_state.expenses:
        if st.button("🗑️ Clear All Expenses"):
            st.session_state.expenses = []
            st.session_state.success_msg = "✅ All expenses cleared!"
            st.rerun()