import streamlit as st
import yfinance as ticker_data
import pandas as pd

# פונקציה למשיכת נתונים מהאינטרנט
def get_live_data(ticker_symbol):
    try:
        stock = ticker_data.Ticker(ticker_symbol)
        info = stock.info
        
        # משיכת נתונים בסיסיים
        price = info.get('currentPrice', 0)
        market_cap = info.get('marketCap', 0) / 1e6  # המרה למיליונים
        
        # משיכת הכנסות (מהדוח השנתי האחרון)
        revenue = info.get('totalRevenue', 0) / 1e6  # המרה למיליונים
        
        return {
            "price": price,
            "market_cap": market_cap,
            "revenue": revenue,
            "symbol": ticker_symbol
        }
    except Exception as e:
        st.error(f"שגיאה במשיכת נתונים עבור {ticker_symbol}: {e}")
        return None

# --- כותרת האפליקציה ---
st.title("🚀 מודל הערכת שווי אוטומטי")

# --- סרגל צד (Sidebar) לנתוני בסיס ---
st.sidebar.header("נתוני בסיס (2026)")
ticker = st.sidebar.text_input("הזן סימול מניה (Ticker):", value="GOOG")

# כפתור רענון נתונים מהרשת
if st.sidebar.button("משוך נתונים מהאינטרנט"):
    live_data = get_live_data(ticker)
    if live_data:
        st.session_state['live_data'] = live_data

# שימוש בנתונים שנמשכו או בערכי ברירת מחדל
data = st.session_state.get('live_data', {"price": 333.34, "market_cap": 4024.0, "revenue": 402.0})

# תיבות קלט הניתנות לעריכה ידנית (עם ערכים אוטומטיים)
revenue_input = st.sidebar.number_input("הכנסות בסיס ($ מיליונים)", value=float(data['revenue']))
market_cap_input = st.sidebar.number_input("שווי שוק נוכחי ($ מיליונים)", value=float(data['market_cap']))
price_input = st.sidebar.number_input("($) מחיר מניה נוכחי", value=float(data['price']))

# --- פרמטרים לצמיחה (סליידרים) ---
st.sidebar.header("פרמטרים לצמיחה")
growth_rate = st.sidebar.slider("צמיחת הכנסות שנתית (%)", 0, 50, 12) / 100
profit_margin = st.sidebar.slider("שולי רווח נקי (%)", 0, 50, 35) / 100
discount_rate = st.sidebar.slider("שיעור היוון - Discount Rate (%)", 5, 20, 12) / 100

# --- חישובים ---
years = 5
future_revenue = revenue_input * ((1 + growth_rate) ** years)
future_net_profit = future_revenue * profit_margin

# יצירת טבלה לתצוגה
st.subheader(f"תחזית הכנסות ורווח: {ticker}")
df_forecast = pd.DataFrame({
    "שנה": [2026 + i for i in range(years + 1)],
    "הכנסות ($M)": [round(revenue_input * ((1 + growth_rate) ** i), 2) for i in range(years + 1)],
    "רווח נקי ($M)": [round((revenue_input * ((1 + growth_rate) ** i)) * profit_margin, 2) for i in range(years + 1)]
})
st.table(df_forecast)

# --- ניתוח שווי הוגן ---
st.subheader("ניתוח שווי הוגן לפי תרחישים")
multiples = [25, 30, 35]
scenarios = []

for m in multiples:
    future_market_cap = future_net_profit * m
    # חישוב מחיר מניה עתידי (מבוסס על מספר המניות הנוכחי)
    num_shares = market_cap_input / price_input
    future_price = future_market_cap / num_shares
    
    # היוון להיום
    fair_value_today = future_price / ((1 + discount_rate) ** years)
    margin_of_safety = (fair_value_today - price_input) / price_input * 100
    
    scenarios.append({
        "מכפיל": m,
        "שווי שוק 2030 ($M)": f"{future_market_cap:,.0f}",
        "מחיר מניה 2030": f"${future_price:,.2f}",
        "שווי הוגן להיום": f"${fair_value_today:,.2f}",
        "מרווח ביטחון": f"{margin_of_safety:.1f}%"
    })

st.table(pd.DataFrame(scenarios))
