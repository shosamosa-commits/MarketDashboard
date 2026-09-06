import math
import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# הגדרת תצורת עמוד Streamlit
st.set_page_config(page_title="Market Shift Dashboard", layout="wide", page_icon="🌌")

# ------------------ עיצוב גלובלי: Aurora כהה + זכוכית + טבעות ------------------
GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Rubik:wght@400;500;600;700;800&display=swap');

:root {
    --bg-base: #0a0e17;
    --glass-bg: rgba(255,255,255,0.045);
    --glass-border: rgba(255,255,255,0.09);
    --text-primary: #e8eaf1;
    --text-secondary: #93a0bd;
    --accent-purple: #8b5cf6;
    --accent-cyan: #22d3ee;
    --accent-green: #34d399;
    --accent-amber: #fbbf24;
    --accent-red: #f43f5e;
}

html, body, [class*="css"] {
    direction: rtl;
    text-align: right;
    font-family: 'Rubik', sans-serif !important;
}

/* --- רקע Aurora אנימטיבי --- */
.stApp {
    direction: rtl;
    background: var(--bg-base);
    position: relative;
    overflow-x: hidden;
}
.stApp::before {
    content: "";
    position: fixed;
    inset: 0;
    z-index: 0;
    pointer-events: none;
    background:
        radial-gradient(circle at 15% 20%, rgba(139,92,246,0.30) 0%, transparent 42%),
        radial-gradient(circle at 85% 15%, rgba(34,211,238,0.22) 0%, transparent 45%),
        radial-gradient(circle at 50% 90%, rgba(244,63,94,0.14) 0%, transparent 45%),
        radial-gradient(circle at 90% 80%, rgba(52,211,153,0.16) 0%, transparent 40%);
    background-size: 200% 200%;
    animation: auroraDrift 28s ease-in-out infinite alternate;
    filter: blur(10px);
}
@keyframes auroraDrift {
    0%   { background-position: 0% 0%, 100% 0%, 50% 100%, 100% 100%; }
    50%  { background-position: 20% 30%, 80% 20%, 40% 80%, 80% 70%; }
    100% { background-position: 5% 15%, 95% 10%, 60% 95%, 90% 90%; }
}
[data-testid="stAppViewContainer"], [data-testid="stMain"], [data-testid="stHeader"] {
    background: transparent !important;
}
[data-testid="stHeader"] { backdrop-filter: none; }
[data-testid="stAppViewContainer"] { position: relative; z-index: 1; }
.block-container { position: relative; z-index: 1; padding-top: 2rem; }

/* --- כותרת עליונה --- */
.hero-title {
    font-size: 2.1rem;
    font-weight: 800;
    background: linear-gradient(90deg, #ffffff 0%, var(--accent-purple) 55%, var(--accent-cyan) 100%);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    margin-bottom: 0.15rem;
}
.hero-caption {
    color: var(--text-secondary);
    font-size: 0.92rem;
    margin-bottom: 1.4rem;
}

/* --- טקסטים כלליים --- */
h1, h2, h3, h4, p, label, span, div { color: var(--text-primary); }
.stCaption, [data-testid="stCaptionContainer"] { color: var(--text-secondary) !important; }

/* --- כותרות: יישור לימין (RTL) --- */
[data-testid="stHeadingWithActionElements"] { direction: rtl; justify-content: flex-end; }
h1, h2, h3, h4, h5, h6 { text-align: right; width: 100%; }

/* --- כרטיסי זכוכית (containers עם border) --- */
div[data-testid="stVerticalBlockBorderWrapper"]:has(div[data-testid="stVerticalBlock"]) {
    background: var(--glass-bg);
    border: 1px solid var(--glass-border);
    border-radius: 20px;
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);
    box-shadow: 0 8px 32px rgba(0,0,0,0.35);
    transition: transform .25s ease, box-shadow .25s ease, border-color .25s ease;
}
div[data-testid="stVerticalBlockBorderWrapper"]:has(div[data-testid="stVerticalBlock"]):hover {
    border-color: rgba(139,92,246,0.45);
    box-shadow: 0 12px 40px rgba(139,92,246,0.18);
}

/* --- כפתורים מרחפים בסגנון Apple --- */
div[data-testid="stButton"] > button {
    background: linear-gradient(180deg, rgba(255,255,255,0.10), rgba(255,255,255,0.03));
    border: 1px solid var(--glass-border);
    color: var(--text-primary);
    border-radius: 999px;
    padding: 0.5rem 1.1rem;
    font-weight: 600;
    backdrop-filter: blur(10px);
    box-shadow: 0 4px 14px rgba(0,0,0,0.28);
    transition: transform .18s cubic-bezier(.2,.8,.2,1), box-shadow .18s ease, border-color .18s ease, background .18s ease;
}
div[data-testid="stButton"] > button:hover {
    transform: translateY(-3px) scale(1.02);
    border-color: rgba(139,92,246,0.55);
    box-shadow: 0 10px 26px rgba(139,92,246,0.28);
}
div[data-testid="stButton"] > button:active {
    transform: translateY(-1px) scale(0.99);
}
div[data-testid="stButton"] > button[kind="primary"] {
    background: linear-gradient(135deg, var(--accent-purple), var(--accent-cyan));
    border: none;
    color: #0a0e17;
    box-shadow: 0 8px 22px rgba(139,92,246,0.38);
}
div[data-testid="stButton"] > button[kind="primary"]:hover {
    box-shadow: 0 14px 30px rgba(139,92,246,0.5);
}

