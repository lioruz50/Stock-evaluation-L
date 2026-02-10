import streamlit as st
import yfinance as yf
import pandas as pd

# --- 1. הגדרות דף ---
st.set_page_config(page_title="Investment Model", layout="wide")

# --- 2. פונקציית משיכת נתונים עם דיפולטים לפי סקטור ---
@st.cache_data
def get_company_data(ticker_symbol):
    try:
        stock = yf.Ticker(ticker_symbol)
        info = stock.info
        if not info or 'currentPrice' not in info:
            return None
        
        # קביעת דיפולטים לפי סקטור כדי להתאים לאקסל
        sector = info.get('sector', '')
        # ברירת מחדל כללית
        pe, growth, margin = 20.0, 10, 20.0
        
        if "Technology" in sector or "Communication" in sector:
            pe, growth, margin = 25.0, 14, 35.0 # ערכי האקסל שלך
            
        return {
            "name": info.get('longName', ticker_symbol),
            "price": info.get('currentPrice', 0.0),
            "market_cap": info.get('marketCap', 0.0) / 1_000_000,
            "revenue": info.get('totalRevenue', 0.0) / 1_000_000,
            "pe_ratio": info.get('trailingPE', pe),
            "growth": growth,
            "margin": margin
        }
    except:
        return None

# --- 3. אבטחה ---
if "password_correct" not in st.session_state:
    st.session_state["password_correct"] = False

if not st.session_state["password_correct"]:
    st.title("🔒 כניסה למערכת")
    pwd = st.text_input("סיסמה:", type="password")
    if st.button("כניסה") and pwd == "3535":
        st.session_state["password_correct"] = True
        st.rerun()
    st.stop()

# --- 4. ממשק בחירת מניה ---
st.title("🚀 מודל תשואה והערכת שווי")

# רשימת מניות מהירה למניעת טעויות הקלדה
suggestions = ["META", "GOOGL", "AAPL", "MSFT", "AMZN", "NVDA", "TSLA"]
selected_ticker = st.selectbox("🔍 בחר מניה או הקלד סימול:", suggestions + ["אחר..."])

if selected_ticker == "אחר...":
    ticker = st.text_input("הקלד סימול (למשל: NFLX):").upper()
else:
    ticker = selected_ticker

if st.button("נתח מניה"):
    with st.spinner('מושך נתונים...'):
        data = get_company_data(ticker)
        if data:
            st.session_state['stock_data'] = data
        else:
            st.error("לא נמצאו נתונים עבור הסימול שהוזן.")

# בדיקה שהנתונים קיימים לפני הצגת השדות
if 'stock_data' in st.session_state:
    d = st.session_state['stock_data']
    
    # --- 5. סרגל צד עם הדיפולטים של הסקטור ---
    st.sidebar.header("⚙️ פרמטרים (מותאמים לסקטור)")
    target_pe = st.sidebar.number_input("מכפיל יעד (P/E)", value=float(d['pe_ratio']))
    growth = st.sidebar.slider("צמיחה שנתית (%)", 0, 50, int(d['growth'])) / 100
    margin = st.sidebar.slider("שולי רווח (%)", 0, 50, int(d['margin'])) / 100
    
    # --- 6. חישובים ---
    years = 5
    future_rev = d['revenue'] * ((1 + growth) ** years)
    future_profit = future_rev * margin
    num_shares = d['market_cap'] / d['price']
    
    f_price = (future_profit * target_pe) / num_shares
    upside = (f_price / d['price'] - 1) * 100
    cagr = ((f_price / d['price']) ** (1/years) - 1) * 100
    
    # --- 7. תצוגה מרכזית ---
    st.header(f"ניתוח עבור {d['name']}")
    
    c1, c2, c3 = st.columns(3)
    c1.metric("מחיר נוכחי", f"${d['price']:,.2f}")
    c2.metric("מחיר יעד 2031", f"${f_price:,.2f}")
    c3.metric("תשואה כוללת", f"{upside:.1f}%")
    
    st.subheader("💰 פוטנציאל השקעה")
    st.write(f"על סמך צמיחה של **{growth*100:.0f}%** ושולי רווח של **{margin*100:.0f}%**:")
    st.write(f"התשואה השנתית הממוצעת (CAGR) הצפויה היא **{cagr:.1f}%**.")
    
    if cagr > 15:
        st.success("✅ המניה נראית כאטרקטיבית מאוד בתרחיש זה")
    elif cagr > 0:
        st.warning("🟡 תשואה חיובית, אך מומלץ לבדוק מרווח ביטחון")
    else:
        st.error("❌ המניה נראית יקרה מדי ביחס לצמיחה החזויה")

else:
    st.info("הזן סימול מניה ולחץ על 'נתח מניה' כדי להתחיל.")
