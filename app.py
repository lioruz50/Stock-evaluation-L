import streamlit as st
import yfinance as yf
import pandas as pd
import qrcode
from io import BytesIO

# --- 1. פונקציות עזר ---

def format_large_number(n):
    """ממיר מספר במיליונים לתצוגה של מיליארד (B) או מיליון (M)"""
    if n >= 1000:
        return f"{n/1000:.2f}B"
    return f"{n:.2f}M"

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
            "pe_ratio": info.get('trailingPE', 25.0)
        }
    except Exception:
        return None

def gen_qr(url):
    qr = qrcode.make(url)
    buf = BytesIO()
    qr.save(buf, format="PNG")
    return buf.getvalue()

# --- 2. אבטחה ---
PASSWORD = "3535"
if "password_correct" not in st.session_state:
    st.session_state["password_correct"] = False

if not st.session_state["password_correct"]:
    st.title("🔒 כניסה למערכת")
    pwd = st.text_input("הזן סיסמה:", type="password")
    if st.button("כניסה"):
        if pwd == PASSWORD:
            st.session_state["password_correct"] = True
            st.rerun()
        else:
            st.error("❌ סיסמה שגויה")
    st.stop()

# --- 3. משיכת נתונים ---
st.title("🚀 מודל הערכת שווי חכם")

ticker = st.text_input("🔍 הזן סימול מניה (Ticker):", value="GOOGL").upper()

if st.button("משוך נתונים עדכניים"):
    with st.spinner('מושך נתונים...'):
        data = get_company_data(ticker)
        if data:
            st.session_state['stock_data'] = data
        else:
            st.error("❌ לא נמצאו נתונים. וודא שהסימול נכון.")

# נתוני ברירת מחדל
current_data = st.session_state.get('stock_data', {
    "name": "Google", "price": 160.0, "market_cap": 2000000.0, 
    "revenue": 307000.0, "currency": "USD", "pe_ratio": 25.0
})

st.header(f"ניתוח עבור: {current_data['name']}")

# --- 4. סרגל צד משולב ---
st.sidebar.header("⚙️ פרמטרים להערכת שווי")

# בחירת מכפיל יעד
target_pe = st.sidebar.number_input("מכפיל רווח יעד (Target P/E)", 
                                    value=float(current_data['pe_ratio']), step=1.0)

# פרמטרים נוספים
growth_rate = st.sidebar.slider("צמיחה שנתית (%)", 0, 50, 12) / 100
profit_margin = st.sidebar.slider("שולי רווח נקי (%)", 0, 50, 25) / 100
discount_rate = st.sidebar.slider("שיעור היוון (WACC) %", 5, 20, 12) / 100

st.sidebar.markdown("---")
st.sidebar.header("📝 נתוני בסיס (משיכה אוטומטית)")

# הצגת הנתונים שנמשכו בצורה קריאה (B/M)
st.sidebar.info(f"הכנסות (רשת): {format_large_number(current_data['revenue'])}")
st.sidebar.info(f"שווי שוק (רשת): {format_large_number(current_data['market_cap'])}")

# שדות עריכה ידניים
rev_input = st.sidebar.number_input("ערוך הכנסות (במיליונים)", value=float(current_data['revenue']))
mc_input = st.sidebar.number_input("ערוך שווי שוק (במיליונים)", value=float(current_data['market_cap']))
price_input = st.sidebar.number_input("ערוך מחיר מניה", value=float(current_data['price']))

# --- 5. חישובים ---
years = 5
future_rev = rev_input * ((1 + growth_rate) ** years)
future_profit = future_rev * profit_margin
num_shares = mc_input / price_input if price_input > 0 else 1

f_mc = future_profit * target_pe
f_price = f_mc / num_shares
fair_today = f_price / ((1 + discount_rate) ** years)
mos = (fair_today - price_input) / price_input * 100

# --- 6. תצוגת תוצאות ---
st.subheader("📊 סיכום הערכה")
c1, c2, c3 = st.columns(3)
c1.metric("מחיר נוכחי", f"${price_input:,.2f}")
c2.metric("שווי הוגן היום", f"${fair_today:,.2f}")
c3.metric("מרווח ביטחון", f"{mos:.1f}%")

# תצוגת הרווח הנקי העתידי בקיצורים חכמים
st.write(f"💰 **רווח נקי צפוי בעוד 5 שנים:** {format_large_number(future_profit)}")

st.sidebar.markdown("---")
# ייצור QR למעבר מהיר
qr_img = gen_qr("https://share.streamlit.io/") 
st.sidebar.image(qr_img, caption="סרוק למעבר למובייל")
