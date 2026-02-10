import streamlit as st
import yfinance as yf
import pandas as pd
import qrcode
from io import BytesIO

# --- 1. הגדרות עיצוב (צבע רקע נעים) ---
st.set_page_config(page_title="Value Model", layout="wide")

st.markdown("""
    <style>
    .stApp {
        background-color: #f0f2f6;
    }
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_value=True)

# --- 2. פונקציות עזר ---
def format_large_number(n):
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

# --- 3. אבטחה ---
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

# --- 4. משיכת נתונים ---
st.title("📈 מודל הערכת שווי מקצועי")

ticker = st.text_input("🔍 הזן סימול מניה (Ticker):", value="META").upper()

if st.button("משוך נתונים עדכניים"):
    with st.spinner('מושך נתונים...'):
        data = get_company_data(ticker)
        if data:
            st.session_state['stock_data'] = data
        else:
            st.error("❌ לא נמצאו נתונים.")

current_data = st.session_state.get('stock_data', {
    "name": "Meta Platforms, Inc.", "price": 649.5, "market_cap": 1637000.0, 
    "revenue": 200000.0, "currency": "USD", "pe_ratio": 25.0
})

st.header(f"ניתוח עבור: {current_data['name']}")

# --- 5. סרגל צד (עדכון ברירות מחדל לפי האקסל) ---
st.sidebar.header("⚙️ פרמטרים להערכה")
target_pe = st.sidebar.number_input("מכפיל רווח יעד (P/E)", value=float(current_data['pe_ratio']), step=1.0)
growth_rate = st.sidebar.slider("צמיחה שנתית (%)", 0, 50, 14) / 100 # מעודכן ל-14%
profit_margin = st.sidebar.slider("שולי רווח נקי (%)", 0, 50, 35) / 100 # מעודכן ל-35%
discount_rate = st.sidebar.slider("שיעור היוון (WACC) %", 5, 20, 12) / 100

st.sidebar.markdown("---")
st.sidebar.header("📝 נתוני בסיס")
rev_input = st.sidebar.number_input("הכנסות (במיליונים)", value=float(current_data['revenue']))
mc_input = st.sidebar.number_input("שווי שוק (במיליונים)", value=float(current_data['market_cap']))
price_input = st.sidebar.number_input("מחיר מניה נוכחי", value=float(current_data['price']))

# --- 6. חישובים ---
years = 5
future_rev = rev_input * ((1 + growth_rate) ** years)
future_profit = future_rev * profit_margin
num_shares = mc_input / price_input if price_input > 0 else 1

# חישוב תרחיש ניטרלי (היעד שבחרת)
f_mc_neutral = future_profit * target_pe
f_price_neutral = f_mc_neutral / num_shares
fair_today = f_price_neutral / ((1 + discount_rate) ** years)
mos = (fair_today - price_input) / price_input * 100
cagr_neutral = ((f_price_neutral / price_input) ** (1/years) - 1) * 100 if price_input > 0 else 0

# המלצת קנייה
if mos > 15:
    recommendation = "✅ קנייה חזקה (Strong Buy)"
    color = "green"
elif mos > 0:
    recommendation = "🟡 החזק/קנייה מתונה (Hold/Buy)"
    color = "orange"
else:
    recommendation = "❌ מכירה/המתנה (Overvalued)"
    color = "red"

# --- 7. תצוגה מרכזית (כרטיסי סיכום) ---
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("מחיר נוכחי", f"${price_input:,.2f}")
with col2:
    st.metric("מחיר צפוי (2031)", f"${f_price_neutral:,.2f}", f"{cagr_neutral:.1f}% CAGR")
with col3:
    st.metric("שווי הוגן היום", f"${fair_today:,.2f}", f"{mos:.1f}% Margin")

st.markdown(f"### המלצה: <span style='color:{color}'>{recommendation}</span>", unsafe_allow_value=True)

# טבלת תרחישים
multiples = [target_pe * 0.8, target_pe, target_pe * 1.2]
table_data = []
for m in multiples:
    f_p = (future_profit * m) / num_shares
    c = ((f_p / price_input) ** (1/years) - 1) * 100 if price_input > 0 else 0
    table_data.append({
        "תרחיש": "שמרני" if m < target_pe else ("אופטימי" if m > target_pe else "ניטרלי (יעד)"),
        "מכפיל": round(m, 1),
        "מחיר צפוי": f"{f_p:,.2f}$",
        "תשואה שנתית (CAGR)": f"{c:.1f}%"
    })

st.table(pd.DataFrame(table_data))

st.sidebar.markdown("---")
st.sidebar.image(gen_qr("https://share.streamlit.io/"), caption="סרוק למעבר למובייל")
