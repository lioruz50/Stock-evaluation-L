import streamlit as st
import yfinance as yf
import pandas as pd
import qrcode
from io import BytesIO

# --- 1. פונקציות עזר (חייבות להופיע ראשונות) ---

@st.cache_data(ttl=3600)
def get_company_data(ticker_symbol):
    try:
        stock = yf.Ticker(ticker_symbol)
        info = stock.info
        return {
            "name": info.get('longName', ticker_symbol),
            "price": info.get('currentPrice', 0.0),
            "market_cap": info.get('marketCap', 0.0) / 1_000_000,
            "revenue": info.get('totalRevenue', 0.0) / 1_000_000,
            "currency": info.get('currency', 'USD'),
            "sector": info.get('sector', 'N/A'),
            "pe_ratio": info.get('trailingPE', 0.0)
        }
    except: return None

@st.cache_data(ttl=3600)
def get_peers_data(ticker_symbol):
    try:
        stock = yf.Ticker(ticker_symbol)
        peers = stock.peers
        if not peers: return None
        
        comparison_list = []
        for t in [ticker_symbol] + peers[:4]:
            t_info = yf.Ticker(t).info
            comparison_list.append({
                "סימול": t,
                "שם": t_info.get('shortName', t),
                "P/E": t_info.get('trailingPE', 0.0),
                "שווי שוק (B)": (t_info.get('marketCap', 0.0) / 1_000_000_000)
            })
        return pd.DataFrame(comparison_list)
    except: return None

# --- 2. לוגיקת אבטחה וכניסה ---

PASSWORD = "3535"
if "password_correct" not in st.session_state:
    st.session_state["password_correct"] = False

if not st.session_state["password_correct"]:
    st.title("🔒 כניסה")
    pwd = st.text_input("סיסמה:", type="password")
    if st.button("כניסה"):
        if pwd == PASSWORD:
            st.session_state["password_correct"] = True
            st.rerun()
        else: st.error("שגויה")
    st.stop()

# --- 3. ממשק המשתמש והחישובים ---

st.title("🚀 מודל הערכת שווי והשוואה")

ticker = st.text_input("🔍 הזן סימול (Ticker):", value="GOOGL").upper()

if st.button("משוך נתונים"):
    data = get_company_data(ticker)
    if data: st.session_state['stock_data'] = data
    else: st.error("לא נמצאו נתונים")

# נתונים נוכחיים
stock_data = st.session_state.get('stock_data')

if stock_data:
    st.subheader(f"ניתוח עבור {stock_data['name']}")
    
    # --- השוואת מתחרים (כאן הייתה השגיאה) ---
    st.markdown("---")
    st.subheader("👥 השוואה למתחרים")
    peers_df = get_peers_data(ticker)
    if peers_df is not None:
        st.table(peers_df.style.format({"P/E": "{:.2f}", "שווי שוק (B)": "${:.2f}B"}))
    else:
        st.info("לא נמצאו מתחרים ישירים להשוואה.")
