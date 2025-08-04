import streamlit as st

from lp_solver.model import Constraint, LinearProgram, Inequality

st.set_page_config(layout="wide")

st.title("Risolutore di Programmazione Lineare")

sense = st.selectbox(
    "Tipo di problema",
    ["max", "min"],
    format_func=lambda s: "Massimizza" if s == "max" else "Minimizza",
)

num_vars = st.number_input(
    "Numero di variabili (n)", min_value=1, max_value=10, value=2
)
num_constraints = st.number_input(
    "Numero di vincoli (m)", min_value=1, max_value=10, value=2
)


# Helper to parse floats
def _parse_float(value):
    if value is None or value == "":
        return 0.0
    try:
        return float(value)
    except ValueError:
        return None

# =======================
# Objective Function
# =======================
st.subheader("Funzione obiettivo")

row = st.columns(num_vars * 2 - 1)  # term + plus + term + plus ...

obj_inputs = []
for j in range(num_vars):
    with row[2*j]:
        ccol1, ccol2 = st.columns([1, 0.5])  # input + variable inline
        coeff = ccol1.text_input("", key=f"c_{j}", label_visibility="collapsed")
        ccol2.latex(f"x_{j+1}")
        obj_inputs.append(coeff)
    if j < num_vars - 1:
        row[2*j + 1].latex("+")


# =======================
# Constraints
# =======================
st.subheader("Vincoli")

constraint_rows = []
for i in range(num_constraints):
    row = st.columns(num_vars * 2 + 2)
    coeff_inputs = []
    for j in range(num_vars):
        with row[2 * j]:
            ccol1, ccol2 = st.columns([1, 0.5])  # coeff + variable side by side
            coeff = ccol1.text_input("", key=f"a_{i}_{j}", label_visibility="collapsed")
            ccol2.latex(f"x_{j + 1}")
            coeff_inputs.append(coeff)
        if j < num_vars - 1:
            row[2 * j + 1].latex("+")

    # inequality and RHS
    inequality = row[-2].selectbox(
        "tipo",
        [ineq.value for ineq in Inequality],
        key=f"ineq_{i}",
        label_visibility="collapsed"
    )
    rhs = row[-1].text_input("", key=f"b_{i}", label_visibility="collapsed")

    constraint_rows.append((coeff_inputs, inequality, rhs))

# =======================
# Build LP after validation
# =======================
if st.button("Crea modello"):
    objective = [_parse_float(v) for v in obj_inputs]
    if any(v is None for v in objective):
        st.error("Coefficienti della funzione obiettivo non validi.")
    else:
        constraints = []
        valid = True
        for coeff_inputs, inequality, rhs in constraint_rows:
            coeffs = [_parse_float(c) for c in coeff_inputs]
            b_val = _parse_float(rhs)
            if b_val is None or any(c is None for c in coeffs):
                valid = False
                break
            constraints.append(Constraint(coeffs, Inequality(inequality), b_val))

        if not valid:
            st.error("Valori non numerici nei vincoli.")
        else:
            lp = LinearProgram(objective=objective, constraints=constraints, sense=sense)
            st.success("Modello LP creato correttamente!")
            st.write("Vettore c:", lp.c_vector())
            st.write("Matrice A:", lp.A_matrix())
            st.write("Vettore b:", lp.b_vector())
            st.write("Tipi di vincolo:", lp.sense_vector())
