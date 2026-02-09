import streamlit as st
import yfinance as yf
import pandas as pd
import qrcode
from io import BytesIO

# --- הגדרות אבטחה ופונקציות עזר (חובה להגדיר בראש הקוד) ---
PASSWORD = "3535"

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
            "currency": info.get('currency', 'USD'),
            "pe_ratio": info.get('trailingPE', 20.0)
        }
    except Exception:
        return None

def gen_qr(url):
    qr = qrcode.make(url)
    buf = BytesIO()
    qr.save(buf, format="PNG")
    return buf.getvalue()

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
            st.error("לא נמצאו נתונים. וודא שהסימול נכון.")

# נתוני ברירת מחדל
current_data = st.session_state.get('stock_data', {"name": "Google", "price": 160.0, "market_cap": 2000000.0, "revenue": 307000.0, "currency": "USD", "pe_ratio": 25.0})

st.header(f"ניתוח עבור: {current_data['name']}")

# --- סרגל צד לפרמטרים ---
st.sidebar.header("נתוני בסיס")
rev_input = st.sidebar.number_input(f"הכנסות (מיליונים)", value=float(current_data['revenue']))
price_input = st.sidebar.number_input(f"מחיר מניה", value=float(current_data['price']))

st.sidebar.header("פרמטרים לעדכון")
growth_rate = st.sidebar.slider("צמיחה שנתית (%)", 0, 50, 12) / 100
profit_margin = st.sidebar.slider("שולי רווח (%)", 0, 50, 25) / 100
fair_pe = st.sidebar.number_input("מכפיל רווח יעד (P/E)", value=float(current_data['pe_ratio']))
discount_rate = st.sidebar.slider("שיעור היוון (%)", 5, 20, 12) / 100

# --- חישובים ---
future_rev = rev_input * ((1 + growth_rate) ** 5)
future_profit = future_rev * profit_margin
# חישוב שווי הוגן לפי המכפיל שהזנת
fair_today = (future_profit * fair_pe) / ((1 + discount_rate) ** 5)
# המרת שווי שוק למחיר מניה מוערך (יחסי)
fair_price_today = (fair_today / (current_data['market_cap'])) * current_data['price']
mos = (fair_price_today - price_input) / price_input * 100

# --- תצוגה ---
st.subheader("📊 סיכום הערכת שווי")
c1, c2, c3 = st.columns(3)
c1.metric("מחיר נוכחי", f"${price_input:,.2f}")
c2.metric("שווי הוגן (יעד)", f"${fair_price_today:,.2f}")
c3.metric("מרווח ביטחון", f"{mos:.1f}%")

st.sidebar.markdown("---")
st.sidebar.image(gen_qr("https://share.streamlit.io/"), caption="סרוק למובייל")
