import streamlit as st
import yfinance as yf
import pandas as pd

# פונקציה למשיכת נתונים
@st.cache_data
def get_company_data(ticker_symbol):
    try:
        stock = yf.Ticker(ticker_symbol)
        info = stock.info
        return {
            "name": info.get('longName', ticker_symbol),
            "price": info.get('currentPrice', 0.0),
            "market_cap": info.get('marketCap', 0.0) / 1e6,
            "revenue": info.get('totalRevenue', 0.0) / 1e6,
            "currency": info.get('currency', 'USD')
        }
    except Exception:
        return None

# --- עיצוב וכותרת ---
st.title("🚀 מודל הערכת שווי אוטומטי")

# --- סרגל צד ---
st.sidebar.header("חיבור נתונים אוטומטי")
ticker = st.sidebar.text_input("הזן סימול מניה (Ticker):", value="GOOGL").upper()

if st.sidebar.button("משוך נתונים עדכניים"):
    data = get_company_data(ticker)
    if data:
        st.session_state['stock_data'] = data
    else:
        st.sidebar.error("לא נמצאו נתונים עבור סימול זה.")

# שימוש בנתונים (Default במידה ולא נמשך כלום)
current_data = st.session_state.get('stock_data', {"name": "Google", "price": 333.34, "market_cap": 4024.0, "revenue": 402.0, "currency": "USD"})

# תצוגת שם החברה שנבחרה
st.header(f"ניתוח עבור: {current_data['name']} ({ticker})")

# תיבות קלט לעריכה ידנית
st.sidebar.subheader("נתוני בסיס")
rev_input = st.sidebar.number_input(f"הכנסות ($M {current_data['currency']})", value=float(current_data['revenue']))
mc_input = st.sidebar.number_input(f"שווי שוק ($M {current_data['currency']})", value=float(current_data['market_cap']))
price_input = st.sidebar.number_input(f"מחיר מניה ({current_data['currency']})", value=float(current_data['price']))

# סליידרים
growth_rate = st.sidebar.slider("צמיחת הכנסות שנתית (%)", 0, 50, 12) / 100
profit_margin = st.sidebar.slider("שולי רווח נקי (%)", 0, 50, 35) / 100
discount_rate = st.sidebar.slider("שיעור היוון (%)", 5, 20, 12) / 100

# --- חישובים ---
years = 5
future_rev = rev_input * ((1 + growth_rate) ** years)
future_profit = future_rev * profit_margin
num_shares = mc_input / price_input

# --- הצגת הערכת שווי מרוכזת ---
multiples = [25, 30, 35]
results = []

for m in multiples:
    f_mc = future_profit * m
    f_price = f_mc / num_shares
    fair_today = f_price / ((1 + discount_rate) ** years)
    mos = (fair_today - price_input) / price_input * 100
    results.append({"מכפיל": m, "מחיר 2030": f_price, "שווי הוגן": fair_today, "מרווח": mos})

# הצגת סיכום הערכת שווי
fair_val_avg = results[1]['שווי הוגן'] # לפי מכפיל 30
st.subheader("📊 סיכום הערכת שווי")

col1, col2, col3 = st.columns(3)
col1.metric("מחיר נוכחי", f"{price_input:,.2f} {current_data['currency']}")
col2.metric("שווי הוגן (מכפיל 30)", f"{fair_val_avg:,.2f} {current_data['currency']}")
col3.metric("מרווח ביטחון", f"{results[1]['מרווח']:.1f}%")

if results[1]['מרווח'] > 15:
    st.success(f"המשך לבדוק! המניה נראית בחסר משמעותי לפי מכפיל 30.")
elif results[1]['מרווח'] > 0:
    st.info("המניה נסחרת קרוב לשווי ההוגן שלה.")
else:
    st.warning("המניה נראית יקרה כרגע בהתבסס על תחזית הצמיחה.")

# טבלת פירוט
st.write("### פירוט תרחישים")
df_res = pd.DataFrame(results)
st.table(df_res.style.format({
    "מחיר 2030": "{:,.2f}$", 
    "שווי הוגן": "{:,.2f}$", 
    "מרווח": "{:.1f}%"
}))
