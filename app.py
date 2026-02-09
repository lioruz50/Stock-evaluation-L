# --- בתוך החלק של הצגת נתוני המתחרים ---
st.markdown("---")
st.subheader("👥 השוואה למתחרים בתעשייה")

peers_df = get_peers_data(ticker)

if peers_df is not None and not peers_df.empty:
    # הצגת הטבלה
    st.table(peers_df.style.format({
        "מכפיל P/E": "{:.2f}",
        "שווי שוק (B)": "${:.2f}B"
    }))
    
    # חישוב ממוצע סקטוריאלי אמיתי מהמתחרים
    # מסננים מכפילים ששווים ל-0 או לא קיימים כדי לא להרוס את הממוצע
    valid_pes = peers_df[peers_df["מכפיל P/E"] > 0]["מכפיל P/E"]
    
    if not valid_pes.empty:
        avg_pe = valid_pes.mean()
        st.success(f"💡 מכפיל ה-P/E הממוצע של המתחרים הוא: **{avg_pe:.2f}**")
        
        # כפתור לעדכון אוטומטי של המודל
        if st.button("השתמש במכפיל הממוצע לחישוב השווי"):
            st.session_state['fair_multiple'] = avg_pe
            st.info("מכפיל היעד עודכן! בדוק את טבלת הערכת השווי למעלה.")
    else:
        st.warning("לא ניתן לחשב ממוצע (נתוני P/E חסרים עבור המתחרים).")
else:
    # הודעה ידידותית במקרה שאין נתונים (כפי שקרה אצלך בתמונה)
    st.info("לא נמצאו מתחרים ישירים (Peers) במאגר עבור סימול זה. מומלץ להזין מכפיל ידני לפי הסקטור הכללי.")
