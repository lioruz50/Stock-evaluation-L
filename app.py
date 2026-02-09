import streamlit as st
import yfinance as yf
import pandas as pd
import qrcode
from io import BytesIO

# --- 1. הגדרת פונקציות (חייב להופיע לפני השימוש בהן) ---

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
    except:
        return None

@st.cache_data(ttl=3600)
def get_peers_data(ticker_symbol):
    try:
        stock = yf.Ticker(ticker_symbol)
        peers = stock.peers
        if not peers or len(peers) == 0:
            return None
        
        comparison_list = []
        # לוקחים את המניה שנבחרה + עד 4 מתחרים
        for t in [ticker_symbol] + peers[:4]:
            t_info = yf.Ticker(t).info
            comparison_list.append({
                "סימול": t,
                "שם": t_info.get('shortName', t),
                "מכפיל P/E": t_info.get('trailingPE', 0.0),
                "שווי שוק (B)": (t_info.get('marketCap', 0.0) / 1_000_000_000)
            })
        return pd.DataFrame(comparison_list)
    except:
        return None

# --- 2. מנגנון אבטחה ---

PASSWORD = "3535"
if "password_correct" not in st.session_state:
    st.session_state["password_correct"] = False

if not st.session_state["password_correct"]:
    st.title("🔒 כניסה למערכת")
    pwd_input = st.text_input("הזן סיסמה:", type="password")
    if st.button("כניסה"):
        if pwd_input == PASSWORD:
            st.session_state["password_correct"] = True
            st.rerun()
        else:
            st.error("❌ סיסמה שגויה")
    st.stop()

# --- 3. ממשק משתמש (UI) ---

st.title("🚀 מודל הערכת שווי והשוואה")

ticker = st.text_input("🔍 הזן סימול מניה (Ticker):", value="GOOGL").upper()

if st.button("משוך נתונים"):
    with st.spinner('מושך נתונים...'):
        data = get_company_data(ticker)
        if data:
            st.session_state['stock_data'] = data
        else:
            st.error("לא נמצאו נתונים עבור הסימול הזה.")

# הצגת נתונים והשוואה אם קיימים ב-session_state
if 'stock_data' in st.session_state:
    data = st.session_state['stock_data']
    st.header(f"ניתוח עבור: {data['name']}")
    
    # הצגת טבלת מתחרים
    st.markdown("---")
    st.subheader("👥 השוואה למתחרים בתעשייה")
    
    peers_df = get_peers_data(ticker)
    
    if peers_df is not None:
        st.table(peers_df.style.format({
            "מכפיל P/E": "{:.2f}",
            "שווי שוק (B)": "${:.2f}B"
        }))
    else:
        st.info("לא נמצאו מתחרים ישירים להשוואה (Peers) במאגר הנתונים.")
