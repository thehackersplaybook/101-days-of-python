import streamlit as st
import math

st.set_page_config(page_title="Profesional Calculator", layout="centered", page_icon="🧮")

def calculate(operation, num1 ,num2=None):
    try:
        if operation == 'Addition':
            sign = '+'
            return num1+ num2, sign
        elif operation == 'Subtraction':
            sign = '-'
            return num1 - num2, sign
        elif operation == 'Multiplication':
            sign= '*'
            return num1 * num2, sign
        elif operation == 'Division':
            sign = "/"
            return num1 / num2 if num2 !=0 else 'Error: Division by zero', sign
        elif operation == 'Square Root':
            sign = '√'
            return math.sqrt(num1),sign
        elif operation == 'Power':
             sign = '^'
             return math.pow(num1, num2), sign
        elif operation == 'Logarithm':
             sign = 'log'
             return math.log(num1, num2) if num1 > 0 and num2 > 0 else 'Error: Invalid input', sign
        elif operation == 'Sine':
             sign = 'sin'
             return math.sin(math.radians(num1)), sign
        elif operation == 'Cosine':
             sign = 'cos'
             return math.cos(math.radians(num1)), sign
        elif operation == 'Tangent':
             sign = 'tan'
             return math.tan(math.radians(num1)), sign
        elif operation == 'Factorial':
             sign = '!'
             return math.factorial(num1) if num1 >= 0 and num1 == int(num1) else 'Error: Invalid input', sign
    except Exception as e:
            return f'Error: {e}'
    
    st.title("Professional Calculator")
    st.markdown("A sleek, user-friendly calculator app designed to perform everyday mathematical operations with precision and ease.")

tab1, tab2 = st.tabs(["Calculator", "History"])

if 'history' not in st.session_state:
         st.session_state.history = []
         

with tab1:
     st.header("Calculator")
     operation = st.selectbox(
        "Select Operation",
        [
            "Addition", "Subtraction", "Multiplication", "Division",
            "Square Root", "Power", "Factorial", "Logarithm", "Sine", "Cosine", "Tangent"
        ]
    )
     if operation in ['Square Root', 'Sine', 'Cosine', 'Tangent', 'Factorial']:
          num1 = st.number_input("Enter the number", value=0, key="single_num")
          num2 = None
     else:
          num1 = st.number_input("Enter the first number", value=0, key="num_1")
          num2=  st.number_input("Enter the second number", value=0, key="num_2")
     if(st.button("Calculate",key="basic_btn")):
          result, sign= calculate(operation, num1, num2)
          if isinstance(result, str) and result.startswith("Error"):
            st.error(result)
          else:
            if num2 is not None:
                st.success(f"Result: {result}")
                st.session_state.history.append(f"{operation} : {num1} {sign} {num2} = {result}")
            else:
                st.success(f"Result: {result}")
                st.session_state.history.append(f"{operation} : {sign}({num1}) = {result}")
                 

with tab2:
     st.header("History")
     if st.session_state.history:
          for entry in st.session_state.history:
               st.write(entry)
          if (st.button("Delete History", key="del_btn")):
               st.session_state.history = []
               st.success("History deleted")
     else:
          st.info("No calculations performed yet")
st.markdown(
        """
        <style>
        .bottom-right {
            position: fixed;
            bottom: 10px;
            right: 15px;
            font-size: 0.9em;
            color: gray;
        }
        </style>
        <div class="bottom-right">
            Made with ⚡ at 'The Hackers Playbook' ©. All rights reserved.
        </div>
        """,
        unsafe_allow_html=True
                )