import streamlit as st
import pandas as pd

# הגדרות דף
st.set_page_config(page_title="דירוג מניות 2026", layout="wide")
st.title("📋 מחשבון כדאיות השקעה אישי - פברואר 2026")

# 1. יצירת סרגל צד להזנת נתונים
st.sidebar.header("הוסף חברה לניתוח")
new_name = st.sidebar.text_input("שם החברה (למשל: Apple)")
new_price = st.sidebar.number_input("מחיר נוכחי ($)", min_value=0.1, value=150.0)
new_growth = st.sidebar.slider("צמיחה צפויה (באחוזים)", 0, 100, 15) / 100
new_pe = st.sidebar.number_input("מכפיל רווח (P/E)", min_value=1, value=25)

# 2. מאגר הנתונים ההתחלתי
all_companies = {
    "Meta (META)": {"price": 647.63, "growth": 0.16, "pe": 26},
    "Amazon (AMZN)": {"price": 204.03, "growth": 0.14, "pe": 40},
    "Microsoft (MSFT)": {"price": 394.63, "growth": 0.13, "pe": 32},
    "Tesla (TSLA)": {"price": 405.93, "growth": 0.18, "pe": 50},
    "Zeta Global (ZETA)": {"price": 18.68, "growth": 0.34, "pe": 30}
}

# 3. הוספת החברה החדשה למאגר (אם הוזן שם)
if new_name:
    all_companies[new_name] = {"price": new_price, "growth": new_growth, "pe": new_pe}

results = []

# 4. לולאת החישובים
for name, d in all_companies.items():
    # נוסחת שווי הוגן ל-5 שנים (מהוון ב-12%)
    fair_price = d["price"] * ((1 + d["growth"])**5) * (d["pe"] / 30) / ((1 + 0.12)**5)
    upside = ((fair_price / d["price"]) - 1) * 100
    
    # קביעת הדירוג
    if upside > 30:
        score = "⭐⭐⭐⭐⭐"
    elif upside > 15:
        score = "⭐⭐⭐⭐"
    else:
        score = "⭐⭐⭐"
        
    results.append({
        "חברה": name, 
        "מחיר נוכחי": f"${d['price']:.2f}", 
        "פוטנציאל רווח": f"{upside:.1f}%", 
        "דירוג": score
    })

# 5. הצגת הטבלה
df = pd.DataFrame(results)
st.table(df)

# טיפ קטן למשתמש
st.info("💡 שים לב: פוטנציאל הרווח מחושב על בסיס צמיחה ל-5 שנים והיוון של 12%.")
