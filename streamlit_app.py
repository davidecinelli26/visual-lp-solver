import streamlit as st

st.title("Risolutore di Programmazione Lineare")

num_vars = st.number_input("Numero di variabili", min_value=1, max_value=10, value=2)
num_constraints = st.number_input("Numero di vincoli", min_value=1, max_value=10, value=2)

st.write(f"Hai scelto {num_vars} variabili e {num_constraints} vincoli.")
