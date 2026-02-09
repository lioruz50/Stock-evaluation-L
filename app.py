import streamlit as st
import yfinance as yf
import pandas as pd

# --- פונקציית השוואת מתחרים ---
def get_peers_data(ticker_symbol):
    try:
        stock = yf.Ticker(ticker_symbol)
        # ניסיון למשוך רשימת מתחרים (לא תמיד זמין לכל המניות)
        peers = stock.peers
        
        # אם אין רשימת מתחרים, נשתמש ברשימה גנרית כגיבוי (או נחזיר ריק)
        if not peers or len(peers) == 0:
            return None
        
        comparison_list = []
        # נוסיף את המניה המקורית לרשימה להשוואה
        all_tickers = [ticker_symbol] + peers[:4] # מקבילים + 4 מתחרים ראשונים
        
        for t in all_tickers:
            t_stock = yf.Ticker(t)
            t_info = t_stock.info
            comparison_list.append({
                "סימול": t,
                "שם": t_info.get('shortName', t),
                "מכפיל רווח (P/E)": t_info.get('trailingPE', 0.0),
                "מכפיל הכנסות (P/S)": t_info.get('priceToSalesTrailing12Months', 0.0),
                "שווי שוק (B)": (t_info.get('marketCap', 0.0) / 1_000_000_000),
                "תשואת דיבידנד (%)": (t_info.get('dividendYield', 0.0) or 0) * 100
            })
        return pd.DataFrame(comparison_list)
    except:
        return None

# --- בתוך ממשק המשתמש (אחרי הצגת תוצאות הערכת השווי) ---

st.markdown("---")
st.subheader("👥 השוואה למתחרים בתעשייה")

with st.spinner('מנתח מתחרים בסקטור...'):
    peers_df = get_peers_data(ticker)
    
    if peers_df is not None:
        # עיצוב הטבלה להדגשת המניה שנבחרה
        def highlight_ticker(s):
            return ['background-color: #1f77b4; color: white' if s.סימול == ticker else '' for _ in s]
        
        st.write("נתונים אלו עוזרים להבין אם מכפיל היעד שבחרת הגיוני ביחס למתחרים:")
        
        styled_df = peers_df.style.format({
            "מכפיל רווח (P/E)": "{:.2f}",
            "מכפיל הכנסות (P/S)": "{:.2f}",
            "שווי שוק (B)": "${:.2f}B",
            "תשואת דיבידנד (%)": "{:.2f}%"
        }).apply(highlight_ticker, axis=1)
        
        st.table(styled_df)
        
        # תובנה אוטומטית
        avg_pe = peers_df["מכפיל רווח (P/E)"].replace(0, pd.NA).dropna().mean()
        st.caption(f"💡 מכפיל ה-P/E הממוצע בקבוצת המתחרים הזו הוא **{avg_pe:.2f}**.")
    else:
        st.warning("לא נמצאו נתוני מתחרים ישירים עבור סימול זה.")

# --- עדכון קטן לסרגל הצד (אופציונלי) ---
if peers_df is not None:
    avg_pe_val = peers_df["מכפיל רווח (P/E)"].replace(0, pd.NA).dropna().mean()
    if st.sidebar.button("השתמש במכפיל ממוצע של המתחרים"):
        st.session_state['fair_multiple'] = avg_pe_val
        st.rerun()
