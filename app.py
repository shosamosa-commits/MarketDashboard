import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# הגדרת תצורת עמוד Streamlit
st.set_page_config(page_title="Market Shift Dashboard", layout="wide")

# ------------------ הגנת PIN לכניסה לדשבורד ------------------
def check_pin():
    if st.session_state.get("authenticated"):
        return True

    st.title("🔒 כניסה לדשבורד")
    pin_input = st.text_input("הזן קוד גישה בן 4 ספרות", type="password", max_chars=4)

    if pin_input:
        if pin_input == st.secrets.get("APP_PIN"):
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("קוד שגוי, נסה שוב.")

    return False

if not check_pin():
    st.stop()

# יישור כללי של הממשק לימין (RTL) עבור עברית
st.markdown("""
    <style>
    html, body, [class*="css"] {
        direction: rtl;
        text-align: right;
    }
    .stApp {
        direction: rtl;
    }
    [data-testid="stMetric"] {
        text-align: right;
    }
    [data-testid="stMetricLabel"] {
        justify-content: flex-end;
    }
    [data-testid="stMetricDelta"] svg {
        transform: scaleX(-1);
    }
    [data-testid="stMetricValue"], [data-testid="stMetricDelta"] {
        direction: ltr;
        text-align: right;
    }
    .stTabs [data-baseweb="tab-list"] {
        direction: rtl;
    }
    .stAlert, .stMarkdown, .stCaption {
        text-align: right;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🚨 דשבורד ניטור שינוי כיוון בשוק (S&P 500)")
st.caption(f"עדכון אחרון: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

# הסברים לכל אחד מ-5 האינדיקטורים, מוצגים בלחיצה על המדד המתאים
IND_INFO = {
    1: dict(
        name="1️⃣ התרחקות מממוצע 150 (SMA150)",
        what="**מה לבדוק:** ככל שהמדד מתרחק יותר מדי כלפי מעלה מהממוצע הנע ל-150 יום, השוק נחשב מתוח יותר והסבירות לתיקון עולה.",
        meaning="**משמעות מעשית:** במצב מתוח, עליות פרבוליות בדרך כלל נרגעות והסיכון לירידה בטווח הקצר גדל.",
    ),
    2: dict(
        name="2️⃣ רוחב השוק (Market Breadth) — מדד RSP",
        what="**מה לבדוק:** השוואת מדד ה-S&P 500 השוויוני (RSP) מול ה-S&P 500 המשוקלל לפי שווי שוק.",
        meaning="**משמעות מעשית:** RSP עולה = ראלי בריא שמשתתפות בו הרבה מניות. RSP משנה כיוון למטה = אזהרה — פחות מניות דוחפות את השוק והעליות מתרכזות במעט חברות.",
    ),
    3: dict(
        name="3️⃣ סנטימנט — מדד הפחד VIX",
        what="**מה לבדוק:** רמת ה-VIX — נמוכה מדי (סביב 12–14) לעומת גבוהה (20–30 ומעלה).",
        meaning="**משמעות מעשית:** VIX נמוך מאוד = שאננות בציבור, כדאי להיזהר ולהתכונן לתיקון. VIX גבוה מאוד = פחד קיצוני, ולרוב זו הזדמנות קנייה.",
    ),
    4: dict(
        name="4️⃣ רוטציה לסקטורים הגנתיים (XLP/SPX)",
        what="**מה לבדוק:** קצב השינוי ביחס בין סקטור מוצרי הצריכה הבסיסיים (XLP) לבין S&P 500.",
        meaning="**משמעות מעשית:** כשהיחס עולה — סימן שכסף גדול/מוסדי מתחיל לחוש לחץ ועובר לנכסים בטוחים.",
    ),
    5: dict(
        name="5️⃣ תאבון לסיכון — התקפי מול הגנתי (XLY/XLP)",
        what="**מה לבדוק:** היחס בין צריכה מחזורית/מותרות (XLY) לצריכה בסיסית (XLP).",
        meaning="**משמעות מעשית:** גרף עולה = Risk-On (תאבון סיכון גבוה). גרף יורד = Risk-Off (התגוננות וחשש מתיקון).",
    ),
}

with st.expander("💡 5 הסימנים לזיהוי שינוי כיוון בשוק — מדריך מהיר"):
    st.markdown("""
**כלל מרכזי:** אין להסתמך על מדד יחיד כאיתות מכירה — יש לחפש הצטברות של מספר סימנים במקביל.

1. התרחקות מממוצע 150 (או 200)
2. רוחב השוק ומדד RSP
3. סנטימנט — מדד הפחד VIX
4. רוטציה לסקטורים הגנתיים (XLP/SPX)
5. תאבון לסיכון — התקפי מול הגנתי (XLY/XLP)

**קנה מידה לתיקונים ב-S&P 500:**
- ירידה של עד 2%–3%: רעש רקע נורמלי בשוק.
- נסיגה לאזור ממוצע 50: המבחן האמיתי הראשון לקונים (אזור תיקון בריא).
- נסיגה לאזור ממוצע 150 / 200: אזור תיקון משמעותי (8%–10%+) והזדמנות קנייה מרכזית.
""")

@st.cache_data(ttl=3600)  # שמירה במטמון לשעה
def load_market_data():
    tickers = ['^GSPC', 'RSP', '^VIX', 'XLP', 'XLY']
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    
    data = yf.download(tickers, start=start_date, end=end_date)['Close']
    data = data.dropna()  # מסיר שורות חלקיות (למשל יום המסחר הנוכחי שטרם נסגר)
    return data

try:
    df = load_market_data()
    
    # חישוב אינדיקטורים
    df['GSPC_SMA150'] = df['^GSPC'].rolling(window=150).mean()
    df['Dist_SMA150'] = ((df['^GSPC'] - df['GSPC_SMA150']) / df['GSPC_SMA150']) * 100
    
    df['RSP_SPX_Ratio'] = df['RSP'] / df['^GSPC']
    df['RSP_Ratio_SMA20'] = df['RSP_SPX_Ratio'].rolling(window=20).mean()
    
    df['Defensive_Ratio'] = df['XLP'] / df['^GSPC']
    df['Defensive_SMA10'] = df['Defensive_Ratio'].rolling(window=10).mean()
    
    df['Risk_Appetite'] = df['XLY'] / df['XLP']
    df['Risk_Appetite_SMA10'] = df['Risk_Appetite'].rolling(window=10).mean()

    # נתונים עדכניים ליום האחרון
    latest = df.iloc[-1]
    prev = df.iloc[-2]

    # ניקוד סיכון (Risk Score out of 5)
    risk_score = 0
    warnings = []

    # 1. התרחקות מממוצע 150
    dist_150 = latest['Dist_SMA150']
    if dist_150 > 6.0:
        risk_score += 1
        warnings.append("S&P 500 מתוח מדי מעל ממוצע 150")

    # 2. רוחב השוק (Breadth)
    if latest['RSP_SPX_Ratio'] < latest['RSP_Ratio_SMA20']:
        risk_score += 1
        warnings.append("מדד RSP נחלש ביחס ל-S&P 500 (רוחב שוק צר)")

    # 3. סנטימנט (VIX)
    vix_val = latest['^VIX']
    if vix_val < 13.5:
        risk_score += 1
        warnings.append("VIX נמוך מאוד – שאננות מוגזמת בשוק")

    # 4. רוטציה הגנתית (XLP/SPX)
    if latest['Defensive_Ratio'] > latest['Defensive_SMA10']:
        risk_score += 1
        warnings.append("זרימת כסף לסקטור ההגנתי (XLP)")

    # 5. תאבון לסיכון (XLY/XLP)
    if latest['Risk_Appetite'] < latest['Risk_Appetite_SMA10']:
        risk_score += 1
        warnings.append("ירידה בתאבון לסיכון (Risk-Off)")

    # ------------------ תצוגת מד הסיכון הראשי ------------------
    st.subheader("📊 מד סיכון משוקלל לתיקון בשוק")
    col_score, col_status = st.columns([1, 3])

    with col_score:
        st.metric("ציון אזהרה מצטבר", f"{risk_score} / 5")

    with col_status:
        if risk_score >= 4:
            st.error("🚨 **רמת סיכון גבוהה:** הצטברו 4-5 סימנים לשינוי כיוון/תיקון מתקרב. מומלץ לנקוט בזהירות.")
        elif risk_score >= 2:
            st.warning("⚠️ **רמת סיכון בינונית:** קיימים מספר איתותי אזהרה בשוק. כדאי לעקוב מקרוב.")
        else:
            st.success("✅ **רמת סיכון נמוכה:** השוק מתנהג כסדרו, אין איתותי אזהרה קריטיים במקביל.")

    st.markdown("---")

    # ------------------ תצוגת 5 המדדים בטורים (לחיצים) ------------------
    st.subheader("📈 פירוט 5 המדדים")
    st.caption("לחץ על הכפתור מתחת לכל מדד כדי לראות את הגרף וההסבר שלו")

    if "selected_indicator" not in st.session_state:
        st.session_state.selected_indicator = 1

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric("1. מרחק מ-SMA150", f"{dist_150:.2f}%",
              delta=f"{dist_150 - prev['Dist_SMA150']:.2f}%", delta_color="inverse")
    c1.button("🔎 פרטים", key="btn_ind_1", width="stretch",
              type="primary" if st.session_state.selected_indicator == 1 else "secondary",
              on_click=lambda: st.session_state.update(selected_indicator=1))

    c2.metric("2. יחס RSP/SPX", f"{latest['RSP_SPX_Ratio']:.4f}",
              delta="נחלש" if latest['RSP_SPX_Ratio'] < latest['RSP_Ratio_SMA20'] else "חזק",
              delta_color="normal" if latest['RSP_SPX_Ratio'] >= latest['RSP_Ratio_SMA20'] else "inverse")
    c2.button("🔎 פרטים", key="btn_ind_2", width="stretch",
              type="primary" if st.session_state.selected_indicator == 2 else "secondary",
              on_click=lambda: st.session_state.update(selected_indicator=2))

    c3.metric("3. VIX (פחד)", f"{vix_val:.2f}",
              delta=f"{vix_val - prev['^VIX']:.2f}", delta_color="inverse")
    c3.button("🔎 פרטים", key="btn_ind_3", width="stretch",
              type="primary" if st.session_state.selected_indicator == 3 else "secondary",
              on_click=lambda: st.session_state.update(selected_indicator=3))

    c4.metric("4. רוטציה הגנתית", "מגננה" if latest['Defensive_Ratio'] > latest['Defensive_SMA10'] else "תקין",
              delta_color="inverse" if latest['Defensive_Ratio'] > latest['Defensive_SMA10'] else "normal")
    c4.button("🔎 פרטים", key="btn_ind_4", width="stretch",
              type="primary" if st.session_state.selected_indicator == 4 else "secondary",
              on_click=lambda: st.session_state.update(selected_indicator=4))

    c5.metric("5. Risk-On/Off", "Risk-On" if latest['Risk_Appetite'] >= latest['Risk_Appetite_SMA10'] else "Risk-Off",
              delta_color="normal" if latest['Risk_Appetite'] >= latest['Risk_Appetite_SMA10'] else "inverse")
    c5.button("🔎 פרטים", key="btn_ind_5", width="stretch",
              type="primary" if st.session_state.selected_indicator == 5 else "secondary",
              on_click=lambda: st.session_state.update(selected_indicator=5))

    # ------------------ פאנל גרף + הסבר לאינדיקטור הנבחר ------------------
    st.markdown("---")

    sel = st.session_state.selected_indicator
    info = IND_INFO[sel]

    six_months_ago = df.index.max() - pd.Timedelta(days=182)
    df6 = df[df.index >= six_months_ago]

    with st.container(border=True):
        st.subheader(info["name"])
        st.markdown(info["what"])
        st.markdown(info["meaning"])
        st.caption("📅 תצוגה: 6 החודשים האחרונים")

        fig = go.Figure()

        if sel == 1:
            fig.add_trace(go.Scatter(x=df6.index, y=df6['GSPC_SMA150'], name="SMA 150",
                                      line=dict(color="orange", dash="dash")))
            fig.add_trace(go.Scatter(x=df6.index, y=df6['^GSPC'], name="S&P 500",
                                      line=dict(color="blue"), fill='tonexty',
                                      fillcolor='rgba(255,165,0,0.15)'))
            fig.add_annotation(text=f"מרחק נוכחי: {dist_150:.2f}%", showarrow=False,
                                xref="paper", yref="paper", x=0.02, y=0.98,
                                font=dict(size=14, color="orange"))

        elif sel == 2:
            fig.add_trace(go.Scatter(x=df6.index, y=df6['RSP_SPX_Ratio'], name="RSP/SPX",
                                      line=dict(color="teal")))
            fig.add_trace(go.Scatter(x=df6.index, y=df6['RSP_Ratio_SMA20'], name="ממוצע 20",
                                      line=dict(color="gray", dash="dot")))

        elif sel == 3:
            fig.add_trace(go.Scatter(x=df6.index, y=df6['^VIX'], name="VIX", line=dict(color="red")))
            fig.add_hline(y=13.5, line_dash="dash", line_color="orange", annotation_text="שאננות (מתחת)")
            fig.add_hline(y=20.0, line_dash="dash", line_color="green", annotation_text="פחד (הזדמנות)")

        elif sel == 4:
            fig.add_trace(go.Scatter(x=df6.index, y=df6['Defensive_Ratio'], name="XLP/SPX",
                                      line=dict(color="purple")))
            fig.add_trace(go.Scatter(x=df6.index, y=df6['Defensive_SMA10'], name="ממוצע 10",
                                      line=dict(color="gray", dash="dot")))

        elif sel == 5:
            fig.add_trace(go.Scatter(x=df6.index, y=df6['Risk_Appetite'], name="XLY/XLP",
                                      line=dict(color="green")))
            fig.add_trace(go.Scatter(x=df6.index, y=df6['Risk_Appetite_SMA10'], name="ממוצע 10",
                                      line=dict(color="gray", dash="dot")))

        fig.update_layout(height=420, margin=dict(l=20, r=20, t=20, b=20),
                           legend=dict(orientation="h", yanchor="bottom", y=1.02))
        st.plotly_chart(fig, width="stretch")

except Exception as e:
    st.error(f"שגיאה בטעינת הנתונים: {e}")