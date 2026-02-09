import streamlit as st
import yfinance as yf
import pandas as pd
import qrcode
from io import BytesIO

# --- 1. הגדרת פונקציות עזר (למניעת NameError) ---

@st.cache_data(ttl=3600)
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
        # השוואה בין המניה המבוקשת ל-4 מתחרים
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

# --- 2. לוגיקת כניסה (אבטחה) ---

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

# --- 3. ממשק המשתמש (UI) ---

st.title("🚀 מודל הערכת שווי והשוואה")

ticker = st.text_input("🔍 הזן סימול מניה (Ticker):", value="GOOGL").upper()

if st.button("משוך נתונים"):
    with st.spinner('מושך נתונים...'):
        data = get_company_data(ticker)
        if data:
            st.session_state['stock_data'] = data
            st.session_state['ticker'] = ticker
        else:
            st.error("לא נמצאו נתונים עבור הסימול הזה.")

# הצגת נתונים במידה וקיימים
if 'stock_data' in st.session_state:
    curr_ticker = st.session_state['ticker']
    data = st.session_state['stock_data']
    
    st.header(f"ניתוח עבור: {data['name']}")
    
    # הצגת טבלת מתחרים
    st.markdown("---")
    st.subheader("👥 השוואה למתחרים בתעשייה")
    
    peers_df = get_peers_data(curr_ticker)
    
    if peers_df is not None and not peers_df.empty:
        st.table(peers_df.style.format({
            "מכפיל P/E": "{:.2f}",
            "שווי שוק (B)": "${:.2f}B"
        }))
        
        # חישוב ממוצע P/E
        valid_pe = peers_df[peers_df["מכפיל P/E"] > 0]["מכפיל P/E"]
        if not valid_pe.empty:
            st.success(f"💡 מכפיל ה-P/E הממוצע של המתחרים: **{valid_pe.mean():.2f}**")
    else:
        st.info("⚠️ לא נמצאו מתחרים ישירים להשוואה במאגר עבור סימול זה.")
