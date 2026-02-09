import streamlit as st
import yfinance as yf
import pandas as pd
import qrcode
from io import BytesIO

# --- הגדרות ופונקציות (חייבות להופיע בראש הקובץ) ---
PASSWORD = "3535"

def gen_qr(url):
    qr = qrcode.make(url)
    buf = BytesIO()
    qr.save(buf, format="PNG")
    return buf.getvalue()

def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
    if st.session_state["password_correct"]:
        return True

    st.title("🔒 כניסה למערכת")
    pwd_input = st.text_input("הזן סיסמה:", type="password")
    if st.button("כניסה"):
        if pwd_input == PASSWORD:
            st.session_state["password_correct"] = True
            st.rerun()
        else:
            st.error("❌ סיסמה שגויה")
    return False

@st.cache_data
def get_company_data(ticker_symbol):
    try:
        stock = yf.Ticker(ticker_symbol)
        info = stock.info
        if not info or 'currentPrice' not in info:
            return None
        return {
            "name": info.get('longName', ticker_symbol),
            "price": info.get('currentPrice', 0.0),
            "market_cap": info.get('marketCap', 0.0) / 1_000_000, 
            "revenue": info.get('totalRevenue', 0.0) / 1_000_000,
            "currency": info.get('currency', 'USD')
        }
    except Exception:
        return None

# --- הרצת האפליקציה ---
if not check_password():
    st.stop()

st.title("🚀 מודל הערכת שווי")

ticker = st.text_input("🔍 הזן סימול מניה (Ticker):", value="GOOGL").upper()

if st.button("משוך נתונים עדכניים"):
    with st.spinner('מושך נתונים...'):
        data = get_company_data(ticker)
        if data:
            st.session_state['stock_data'] = data
        else:
            st.error("❌ לא נמצאו נתונים. וודא שהסימול נכון.")

# נתוני ברירת מחדל
current_data = st.session_state.get('stock_data', {"name": "Google", "price": 160.0, "market_cap": 2000000.0, "revenue": 307000.0, "currency": "USD"})

st.header(f"ניתוח עבור: {current_data['name']}")

# --- סרגל צד ---
st.sidebar.header("נתוני בסיס (עריכה ידנית)")
rev_input = st.sidebar.number_input(f"הכנסות במיליוני {current_data['currency']}", value=float(current_data['revenue']))
mc_input = st.sidebar.number_input(f"שווי שוק במיליוני {current_data['currency']}", value=float(current_data['market_cap']))
price_input = st.sidebar.number_input(f"מחיר מניה ({current_data['currency']})", value=float(current_data['price']))

st.sidebar.header("פרמטרים לצמיחה")
growth_rate = st.sidebar.slider("צמיחת הכנסות שנתית (%)", 0, 50, 12) / 100
profit_margin = st.sidebar.slider("שולי רווח נקי (%)", 0, 50, 25) / 100
discount_rate = st.sidebar.slider("שיעור היוון (%)", 5, 20, 12) / 100

# --- חישובים ---
years = 5
future_rev = rev_input * ((1 + growth_rate) ** years)
future_profit = future_rev * profit_margin
num_shares = mc_input / price_input if price_input > 0 else 1

multiples = [25, 30, 35]
results = []
for m in multiples:
    f_mc = future_profit * m
    f_price = f_mc / num_shares
    fair_today = f_price / ((1 + discount_rate) ** years)
    mos = (fair_today - price_input) / price_input * 100 if price_input > 0 else 0
    results.append({"מכפיל": m, "מחיר 2030": f_price, "שווי הוגן": fair_today, "מרווח": mos})

# --- תצוגה ---
st.subheader("📊 סיכום הערכת שווי")
c1, c2, c3 = st.columns(3)
c1.metric("מחיר נוכחי", f"${price_input:,.2f}")
c2.metric("שווי הוגן (מכפיל 30)", f"${results[1]['שווי הוגן']:,.2f}")
c3.metric("מרווח ביטחון", f"{results[1]['מרווח']:.1f}%")

st.table(pd.DataFrame(results).style.format({"מחיר 2030": "{:,.2f}$", "שווי הוגן": "{:,.2f}$", "מרווח": "{:.1f}%"}))

st.sidebar.markdown("---")
st.sidebar.image(gen_qr("https://share.streamlit.io/"), caption="סרוק למעבר מהיר")
