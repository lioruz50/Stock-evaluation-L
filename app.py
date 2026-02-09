import streamlit as st
import pandas as pd
import numpy as np

# הגדרות דף
st.set_page_config(page_title="מחשבון שווי שוק - אקסל", layout="wide")
st.title("📊 מודל הערכת שווי (לפי שווי שוק)")

# --- סרגל צד: נתוני בסיס מהאקסל ---
st.sidebar.header("נתוני בסיס (2026)")
company_name = st.sidebar.text_input("שם החברה", "Google")
base_rev = st.sidebar.number_input("הכנסות בסיס ($ מיליונים)", value=402000)
base_market_cap = st.sidebar.number_input("שווי שוק נוכחי ($ מיליונים)", value=4024000)
curr_price = st.sidebar.number_input("מחיר מניה נוכחי ($)", value=333.34)

st.sidebar.subheader("פרמטרים לצמיחה")
growth_rate = st.sidebar.slider("צמיחת הכנסות שנתית (%)", 0, 50, 12) / 100
net_margin = st.sidebar.slider("שולי רווח נקי (%)", 1, 50, 35) / 100
discount_rate = st.sidebar.slider("שיעור היוון (Discount Rate) (%)", 5, 20, 12) / 100

# חישוב יחס מניה לשווי שוק (כדי למצוא מחיר עתידי ללא הזנת כמות מניות)
# שווי שוק / מחיר מניה = כמות מניות "וירטואלית"
implied_shares = base_market_cap / curr_price

# --- חישוב תחזית 5 שנים ---
years = [2026, 2027, 2028, 2029, 2030]
rev_list = []
profit_list = []
temp_rev = base_rev

for year in years:
    rev_list.append(temp_rev)
    profit_list.append(temp_rev * net_margin)
    temp_rev *= (1 + growth_rate)

df_forecast = pd.DataFrame({
    "שנה": years,
    "הכנסות ($M)": [f"{r:,.0f}" for r in rev_list],
    "רווח נקי ($M)": [f"{p:,.0f}" for p in profit_list]
})

# --- ניתוח תרחישי מכפילים (בדיוק כמו באקסל) ---
pe_scenarios = [25, 30, 35]
scenario_results = []

final_profit_2030 = profit_list[-1]

for pe in pe_scenarios:
    # 1. שווי שוק עתידי = רווח 2030 * מכפיל
    future_mc = final_profit_2030 * pe
    # 2. מחיר מניה עתידי (לפי היחס הנוכחי)
    future_p = future_mc / implied_shares
    # 3. שווי הוגן להיום (היוון)
    fair_today = future_p / ((1 + discount_rate) ** 5)
    # 4. מרווח ביטחון (Margin of Safety)
    mos = ((fair_today / curr_price) - 1) * 100
    
    scenario_results.append({
        "מכפיל": pe,
        "שווי שוק 2030 ($M)": f"{future_mc:,.0f}",
        "מחיר מניה 2030": f"${future_p:.2f}",
        "שווי הוגן להיום": f"${fair_today:.2f}",
        "מרווח ביטחון": f"{mos:.1f}%"
    })

# --- תצוגה ---
st.subheader(f"📅 תחזית הכנסות ורווח: {company_name}")
st.table(df_forecast)

st.subheader("🎯 ניתוח שווי הוגן לפי תרחישים")
st.table(pd.DataFrame(scenario_results))

# סיכום צבעוני
avg_fair = np.mean([float(s["שווי הוגן להיום"].replace('$','')) for s in scenario_results])
upside = ((avg_fair / curr_price) - 1) * 100

if upside > 10:
    st.success(f"המניה נמצאת בתמחור חסר! פוטנציאל של {upside:.1f}% למחיר השווי ההוגן (${avg_fair:.2f})")
elif upside < -10:
    st.error(f"המניה נראית יקרה מדי. מחיר שוק גבוה מהשווי ההוגן (${avg_fair:.2f}) ב-{abs(upside):.1f}%")
else:
    st.warning(f"המניה מתומחרת סביב השווי ההוגן שלה (${avg_fair:.2f})")
