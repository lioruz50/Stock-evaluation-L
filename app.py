import streamlit as st
import pandas as pd

# הגדרת כותרת והגדרות דף
st.set_page_config(page_title="דירוג מניות 2026", layout="wide")
st.title("📋 טבלת כדאיות השקעה - פברואר 2026")

# מאגר הנתונים של החברות
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

# לולאה שעוברת על כל החברות ומבצעת חישובים
for name, d in all_companies.items():
    # נוסחת שווי הוגן ל-5 שנים (מהוון ב-12%)
    # שימי לב: השורות הבאות מוזחות ימינה כדי להיות חלק מהלולאה
    fair_price = d["price"] * ((1 + d["growth"])**5) * (d["pe"] / 30) / ((1 + 0.12)**5)
    upside = ((fair_price / d["price"]) - 1) * 100
    
    # קביעת הדירוג לפי הפוטנציאל
    if upside > 30:
        score = "⭐⭐⭐⭐⭐"
    elif upside > 15:
        score = "⭐⭐⭐⭐"
    else:
        score = "⭐⭐⭐"
        
    # הוספת התוצאה לרשימה
    results.append({
        "חברה": name, 
        "מחיר נוכחי": f"${d['price']:.2f}", 
        "פוטנציאל רווח": f"{upside:.1f}%", 
        "דירוג": score
    })

# הפיכת הרשימה לטבלה והצגתה
df = pd.DataFrame(results)
st.table(df)