/* --- Metric --- */
[data-testid="stMetric"] { text-align: right; background: transparent; }
[data-testid="stMetricLabel"] { justify-content: flex-end; color: var(--text-secondary) !important; }
[data-testid="stMetricDelta"] svg { transform: scaleX(-1); }
[data-testid="stMetricValue"], [data-testid="stMetricDelta"] { direction: ltr; text-align: right; }

/* --- Expander / Alerts / Tabs --- */
[data-testid="stExpander"] {
    background: var(--glass-bg);
    border: 1px solid var(--glass-border);
    border-radius: 16px;
    backdrop-filter: blur(14px);
}
[data-testid="stAlertContainer"] {
    border-radius: 14px;
    border: 1px solid var(--glass-border);
    background: rgba(10,14,23,0.55) !important;
    border-inline-end: 4px solid var(--glass-border);
}
[data-testid="stAlertContainer"]:has(> [data-testid="stAlertContentSuccess"]) {
    border-inline-end-color: var(--accent-green) !important;
    box-shadow: inset 0 0 40px rgba(52,211,153,0.08);
}
[data-testid="stAlertContainer"]:has(> [data-testid="stAlertContentWarning"]) {
    border-inline-end-color: var(--accent-amber) !important;
    box-shadow: inset 0 0 40px rgba(251,191,36,0.09);
}
[data-testid="stAlertContainer"]:has(> [data-testid="stAlertContentError"]) {
    border-inline-end-color: var(--accent-red) !important;
    box-shadow: inset 0 0 40px rgba(244,63,94,0.10);
}
.stAlert [data-testid="stMarkdownContainer"] p { font-size: 1rem; }
.stAlert, .stMarkdown, .stCaption { text-align: right; }
.stTabs [data-baseweb="tab-list"] { direction: rtl; }

/* --- טבעות התקדמות (Apple Watch style) --- */
.ring-wrap { position: relative; display: inline-flex; align-items: center; justify-content: center; }
.ring-arc { transition: stroke-dashoffset 1.1s cubic-bezier(.2,.8,.2,1); }
.ring-center {
    position: absolute; inset: 0;
    display: flex; align-items: center; justify-content: center;
    flex-direction: column; line-height: 1.05;
}
.ring-value { font-weight: 700; direction: ltr; }
.ring-card {
    display: flex; flex-direction: column; align-items: center; gap: 0.35rem;
    padding: 0.4rem 0 0.2rem 0;
}
.ring-label { font-size: 1rem; font-weight: 700; color: var(--text-primary); text-align: center; }
.ring-delta { font-size: 0.9rem; font-weight: 700; direction: ltr; }
.ring-range { font-size: 0.78rem; font-weight: 600; color: var(--text-secondary); direction: ltr; opacity: 0.9; }

input, textarea { direction: ltr; }

/* --- Plotly: מונע מ-RTL הגלובלי לשבור את תוויות הצירים --- */
.js-plotly-plot, .js-plotly-plot .plotly, .js-plotly-plot .plot-container {
    direction: ltr;
}

/* --- כניסה מדורגת של הכרטיסים --- */
@keyframes cardFadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: translateY(0); }
}
div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
    animation: cardFadeIn 0.55s cubic-bezier(.2,.8,.2,1) both;
}
div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(1) { animation-delay: .05s; }
div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(2) { animation-delay: .10s; }
div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(3) { animation-delay: .15s; }
div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(4) { animation-delay: .20s; }
div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(5) { animation-delay: .25s; }

/* --- פעימת התראה עדינה למד הסיכון כשהסיכון גבוה --- */
@keyframes riskPulse {
    0%, 100% { filter: drop-shadow(0 0 6px rgba(244,63,94,0.35)); }
    50%      { filter: drop-shadow(0 0 16px rgba(244,63,94,0.75)); }
}
.risk-pulse .ring-arc { animation: riskPulse 2.2s ease-in-out infinite; }

