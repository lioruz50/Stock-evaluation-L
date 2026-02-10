import streamlit as st
import yfinance as yf
import pandas as pd
import qrcode
from io import BytesIO

# --- 1. פונקציות עזר (מוגדרות מראש למניעת NameError) ---

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
            "pe_ratio": info.get('trailingPE', 25.0) # מכפיל נוכחי מהשוק
        }
    except Exception:
        return None

def gen_qr(url):
    qr = qrcode.make(url)
    buf = BytesIO()
    qr.save(buf, format="PNG")
    return buf.getvalue()

# --- 2. מנגנון אבטחה ---

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

# --- 3. ממשק המשתמש ---

st.title("🚀 מודל הערכת שווי משופר")

ticker = st.text_input("🔍 הזן סימול מניה (Ticker):", value="GOOGL").upper()

if st.button("משוך נתונים עדכניים"):
    with st.spinner('מושך נתונים...'):
        data = get_company_data(ticker)
        if data:
            st.session_state['stock_data'] = data
        else:
            st.error("❌ לא נמצאו נתונים. וודא שהסימול נכון.")

# שימוש בנתונים שנמשכו או בברירת מחדל
current_data = st.session_state.get('stock_data', {
    "name": "Google", "price": 160.0, "market_cap": 2000000.0, 
    "revenue": 307000.0, "currency": "USD", "pe_ratio": 25.0
})

st.header(f"ניתוח עבור: {current_data['name']}")

# --- 4. סרגל צד (הוספת שליטה במכפיל) ---

st.sidebar.header("⚙️ פרמטרים להערכת שווי")

# מכפיל רווח יעד - המשתמש יכול לשנות ידנית
target_pe = st.sidebar.number_input("מכפיל רווח יעד (Target P/E)", 
                                    value=float(current_data['pe_ratio']), 
                                    step=1.0)

growth_rate = st.sidebar.slider("צמיחת הכנסות שנתית (%)", 0, 50, 12) / 100
profit_margin = st.sidebar.slider("שולי רווח נקי (%)", 0, 50, 25) / 100
discount_rate = st.sidebar.slider("שיעור היוון (%)", 5, 20, 12) / 100

st.sidebar.markdown("---")
st.sidebar.header("📝 עריכת נתוני שוק")
rev_input = st.sidebar.number_input("הכנסות (מיליונים)", value=float(current_data['revenue']))
price_input = st.sidebar.number_input("מחיר מניה", value=float(current_data['price']))
mc_input = st.sidebar.number_input("שווי שוק (מיליונים)", value=float(current_data['market_cap']))

# --- 5. חישובים ---

years = 5
future_rev = rev_input * ((1 + growth_rate) ** years)
future_profit = future_rev * profit_margin
num_shares = mc_input / price_input if price_input > 0 else 1

# בניית 3 תרחישים סביב המכפיל שבחרת
multiples = [target_pe * 0.8, target_pe, target_pe * 1.2]
results = []

for m in multiples:
    f_mc = future_profit * m
    f_price = f_mc / num_shares
    fair_today = f_price / ((1 + discount_rate) ** years)
    mos = (fair_today - price_input) / price_input * 100 if price_input > 0 else 0
    results.append({
        "תרחיש": "שמרני" if m < target_pe else ("אופטימי" if m > target_pe else "יעד"),
        "מכפיל": round(m, 1), 
        "מחיר צפוי 2031": f_price, 
        "שווי הוגן היום": fair_today, 
        "מרווח ביטחון": mos
    })

# --- 6. תצוגת תוצאות ---

st.subheader("📊 תוצאות המודל")
c1, c2, c3 = st.columns(3)
c1.metric("מחיר נוכחי", f"${price_input:,.2f}")
c2.metric("שווי הוגן (לפי היעד)", f"${results[1]['שווי הוגן היום']:,.2f}")
c3.metric("מרווח ביטחון", f"{results[1]['מרווח ביטחון']:.1f}%")

df_results = pd.DataFrame(results)
st.table(df_results.style.format({
    "מחיר צפוי 2031": "{:,.2f}$", 
    "שווי הוגן היום": "{:,.2f}$", 
    "מרווח ביטחון": "{:.1f}%"
}))

st.sidebar.markdown("---")
# החלף את הקישור למטה בלינק האמיתי של האפליקציה שלך ב-Streamlit Cloud
st.sidebar.image(gen_qr("https://share.streamlit.io/"), caption="סרוק למעבר לנייד")
