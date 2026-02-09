import streamlit as st
import yfinance as yf
import pandas as pd

# פונקציה חכמה למשיכת נתונים עם זיכרון מטמון (Cache) כדי לא להעמיס על האתר
@st.cache_data
def fetch_stock_info(ticker_symbol):
    try:
        stock = yf.Ticker(ticker_symbol)
        info = stock.info
        
        # חילוץ נתונים - אם נתון חסר, נשתמש בערך ברירת מחדל
        return {
            "price": info.get('currentPrice', 333.34),
            "market_cap": info.get('marketCap', 4024000000) / 1e6,
            "revenue": info.get('totalRevenue', 402000000) / 1e6
        }
    except Exception:
        return None

# --- ממשק המשתמש ---
st.sidebar.header("חיבור נתונים אוטומטי")
ticker = st.sidebar.text_input("הזן סימול מניה (למשל GOOGL):", value="GOOGL")

if st.sidebar.button("משוך נתונים עדכניים"):
    with st.spinner('מושך נתונים מ-Yahoo Finance...'):
        live_data = fetch_stock_info(ticker)
        if live_data:
            st.session_state['data'] = live_data
            st.sidebar.success("הנתונים עודכנו!")
        else:
            st.sidebar.error("לא הצלחתי למצוא את המניה. בדוק את הסימול.")

# הגדרת ערכים ראשוניים (Default) אם עדיין לא נלחץ הכפתור
if 'data' not in st.session_state:
    st.session_state['data'] = {"price": 333.34, "market_cap": 4024.0, "revenue": 402.0}

# שימוש בנתונים בתיבות הקלט
rev = st.sidebar.number_input("הכנסות ($M)", value=float(st.session_state['data']['revenue']))
mc = st.sidebar.number_input("שווי שוק ($M)", value=float(st.session_state['data']['market_cap']))
pr = st.sidebar.number_input("מחיר מניה ($)", value=float(st.session_state['data']['price']))