/* --- פס גלילה בסגנון האתר --- */
::-webkit-scrollbar { width: 10px; height: 10px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, var(--accent-purple), var(--accent-cyan));
    border-radius: 8px;
    opacity: 0.6;
}
::-webkit-scrollbar-thumb:hover { background: var(--accent-cyan); }
* { scrollbar-color: #6d5bd0 transparent; scrollbar-width: thin; }
</style>
"""

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

st.markdown('<div class="hero-title">🚨 דשבורד ניטור שינוי כיוון בשוק (S&amp;P 500)</div>', unsafe_allow_html=True)
st.markdown(f'<div class="hero-caption">עדכון אחרון: {datetime.now().strftime("%Y-%m-%d %H:%M")}</div>', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["🚨 ניטור שינוי כיוון בשוק", "🔍 בחירת מניות"])

def ring_gauge(value_text, pct, ring_id, size=78, stroke=7,
                color_from="#8b5cf6", color_to="#22d3ee", font_size="1.0rem"):
    """טבעת התקדמות בסגנון Apple Watch — מציגה היכן הערך הנוכחי ביחס לטווח (0-1)."""
    pct = max(0.0, min(1.0, pct))
    r = (size - stroke) / 2
    c = 2 * math.pi * r
    offset = c * (1 - pct)
    center = size / 2
    return f"""
    <div class="ring-wrap" style="width:{size}px;height:{size}px;">
        <svg width="{size}" height="{size}" viewBox="0 0 {size} {size}">
            <defs>
                <linearGradient id="{ring_id}" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="{color_from}"/>
                    <stop offset="100%" stop-color="{color_to}"/>
                </linearGradient>
            </defs>
            <circle cx="{center}" cy="{center}" r="{r}" fill="none" stroke="rgba(255,255,255,0.09)" stroke-width="{stroke}"/>
            <circle cx="{center}" cy="{center}" r="{r}" fill="none" stroke="url(#{ring_id})" stroke-width="{stroke}"
                    stroke-linecap="round" stroke-dasharray="{c:.2f}" stroke-dashoffset="{offset:.2f}"
                    transform="rotate(-90 {center} {center})" class="ring-arc"
                    style="filter: drop-shadow(0 0 5px {color_to}77);"/>
        </svg>
        <div class="ring-center"><span class="ring-value" style="font-size:{font_size};">{value_text}</span></div>
    </div>
    """


def pct_in_range(series_window, value):
    lo, hi = series_window.min(), series_window.max()
    if hi == lo:
        return 0.5
    return (value - lo) / (hi - lo)

# ------------------ לשונית "בחירת מניות" — פונקציות עזר ------------------

@st.cache_data(ttl=300, show_spinner=False)
def search_symbols(query):
    """מחפש מניות/ניירות ערך דרך מנוע החיפוש של יאהו פייננס (כמו תיבת חיפוש ביאהו/גוגל)."""
    try:
        res = yf.Search(query, max_results=8)
        return [q for q in res.quotes if q.get("symbol") and q.get("quoteType") == "EQUITY"]
    except Exception:
        return []


@st.cache_data(ttl=1800, show_spinner=False)
def load_stock_history(symbol):
    t = yf.Ticker(symbol)
    hist = t.history(period="2y", auto_adjust=True)
    hist = hist.dropna(subset=["Close"])
    info = t.info
    return hist, info


@st.cache_data(ttl=21600, show_spinner=False)  # 6 שעות — נתוני ענף משתנים לאט
def get_industry_avg_pe(industry_key, exclude_symbol):
    """ממוצע P/E (trailing) של החברות המובילות באותו תת-ענף ביאהו פייננס, כתחליף ל'ממוצע הענף'."""
    try:
        top = yf.Industry(industry_key).top_companies
        peers = [s for s in top.index.tolist() if s != exclude_symbol][:8]
        pes = []
        for s in peers:
            try:
                pe = yf.Ticker(s).info.get("trailingPE")
                if pe and pe > 0:
                    pes.append(pe)
            except Exception:
                continue
        if not pes:
            return None, 0
        return sum(pes) / len(pes), len(pes)
    except Exception:
        return None, 0


def _price_change_pct(hist, days_back):
    target = hist.index.max() - pd.Timedelta(days=days_back)
    window = hist[hist.index <= target]
    if window.empty:
        return None
    base = float(window["Close"].iloc[-1])
    last = float(hist["Close"].iloc[-1])
    return ((last - base) / base * 100) if base else None


def compute_momentum(hist):
    """מומנטום מחיר: חודש / 3 חודשים / מתחילת השנה (YTD)."""
    last_ts = hist.index.max()
    year_start = pd.Timestamp(year=last_ts.year, month=1, day=1, tz=hist.index.tz)
    ytd_window = hist[hist.index >= year_start]
    ytd = None
    if not ytd_window.empty:
        base = float(ytd_window["Close"].iloc[0])
        last = float(hist["Close"].iloc[-1])
        ytd = ((last - base) / base * 100) if base else None
    return dict(m1=_price_change_pct(hist, 30), m3=_price_change_pct(hist, 91), ytd=ytd)


def compute_fibonacci(hist, lookback_days):
    """רמות פיבונאצי לפי שיא/שפל בטווח הנבחר. retracement=0 בשיא, 1 בשפל."""
    window = hist[hist.index >= hist.index.max() - pd.Timedelta(days=lookback_days)]
    if window.empty:
        return None
    swing_high = float(window["High"].max())
    swing_low = float(window["Low"].min())
    if swing_high == swing_low:
        return None
    current = float(hist["Close"].iloc[-1])
    retracement = max(0.0, min(1.0, (swing_high - current) / (swing_high - swing_low)))
    levels = [0.0, 0.236, 0.382, 0.5, 0.618, 0.786, 1.0]
    nearest = min(levels, key=lambda l: abs(l - retracement))
    return dict(swing_high=swing_high, swing_low=swing_low, current=current,
                retracement=retracement, nearest_level=nearest, levels=levels)


# הסברים לכל אחד מ-4 האינדיקטורים ללשונית "בחירת מניות"
STOCK_IND_INFO = {
    1: dict(
        name="1️⃣ מרחק מהממוצע הנע ל-150 יום (SMA150)",
        what="**מה לבדוק:** האם המחיר נסחר מעל או מתחת לממוצע הנע ל-150 יום, ובאיזה מרחק (באחוזים).",
        meaning="**משמעות מעשית:** מחיר מעל הממוצע ומתרחק ממנו = מגמת עלייה חזקה (אך גם מתוחה יותר). מחיר מתחת לממוצע = מגמת ירידה או תיקון ממושך.",
    ),
    2: dict(
        name="2️⃣ מומנטום מחיר — חודש / 3 חודשים / מתחילת השנה",
        what="**מה לבדוק:** שינוי המחיר באחוזים בשלושה טווחי זמן שונים — קצר (חודש), בינוני (3 חודשים) וממושך (YTD).",
        meaning="**משמעות מעשית:** מומנטום חיובי ועקבי בכל הטווחים מחזק את התמונה החיובית. פיצול בין הטווחים (למשל חיובי בטווח קצר אך שלילי מתחילת השנה) מרמז על שינוי מגמה.",
    ),
    3: dict(
        name="3️⃣ רווח למניה (P/E) מול ממוצע הענף",
        what="**מה לבדוק:** יחס מחיר/רווח (P/E) של החברה מול הממוצע בקרב החברות המובילות באותו תת-ענף ביאהו פייננס.",
        meaning="**משמעות מעשית:** P/E נמוך מהענף עשוי להעיד על מניה זולה יחסית לתחום שלה; P/E גבוה מהענף עשוי להעיד על תמחור יקר או על ציפיות צמיחה גבוהות. זהו אינדיקטור השוואתי בלבד, לא המלצת קנייה/מכירה.",
    ),
    4: dict(
        name="4️⃣ רמות פיבונאצי",
        what="**מה לבדוק:** היכן נמצא המחיר הנוכחי ביחס לרמות תיקון פיבונאצי (23.6%, 38.2%, 50%, 61.8%...) על טווח השיא/שפל שנבחר.",
        meaning="**משמעות מעשית:** מחיר קרוב לשיא הטווח (תיקון קטן) נחשב חזק יותר; מחיר שירד לרמות תיקון עמוקות (61.8% ומעלה) מתקרב לאזור שבו לרוב נבחנת התאוששות או המשך ירידה.",
    ),
}
STOCK_IND_SHORT = {1: "מרחק מ-SMA150", 2: "מומנטום מחיר", 3: "P/E מול הענף", 4: "רמת פיבונאצי"}



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

# תוויות קצרות לכרטיסי הסקאלה (השם המלא מופיע בפאנל הפירוט למטה)
IND_SHORT = {
    1: "מרחק מ-SMA150",
    2: "רוחב שוק — RSP",
    3: "VIX — סנטימנט",
    4: "רוטציה הגנתית",
    5: "Risk-On / Risk-Off",
}

with tab1:
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
        # ffill קודם: טיקר בודד עם עדכון מאוחר (למשל VIX) לא ימחק את כל שאר הטורים לאותו יום.
        # dropna בסוף מסיר רק את הימים המובילים שעדיין חסר להם נתון היסטורי.
        data = data.ffill().dropna()
        return data

    try:
        df = load_market_data()
        if df.empty or len(df) < 2:
            raise ValueError(
                "נתוני שוק חסרים או לא זמינים כרגע (ייתכן עומס/חסימה זמנית מול ספק הנתונים) — נסו לרענן בעוד כמה דקות"
            )

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

        # חלון 6 חודשים — משמש גם לגרפים וגם לסקאלות של הטבעות
        six_months_ago = df.index.max() - pd.Timedelta(days=182)
        df6 = df[df.index >= six_months_ago]

        # ------------------ תצוגת מד הסיכון הראשי ------------------
        st.subheader("📊 מד סיכון משוקלל לתיקון בשוק")

        if risk_score >= 4:
            score_colors = ("#f43f5e", "#fb7185")
            status_fn, status_text = st.error, "🚨 **רמת סיכון גבוהה:** הצטברו 4-5 סימנים לשינוי כיוון/תיקון מתקרב. מומלץ לנקוט בזהירות."
        elif risk_score >= 2:
            score_colors = ("#fbbf24", "#f59e0b")
            status_fn, status_text = st.warning, "⚠️ **רמת סיכון בינונית:** קיימים מספר איתותי אזהרה בשוק. כדאי לעקוב מקרוב."
        else:
            score_colors = ("#34d399", "#22d3ee")
            status_fn, status_text = st.success, "✅ **רמת סיכון נמוכה:** השוק מתנהג כסדרו, אין איתותי אזהרה קריטיים במקביל."

        with st.container(border=True):
            col_score, col_status = st.columns([1, 3], vertical_alignment="center")
            with col_score:
                ring_html = ring_gauge(f"{risk_score}/5", risk_score / 5, "mainRing",
                                        size=130, stroke=11,
                                        color_from=score_colors[0], color_to=score_colors[1],
                                        font_size="1.5rem")
                pulse_class = "risk-pulse" if risk_score >= 4 else ""
                st.markdown(
                    f'<div class="{pulse_class}" style="display:flex;flex-direction:column;align-items:center;gap:0.4rem;">'
                    f'{ring_html}<div class="ring-label">ציון אזהרה מצטבר</div></div>',
                    unsafe_allow_html=True,
                )
            with col_status:
                status_fn(status_text)

        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

        # ------------------ תצוגת 5 המדדים עם טבעות סקאלה ------------------
        st.subheader("📈 פירוט 5 המדדים")
        st.caption("הטבעת מציגה את מיקום הערך הנוכחי בתוך הטווח של 6 החודשים האחרונים — קרוב לקצה = קרוב לקיצון")

        if "selected_indicator" not in st.session_state:
            st.session_state.selected_indicator = 1

        def indicator_card(col, idx, ring_value_text, pct, delta_text, delta_color, series_window, raw_fmt):
            lo, hi = series_window.min(), series_window.max()
            with col:
                with st.container(border=True):
                    ring_html = ring_gauge(ring_value_text, pct, f"ring{idx}", size=78, stroke=7,
                                            color_from="#8b5cf6", color_to="#22d3ee", font_size="0.85rem")
                    delta_hex = "#f43f5e" if delta_color == "bad" else "#34d399"
                    st.markdown(
                        f'<div class="ring-card">'
                        f'{ring_html}'
                        f'<div class="ring-label">{IND_SHORT[idx]}</div>'
                        f'<div class="ring-delta" style="color:{delta_hex};">{delta_text}</div>'
                        f'<div class="ring-range">{raw_fmt(lo)} – {raw_fmt(hi)}</div>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                    st.button("🔎 פרטים", key=f"btn_ind_{idx}", width="stretch",
                              type="primary" if st.session_state.selected_indicator == idx else "secondary",
                              on_click=lambda i=idx: st.session_state.update(selected_indicator=i))

        c1, c2, c3, c4, c5 = st.columns(5)

        indicator_card(
            c1, 1, f"{dist_150:.1f}%", pct_in_range(df6['Dist_SMA150'], dist_150),
            f"{dist_150 - prev['Dist_SMA150']:+.2f}%", "bad" if (dist_150 - prev['Dist_SMA150']) > 0 else "good",
            df6['Dist_SMA150'], lambda v: f"{v:.1f}%",
        )
        indicator_card(
            c2, 2, f"{latest['RSP_SPX_Ratio']:.3f}", pct_in_range(df6['RSP_SPX_Ratio'], latest['RSP_SPX_Ratio']),
            "נחלש" if latest['RSP_SPX_Ratio'] < latest['RSP_Ratio_SMA20'] else "חזק",
            "bad" if latest['RSP_SPX_Ratio'] < latest['RSP_Ratio_SMA20'] else "good",
            df6['RSP_SPX_Ratio'], lambda v: f"{v:.3f}",
        )
        indicator_card(
            c3, 3, f"{vix_val:.1f}", pct_in_range(df6['^VIX'], vix_val),
            f"{vix_val - prev['^VIX']:+.2f}", "bad" if (vix_val - prev['^VIX']) > 0 else "good",
            df6['^VIX'], lambda v: f"{v:.0f}",
        )
        indicator_card(
            c4, 4, "מגננה" if latest['Defensive_Ratio'] > latest['Defensive_SMA10'] else "תקין",
            pct_in_range(df6['Defensive_Ratio'], latest['Defensive_Ratio']),
            "הגנתי" if latest['Defensive_Ratio'] > latest['Defensive_SMA10'] else "רגיל",
            "bad" if latest['Defensive_Ratio'] > latest['Defensive_SMA10'] else "good",
            df6['Defensive_Ratio'], lambda v: f"{v:.3f}",
        )
        indicator_card(
            c5, 5, "Risk-On" if latest['Risk_Appetite'] >= latest['Risk_Appetite_SMA10'] else "Risk-Off",
            pct_in_range(df6['Risk_Appetite'], latest['Risk_Appetite']),
            "Risk-On" if latest['Risk_Appetite'] >= latest['Risk_Appetite_SMA10'] else "Risk-Off",
            "good" if latest['Risk_Appetite'] >= latest['Risk_Appetite_SMA10'] else "bad",
            df6['Risk_Appetite'], lambda v: f"{v:.2f}",
        )

        # ------------------ פאנל גרף + הסבר לאינדיקטור הנבחר ------------------
        st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

        sel = st.session_state.selected_indicator
        info = IND_INFO[sel]

        with st.container(border=True):
            st.subheader(info["name"])
            st.markdown(info["what"])
            st.markdown(info["meaning"])
            st.caption("📅 תצוגה: 6 החודשים האחרונים")

            fig = go.Figure()

            if sel == 1:
                fig.add_trace(go.Scatter(x=df6.index, y=df6['GSPC_SMA150'], name="SMA 150",
                                          line=dict(color="#fbbf24", dash="dash")))
                fig.add_trace(go.Scatter(x=df6.index, y=df6['^GSPC'], name="S&P 500",
                                          line=dict(color="#22d3ee"), fill='tonexty',
                                          fillcolor='rgba(139,92,246,0.15)'))
                fig.add_annotation(text=f"מרחק נוכחי: {dist_150:.2f}%", showarrow=False,
                                    xref="paper", yref="paper", x=0.02, y=0.98,
                                    font=dict(size=14, color="#fbbf24"))

            elif sel == 2:
                fig.add_trace(go.Scatter(x=df6.index, y=df6['RSP_SPX_Ratio'], name="RSP/SPX",
                                          line=dict(color="#22d3ee")))
                fig.add_trace(go.Scatter(x=df6.index, y=df6['RSP_Ratio_SMA20'], name="ממוצע 20",
                                          line=dict(color="#93a0bd", dash="dot")))

            elif sel == 3:
                fig.add_trace(go.Scatter(x=df6.index, y=df6['^VIX'], name="VIX", line=dict(color="#f43f5e")))
                fig.add_hline(y=13.5, line_dash="dash", line_color="#fbbf24", annotation_text="שאננות (מתחת)")
                fig.add_hline(y=20.0, line_dash="dash", line_color="#34d399", annotation_text="פחד (הזדמנות)")

            elif sel == 4:
                fig.add_trace(go.Scatter(x=df6.index, y=df6['Defensive_Ratio'], name="XLP/SPX",
                                          line=dict(color="#8b5cf6")))
                fig.add_trace(go.Scatter(x=df6.index, y=df6['Defensive_SMA10'], name="ממוצע 10",
                                          line=dict(color="#93a0bd", dash="dot")))

            elif sel == 5:
                fig.add_trace(go.Scatter(x=df6.index, y=df6['Risk_Appetite'], name="XLY/XLP",
                                          line=dict(color="#34d399")))
                fig.add_trace(go.Scatter(x=df6.index, y=df6['Risk_Appetite_SMA10'], name="ממוצע 10",
                                          line=dict(color="#93a0bd", dash="dot")))

            fig.update_layout(
                height=420, margin=dict(l=55, r=20, t=20, b=20),
                legend=dict(orientation="h", yanchor="bottom", y=1.02),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#e8eaf1", family="Rubik, sans-serif"),
                xaxis=dict(gridcolor="rgba(255,255,255,0.07)", zerolinecolor="rgba(255,255,255,0.07)", automargin=True),
                yaxis=dict(gridcolor="rgba(255,255,255,0.07)", zerolinecolor="rgba(255,255,255,0.07)", automargin=True),
            )
            st.plotly_chart(fig, width="stretch")

    except Exception as e:
        st.error(f"שגיאה בטעינת הנתונים: {e}")

with tab2:
    st.subheader("🔍 אינדיקציות לבחירת מניות")
    st.caption("חיפוש מניה מכל בורסה בעולם (מבוסס יאהו פייננס) וניתוח 4 אינדיקטורים + סיכום קצר בוליש/בריש")

    with st.expander("💡 4 האינדיקטורים לבחירת מניות — מדריך מהיר"):
        st.markdown("""
**כלל מרכזי:** כל אינדיקטור בודד הוא רמז אחד בלבד — הסיכום למטה משקלל את כולם יחד, אך אינו תחליף לניתוח עצמאי ואינו המלצת השקעה.

1. מרחק מהממוצע הנע ל-150 יום (מעל/מתחת, ובאיזה מרחק)
2. מומנטום מחיר — חודש / 3 חודשים / מתחילת השנה
3. רווח למניה (P/E) בהשוואה לממוצע החברות המובילות באותו תת-ענף
4. רמות פיבונאצי — היכן נמצא המחיר ביחס לטווח השיא/שפל האחרון
""")

    query = st.text_input(
        "חיפוש מניה או נייר ערך (שם חברה או טיקר)",
        placeholder="לדוגמה: Apple, AAPL, Microsoft, טבע...",
        key="stock_pick_query",
    )

    selected_symbol = None
    selected_name = None

    if query and len(query.strip()) >= 2:
        with st.spinner("מחפש..."):
            matches = search_symbols(query.strip())
        if matches:
            def _fmt_match(i, matches=matches):
                m = matches[i]
                name = m.get("longname") or m.get("shortname") or ""
                return f"{m['symbol']} — {name} ({m.get('exchDisp', '')})"
            choice_idx = st.selectbox(
                "בחר/י מניה מתוך התוצאות", range(len(matches)),
                format_func=_fmt_match, key="stock_pick_choice",
            )
            selected_symbol = matches[choice_idx]["symbol"]
            selected_name = _fmt_match(choice_idx)
        else:
            st.warning("לא נמצאו תוצאות התואמות לחיפוש")

    if not selected_symbol:
        st.info("הקלד/י שם מניה או טיקר למעלה כדי להתחיל בניתוח")
    else:
        fib_label = st.radio(
            "טווח לחישוב רמות פיבונאצי", ["3 חודשים", "6 חודשים", "12 חודשים"],
            index=1, horizontal=True, key="fib_lookback",
        )
        fib_days = {"3 חודשים": 91, "6 חודשים": 182, "12 חודשים": 365}[fib_label]

        try:
            with st.spinner(f"טוען נתונים עבור {selected_symbol}..."):
                hist, info = load_stock_history(selected_symbol)

            if hist.empty or len(hist) < 30:
                st.error("אין מספיק נתוני מחיר עבור נייר ערך זה.")
            else:
                hist = hist.copy()
                hist["SMA150"] = hist["Close"].rolling(window=150).mean()
                last_close = float(hist["Close"].iloc[-1])
                last_sma150 = hist["SMA150"].iloc[-1]
                dist_150 = ((last_close - last_sma150) / last_sma150 * 100) if pd.notna(last_sma150) else None

                mom = compute_momentum(hist)
                mom_values = [v for v in (mom["m1"], mom["m3"], mom["ytd"]) if v is not None]
                fib = compute_fibonacci(hist, fib_days)

                industry_key = info.get("industryKey")
                stock_pe = info.get("trailingPE")
                industry_pe, n_peers = (None, 0)
                if industry_key and stock_pe:
                    with st.spinner("משווה לענף..."):
                        industry_pe, n_peers = get_industry_avg_pe(industry_key, selected_symbol)

                # ------------- ניקוד בוליש/בריש -------------
                bull_score, bear_score = 0, 0
                signal_notes = []

                if dist_150 is not None:
                    if last_close > last_sma150:
                        bull_score += 1
                        signal_notes.append("המחיר מעל ממוצע 150 יום")
                    else:
                        bear_score += 1
                        signal_notes.append("המחיר מתחת לממוצע 150 יום")

                if mom_values:
                    positive = sum(1 for v in mom_values if v > 0)
                    if positive > len(mom_values) / 2:
                        bull_score += 1
                        signal_notes.append("מומנטום המחיר חיובי ברוב הטווחים")
                    else:
                        bear_score += 1
                        signal_notes.append("מומנטום המחיר שלילי ברוב הטווחים")

                if stock_pe and industry_pe:
                    if stock_pe < industry_pe:
                        bull_score += 1
                        signal_notes.append("המניה נסחרת בזול יחסית לענף (P/E נמוך יותר)")
                    else:
                        bear_score += 1
                        signal_notes.append("המניה נסחרת ביוקר יחסית לענף (P/E גבוה יותר)")

                if fib is not None:
                    if fib["retracement"] <= 0.5:
                        bull_score += 1
                        signal_notes.append("המחיר קרוב לשיא הטווח שנבחר (תיקון קל בלבד)")
                    else:
                        bear_score += 1
                        signal_notes.append("המחיר קרוב לשפל הטווח שנבחר (תיקון עמוק)")

                total_signals = bull_score + bear_score
                diff = bull_score - bear_score

                st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

                if total_signals == 0:
                    st.warning("אין מספיק נתונים עבור נייר ערך זה כדי לחשב סיכום בוליש/בריש.")
                else:
                    if diff >= 2:
                        verdict_full, verdict_fn = "בוליש 🐂", st.success
                        v_colors = ("#34d399", "#22d3ee")
                    elif diff == 1:
                        verdict_full, verdict_fn = "נוטה לבוליש", st.success
                        v_colors = ("#34d399", "#a3e635")
                    elif diff == 0:
                        verdict_full, verdict_fn = "ניטרלי", st.warning
                        v_colors = ("#fbbf24", "#f59e0b")
                    elif diff == -1:
                        verdict_full, verdict_fn = "נוטה לבריש", st.warning
                        v_colors = ("#fb7185", "#fbbf24")
                    else:
                        verdict_full, verdict_fn = "בריש 🐻", st.error
                        v_colors = ("#f43f5e", "#fb7185")

                    with st.container(border=True):
                        col_score, col_status = st.columns([1, 3], vertical_alignment="center")
                        with col_score:
                            ring_html = ring_gauge(f"{bull_score}/{total_signals}", bull_score / total_signals,
                                                    "stockRing", size=130, stroke=11,
                                                    color_from=v_colors[0], color_to=v_colors[1], font_size="1.4rem")
                            st.markdown(
                                f'<div style="display:flex;flex-direction:column;align-items:center;gap:0.4rem;">'
                                f'{ring_html}<div class="ring-label">{verdict_full}</div></div>',
                                unsafe_allow_html=True,
                            )
                        with col_status:
                            bullets = "\n".join(f"- {n}" for n in signal_notes)
                            verdict_fn(f"**{selected_name or selected_symbol}**\n\n{bullets}")

                st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

                # ------------- כרטיסי 4 האינדיקטורים -------------
                st.subheader("📈 פירוט האינדיקטורים")
                if "selected_stock_indicator" not in st.session_state:
                    st.session_state.selected_stock_indicator = 1

                def stock_indicator_card(col, idx, ring_value_text, pct, delta_text, delta_color, raw_range_text):
                    with col:
                        with st.container(border=True):
                            ring_html = ring_gauge(ring_value_text, pct, f"stockind{idx}", size=78, stroke=7,
                                                    color_from="#8b5cf6", color_to="#22d3ee", font_size="0.85rem")
                            delta_hex = {"good": "#34d399", "bad": "#f43f5e"}.get(delta_color, "#93a0bd")
                            st.markdown(
                                f'<div class="ring-card">'
                                f'{ring_html}'
                                f'<div class="ring-label">{STOCK_IND_SHORT[idx]}</div>'
                                f'<div class="ring-delta" style="color:{delta_hex};">{delta_text}</div>'
                                f'<div class="ring-range">{raw_range_text}</div>'
                                f'</div>',
                                unsafe_allow_html=True,
                            )
                            st.button("🔎 פרטים", key=f"btn_stock_ind_{idx}", width="stretch",
                                      type="primary" if st.session_state.selected_stock_indicator == idx else "secondary",
                                      on_click=lambda i=idx: st.session_state.update(selected_stock_indicator=i))

                sc1, sc2, sc3, sc4 = st.columns(4)
                six_months_ago = hist.index.max() - pd.Timedelta(days=182)

                # 1. מרחק מ-SMA150
                dist_series_full = (hist["Close"] - hist["SMA150"]) / hist["SMA150"] * 100
                dist6_window = dist_series_full[hist.index >= six_months_ago].dropna()
                if dist_150 is not None and not dist6_window.empty:
                    stock_indicator_card(
                        sc1, 1, f"{dist_150:.1f}%", pct_in_range(dist6_window, dist_150),
                        "מעל הממוצע" if dist_150 > 0 else "מתחת לממוצע",
                        "good" if dist_150 > 0 else "bad",
                        f"{dist6_window.min():.1f}% – {dist6_window.max():.1f}%",
                    )
                else:
                    with sc1:
                        st.info("אין מספיק היסטוריה לחישוב SMA150")

                # 2. מומנטום
                mom_pct = (sum(1 for v in mom_values if v > 0) / len(mom_values)) if mom_values else 0.5
                mom_text = " / ".join(
                    f"{lbl} {v:+.1f}%" for lbl, v in zip(["חודש", "3ח׳", "YTD"], (mom["m1"], mom["m3"], mom["ytd"]))
                    if v is not None
                )
                stock_indicator_card(
                    sc2, 2, f"{mom['m3']:+.0f}%" if mom["m3"] is not None else "—", mom_pct,
                    "חיובי" if mom_pct > 0.5 else "שלילי", "good" if mom_pct > 0.5 else "bad",
                    mom_text or "אין נתונים",
                )

                # 3. P/E מול ענף
                if stock_pe and industry_pe:
                    pe_ratio = stock_pe / industry_pe
                    pe_pct = max(0.0, min(1.0, (pe_ratio - 0.4) / (1.6 - 0.4)))
                    stock_indicator_card(
                        sc3, 3, f"{stock_pe:.1f}", pe_pct,
                        "זול מהענף" if stock_pe < industry_pe else "יקר מהענף",
                        "good" if stock_pe < industry_pe else "bad",
                        f"ענף: {industry_pe:.1f} ({n_peers} חברות)",
                    )
                else:
                    with sc3:
                        st.info("אין נתוני P/E זמינים להשוואה")

                # 4. פיבונאצי
                if fib is not None:
                    stock_indicator_card(
                        sc4, 4, f"{fib['retracement']*100:.0f}%", fib["retracement"],
                        f"קרוב לרמת {fib['nearest_level']*100:.1f}%",
                        "bad" if fib["retracement"] > 0.5 else "good",
                        f"שפל {fib['swing_low']:.2f} – שיא {fib['swing_high']:.2f}",
                    )
                else:
                    with sc4:
                        st.info("אין מספיק נתונים לחישוב פיבונאצי")

                # ------------- פאנל פירוט + גרף לאינדיקטור הנבחר -------------
                st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
                sel2 = st.session_state.selected_stock_indicator
                info2 = STOCK_IND_INFO[sel2]

                with st.container(border=True):
                    st.subheader(info2["name"])
                    st.markdown(info2["what"])
                    st.markdown(info2["meaning"])

                    fig2 = go.Figure()
                    show_chart = True

                    if sel2 == 1:
                        h6 = hist[hist.index >= six_months_ago]
                        fig2.add_trace(go.Scatter(x=h6.index, y=h6["SMA150"], name="SMA 150",
                                                   line=dict(color="#fbbf24", dash="dash")))
                        fig2.add_trace(go.Scatter(x=h6.index, y=h6["Close"], name=selected_symbol,
                                                   line=dict(color="#22d3ee"), fill="tonexty",
                                                   fillcolor="rgba(139,92,246,0.15)"))

                    elif sel2 == 2:
                        labels = ["חודש", "3 חודשים", "מתחילת השנה"]
                        values = [mom["m1"], mom["m3"], mom["ytd"]]
                        colors = ["#34d399" if (v or 0) >= 0 else "#f43f5e" for v in values]
                        fig2.add_trace(go.Bar(x=labels, y=[v if v is not None else 0 for v in values],
                                               marker_color=colors,
                                               text=[f"{v:+.1f}%" if v is not None else "—" for v in values],
                                               textposition="outside"))

                    elif sel2 == 3:
                        if stock_pe and industry_pe:
                            fig2.add_trace(go.Bar(x=[selected_symbol, "ממוצע הענף"], y=[stock_pe, industry_pe],
                                                   marker_color=["#8b5cf6", "#93a0bd"],
                                                   text=[f"{stock_pe:.1f}", f"{industry_pe:.1f}"],
                                                   textposition="outside"))
                        else:
                            st.info("אין נתוני P/E זמינים להצגת גרף")
                            show_chart = False

                    elif sel2 == 4:
                        if fib is not None:
                            hfib = hist[hist.index >= hist.index.max() - pd.Timedelta(days=fib_days)]
                            fig2.add_trace(go.Scatter(x=hfib.index, y=hfib["Close"], name=selected_symbol,
                                                       line=dict(color="#22d3ee")))
                            for lvl in fib["levels"]:
                                price_at_level = fib["swing_high"] - lvl * (fib["swing_high"] - fib["swing_low"])
                                fig2.add_hline(y=price_at_level, line_dash="dot", line_color="#93a0bd",
                                               annotation_text=f"{lvl*100:.1f}%", annotation_position="right")
                        else:
                            st.info("אין מספיק נתונים לחישוב פיבונאצי")
                            show_chart = False

                    if show_chart:
                        fig2.update_layout(
                            height=420, margin=dict(l=55, r=55 if sel2 == 4 else 20, t=20, b=20),
                            legend=dict(orientation="h", yanchor="bottom", y=1.02),
                            paper_bgcolor="rgba(0,0,0,0)",
                            plot_bgcolor="rgba(0,0,0,0)",
                            font=dict(color="#e8eaf1", family="Rubik, sans-serif"),
                            xaxis=dict(gridcolor="rgba(255,255,255,0.07)", zerolinecolor="rgba(255,255,255,0.07)", automargin=True),
                            yaxis=dict(gridcolor="rgba(255,255,255,0.07)", zerolinecolor="rgba(255,255,255,0.07)", automargin=True),
                        )
                        st.plotly_chart(fig2, width="stretch")

        except Exception as e:
            st.error(f"שגיאה בטעינת נתונים עבור {selected_symbol}: {e}")
