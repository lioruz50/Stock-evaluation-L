import streamlit as st
import pandas as pd
import numpy as np

# הגדרות דף
st.set_page_config(page_title="מחשבון הערכת שווי DCF", layout="wide")
st.title("📊 מודל הערכת שווי מניות (תחזית 5 שנים)")

# --- סרגל צד להזנת נתונים ---
st.sidebar.header("נתוני בסיס - Google / כללי")
company_name = st.sidebar.text_input("שם החברה", "Google")
base_revenue = st.sidebar.number_input("הכנסות בסיס (2026) [$ מיליונים]", value=402000)
growth_rate = st.sidebar.slider("צמיחת הכנסות שנתית [%]", 0, 50, 12) / 100
net_margin = st.sidebar.slider("שולי רווח נקי [%]", 1, 50, 35) / 100
discount_rate = st.sidebar.slider("שיעור היוון (Discount Rate) [%]", 5, 20, 12) / 100
current_price = st.sidebar.number_input("מחיר מניה נוכחי [$]", value=333.34)
shares_outstanding = st.sidebar.number_input("שווי שוק נוכחי [מיליוני $]", value=4024000) / current_price # חישוב כמות מניות

st.sidebar.subheader("תרחישי מכפיל רווח (P/E)")
pe_low = st.sidebar.number_input("מכפיל נמוך", value=25)
pe_med = st.sidebar.number_input("מכפיל ממוצע", value=30)
pe_high = st.sidebar.number_input("מכפיל גבוה", value=35)

# --- חישוב תחזית רב-שנתית ---
years = [2026, 2027, 2028, 2029, 2030, "2030 (סוף שנה)"]
projections = []
rev = base_revenue

for i in range(5):
    profit = rev * net_margin
    projections.append({
        "שנה": 2026 + i,
        "הכנסות ($M)": round(rev),
        "שולי רווח": f"{net_margin*100}%",
        "רווח נקי ($M)": round(profit)
    })
    rev *= (1 + growth_rate)

# נתוני שנה אחרונה (טרמינלית)
final_profit = projections[-1]["רווח נקי ($M)"]

# --- חישוב תרחישי שווי ---
scenarios = []
for pe in [pe_low, pe_med, pe_high]:
    future_market_cap = final_profit * pe
    future_price = future_market_cap / shares_outstanding
    # היוון להיום: PV = FV / (1 + r)^n
    fair_price_today = future_price / ((1 + discount_rate) ** 5)
    margin_of_safety = ((fair_price_today / current_price) - 1) * 100
    
    scenarios.append({
        "תרחיש מכפיל": pe,
        "שווי שוק עתידי ($M)": f"{future_market_cap:,.0f}",
        "מחיר מניה 2030": f"${future_price:.2f}",
        "שווי הוגן להיום": f"${fair_price_today:.2f}",
        "מרווח ביטחון / פוטנציאל": f"{margin_of_safety:.1f}%"
    })

# --- הצגת הנתונים ---
st.subheader(f"📅 תחזית צמיחה עבור {company_name}")
st.table(pd.DataFrame(projections).set_index("שנה"))

st.subheader("🎯 ניתוח שווי הוגן (לפי תרחישי מכפילים)")
st.table(pd.DataFrame(scenarios))

# --- סיכום ויזואלי ---
avg_fair_price = np.mean([float(s["שווי הוגן להיום"].replace('$','')) for s in scenarios])
st.info(f"💡 **סיכום:** השווי ההוגן הממוצע לפי המודל הוא **${avg_fair_price:.2f}**. בהשוואה למחיר השוק (${current_price}), זה מייצג פוטנציאל של **{((avg_fair_price/current_price)-1)*100:.1f}%**.")
