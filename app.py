import streamlit as st
import pandas as pd

# פונקציה לבדיקת סיסמה
def check_password():
def password_entered():
if st.session_state["password"] == "1234":
st.session_state["password_correct"] = True
del st.session_state["password"]
else:
st.session_state["password_correct"] = False

if "password_correct" not in st.session_state:
st.text_input("אנא הזן סיסמה לגישה למערכת:", type="password", on_change=password_entered, key="password")
return False
elif not st.session_state["password_correct"]:
st.text_input("סיסמה שגויה. נסה שוב:", type="password", on_change=password_entered, key="password")
return False
return True

if check_password():
st.set_page_config(page_title="דירוג מניות 2026", layout="wide")
st.title("📋 טבלת כדאיות השקעה - פברואר 2026")

all_companies = {
"Meta (META)": {"price": 647.63, "growth": 0.16, "margin": 0.34, "pe": 26},
"Amazon (AMZN)": {"price": 204.03, "growth": 0.14, "margin": 0.12, "pe": 40},
"Microsoft (MSFT)": {"price": 394.63, "growth": 0.13, "margin": 0.36, "pe": 32},
"Salesforce (CRM)": {"price": 191.35, "growth": 0.10, "margin": 0.34, "pe": 27},
"Tesla (TSLA)": {"price": 405.93, "growth": 0.18, "margin": 0.15, "pe": 50},
"AMD": {"price": 203.87, "growth": 0.25, "margin": 0.22, "pe": 35},
"Zeta Global (ZETA)": {"price": 18.68, "growth": 0.34, "margin": 0.15, "pe": 30},
"Nu Holdings (NU)": {"price": 18.16, "growth": 0.40, "margin": 0.20, "pe": 28},
"Ouster (OUST)": {"price": 17.30, "growth": 0.35, "margin": 0.15, "pe": 25}
}

results = []
for name, d in all_companies.items():
# נוסחת שווי הוגן ל-5 שנים (מהוון ב-12%)
fair_price = d["price"] * ((1 + d["growth"])**5) * (d["pe"] / 30) / ((1 + 0.12)**5)
upside = ((fair_price / d["price"]) - 1) * 100
score = "⭐⭐⭐⭐⭐" if upside > 30 else "⭐⭐⭐⭐" if upside > 15 else "⭐⭐⭐"
results.append({"חברה": name, "מחיר": f"${d['price']:.2f}", "פוטנציאל": f"{upside:.1f}%", "דירוג": score})

st.table(pd.DataFrame(results))
