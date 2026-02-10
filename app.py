import streamlit as st
import yfinance as yf
import pandas as pd

# --- 1. הגדרות דף ---
st.set_page_config(page_title="Value Model", layout="wide")

# שימוש בעיצוב רקע עדין ונעים לעיניים
st.markdown("""
    <style>
    .stApp {
        background-color: #f8f9fa;
    }
    </style>
    """, unsafe_allow_value=True)

# --- 2. פונקציות עזר ---
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
            "pe_ratio": info.get('trailingPE', 25.0)
        }
    except:
        return None

# --- 3. אבטחה ---
if "password_correct" not in st.session_state:
    st.session_state["password_correct"] = False

if not st.session_state["password_correct"]:
    st.title("🔒 כניסה למערכת")
    pwd = st.text_input("הזן סיסמה:", type="password")
    if st.button("כניסה") and pwd == "3535":
        st.session_state["password_correct"] = True
        st.rerun()
    st.stop()

# --- 4. ממשק ראשי ---
st.title("📊 מודל הערכת שווי והמלצת קנייה")

ticker = st.text_input("🔍 (Ticker) הזן סימול מניה:", value="META").upper()

if st.button("משוך נתונים עדכניים"):
    with st.spinner('מושך נתונים...'):
        data = get_company_data(ticker)
        if data:
            st.session_state['stock_data'] = data
        else:
            st.error("לא נמצאו נתונים עבור הסימול שהוזן.")

# נתוני ברירת מחדל (Meta לפי האקסל שלך)
current_data = st.session_state.get('stock_data', {
    "name": "Meta Platforms, Inc.", "price": 649.5, "market_cap": 1637000.0, 
    "revenue": 200000.0, "pe_ratio": 25.0
})

st.subheader(f"ניתוח עבור: {current_data['name']}")

# --- 5. סרגל צד (הגדרות האקסל) ---
st.sidebar.header("⚙️ פרמטרים להערכה")
target_pe = st.sidebar.number_input("מכפיל רווח יעד (P/E)", value=float(current_data['pe_ratio']))
growth_rate = st.sidebar.slider("צמיחה שנתית (%)", 0, 50, 14) / 100 # 14% לפי האקסל
profit_margin = st.sidebar.slider("שולי רווח נקי (%)", 0, 50, 35) / 100 # 35% לפי האקסל
discount_rate = st.sidebar.slider("שיעור היוון (WACC) %", 5, 20, 12) / 100

st.sidebar.markdown("---")
st.sidebar.header("📝 עריכת נתוני שוק")
rev_input = st.sidebar.number_input("הכנסות (במיליונים)", value=float(current_data['revenue']))
mc_input = st.sidebar.number_input("שווי שוק (במיליונים)", value=float(current_data['market_cap']))
price_input = st.sidebar.number_input("מחיר מניה נוכחי", value=float(current_data['price']))

# --- 6. חישובים ---
years = 5
future_rev = rev_input * ((1 + growth_rate) ** years)
future_profit = future_rev * profit_margin
num_shares = mc_input / price_input if price_input > 0 else 1

# תרחיש ניטרלי (לפי המכפיל שנבחר)
f_mc_neutral = future_profit * target_pe
f_price_neutral = f_mc_neutral / num_shares
fair_today = f_price_neutral / ((1 + discount_rate) ** years)
mos = (fair_today - price_input) / price_input * 100
cagr_neutral = ((f_price_neutral / price_input) ** (1/years) - 1) * 100 if price_input > 0 else 0

# המלצה
if mos > 15:
    recommendation, rec_color = "✅ קנייה חזקה (Strong Buy)", "green"
elif mos > 0:
    recommendation, rec_color = "🟡 החזק/קנייה מתונה (Hold/Buy)", "orange"
else:
    recommendation, rec_color = "❌ מכירה/המתנה (Overvalued)", "red"

# --- 7. תצוגת תוצאות מרכזית ---
col1, col2, col3 = st.columns(3)
col1.metric("מחיר נוכחי", f"${price_input:,.2f}")
col2.metric("מחיר יעד 2030", f"${f_price_neutral:,.2f}", f"{cagr_neutral:.1f}% CAGR")
col3.metric("שווי הוגן היום", f"${fair_today:,.2f}", f"{mos:.1f}% Margin")

st.markdown(f"### המלצה: :{rec_color}[{recommendation}]")

# טבלת תרחישים (ללא שורת ה-Total Profit שהוסרה)
st.write("---")
multiples = [target_pe * 0.8, target_pe, target_pe * 1.2]
results = []
for m in multiples:
    f_p = (future_profit * m) / num_shares
    c = ((f_p / price_input) ** (1/years) - 1) * 100 if price_input > 0 else 0
    results.append({
        "תרחיש": "שמרני" if m < target_pe else ("אופטימי" if m > target_pe else "ניטרלי"),
        "מכפיל": round(m, 1),
        "מחיר צפוי": f"{f_p:,.2f}$",
        "תשואה שנתית (CAGR)": f"{c:.1f}%"
    })

st.table(pd.DataFrame(results))
