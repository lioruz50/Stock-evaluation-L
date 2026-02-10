import streamlit as st
import yfinance as yf
import pandas as pd
import qrcode
from io import BytesIO

# --- 1. הגדרות דף ---
st.set_page_config(page_title="Value Model", layout="wide")

# --- 2. פונקציות עזר ---
@st.cache_data
def get_company_data(ticker_symbol):
    try:
        stock = yf.Ticker(ticker_symbol)
        info = stock.info
        if not info or 'currentPrice' not in info:
            return None
        
        # קביעת דיפולטים לפי סקטור
        sector = info.get('sector', 'Unknown')
        defaults = {
            "Technology": {"pe": 28.0, "growth": 15},
            "Communication Services": {"pe": 25.0, "growth": 14},
            "Consumer Cyclical": {"pe": 22.0, "growth": 12},
            "Financial Services": {"pe": 15.0, "growth": 8}
        }
        sector_defaults = defaults.get(sector, {"pe": 20.0, "growth": 10})

        return {
            "name": info.get('longName', ticker_symbol),
            "price": info.get('currentPrice', 0.0),
            "market_cap": info.get('marketCap', 0.0) / 1_000_000,
            "revenue": info.get('totalRevenue', 0.0) / 1_000_000,
            "pe_ratio": info.get('trailingPE', sector_defaults["pe"]),
            "sector_growth": sector_defaults["growth"]
        }
    except Exception:
        return None

# --- 3. אבטחה ---
if "password_correct" not in st.session_state:
    st.session_state["password_correct"] = False

if not st.session_state["password_correct"]:
    st.title("🔒 כניסה")
    pwd = st.text_input("סיסמה:", type="password")
    if st.button("כניסה") and pwd == "3535":
        st.session_state["password_correct"] = True
        st.rerun()
    st.stop()

# --- 4. בחירת מניה ---
st.title("📈 מודל השקעה ממוקד תשואה")

# רשימת הצעות לחיפוש מהיר
suggestions = ["META", "GOOGL", "AAPL", "MSFT", "AMZN", "TSLA", "NVDA"]
ticker_input = st.selectbox("🔍 בחר מניה מהרשימה או הקלד סימול:", suggestions + ["אחר..."])

if ticker_input == "אחר...":
    ticker = st.text_input("הקלד סימול (למשל NFLX):").upper()
else:
    ticker = ticker_input

if st.button("נתח מניה"):
    data = get_company_data(ticker)
    if data:
        st.session_state['stock_data'] = data
    else:
        st.error("לא נמצאו נתונים")

current_data = st.session_state.get('stock_data', {
    "name": "Meta Platforms", "price": 649.5, "market_cap": 1637000.0, 
    "revenue": 200000.0, "pe_ratio": 25.0, "sector_growth": 14
})

# --- 5. סרגל צד (דינמי לפי סקטור) ---
st.sidebar.header("⚙️ פרמטרים")
target_pe = st.sidebar.number_input("מכפיל יעד", value=float(current_data['pe_ratio']))
growth = st.sidebar.slider("צמיחה שנתית (%)", 0, 50, current_data['sector_growth']) / 100
margin = st.sidebar.slider("שולי רווח (%)", 0, 50, 35) / 100 # דיפולט 35% כמו באקסל

# --- 6. חישובים ממוקדי מחיר ---
years = 5
future_rev = current_data['revenue'] * ((1 + growth) ** years)
future_profit = future_rev * margin
num_shares = current_data['market_cap'] / current_data['price']

f_price = (future_profit * target_pe) / num_shares
total_return = (f_price / current_data['price'] - 1) * 100
cagr = ((f_price / current_data['price']) ** (1/years) - 1) * 100

# --- 7. תצוגה ---
st.header(f"ניתוח {current_data['name']}")

col1, col2, col3 = st.columns(3)
col1.metric("מחיר נוכחי", f"${current_data['price']:,.2f}")
col2.metric("מחיר יעד (5 שנים)", f"${f_price:,.2f}")
col3.metric("תשואה כוללת חזויה", f"{total_return:.1f}%")

st.subheader("📊 סיכום למשקיע")
st.write(f"השקעה של $1,000 היום צפויה להיות שווה **${1000 * (1 + total_return/100):,.0f}** בעוד 5 שנים.")
st.write(f"זה משקף תשואה שנתית ממוצעת (CAGR) של **{cagr:.1f}%**.")

if cagr > 15:
    st.success("✅ פוטנציאל תשואה גבוה ביחס לשוק")
elif cagr > 8:
    st.warning("🟡 תשואה סבירה, תואמת ממוצע שוק")
else:
    st.error("❌ תשואה נמוכה, ייתכן שהמניה יקרה מדי")
