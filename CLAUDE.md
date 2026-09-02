# MarketDashboard

Streamlit dashboard (Hebrew, RTL) that scores S&P 500 trend-change risk from
5 technical indicators. Single file: `app.py`. No login/PIN gate — the
dashboard is open to anyone with the URL (removed 2026-09-02).

## Running locally

```bash
cd "/Users/yossilevi/Library/CloudStorage/OneDrive-InvestigationsDivision–ComputerForensics/yossi-personal/MarketDashboard"
source venv/bin/activate
streamlit run app.py
```

Opens `http://localhost:8501`. Keep the terminal open — closing it or Ctrl+C
kills the server and `localhost` stops responding. On the same Wi-Fi network,
other devices (e.g. iPhone) can reach it via the "Network URL" Streamlit
prints on startup.

## Deployment

- GitHub: `shosamosa-commits/MarketDashboard` (remote `origin`, branch `main`)
- Live on Streamlit Community Cloud: https://shosamosa-commits-marketdashboard-app-guipmf.streamlit.app/
- Streamlit Cloud auto-redeploys on every push to `main` (~1-2 min)
- `.streamlit/config.toml` sets the dark theme for the deployed app — unlike
  `secrets.toml`, this file **must** stay committed or the live site reverts
  to Streamlit's default light theme.

## Design system (added 2026-08-17)

Dark "aurora" theme, all defined inline in `GLOBAL_CSS` in `app.py`:

- Background: slow-drifting blurred radial gradients (`#0a0e17` base) behind
  glass-morphism cards (`backdrop-filter: blur`)
- Palette: purple `#8b5cf6`, cyan `#22d3ee`, green `#34d399`, amber `#fbbf24`,
  red `#f43f5e`
- Font: Rubik (Google Fonts `@import` in `GLOBAL_CSS`)
- `ring_gauge()` — Apple-Watch-style SVG progress ring, reused for the main
  risk score and each of the 5 indicator cards. Shows where the current
  value sits within its own 6-month min/max (`pct_in_range()`), not a
  fixed/arbitrary threshold.
- Buttons: floating glass pills, hover-lift; the active/selected indicator
  button gets a purple→cyan gradient fill
- Alert boxes (`st.success/warning/error`): styled via
  `[data-testid="stAlertContainer"]` with a solid accent-color border, not a
  translucent background fill (see gotchas below for why)
- Verified on an iPhone-sized viewport (390×844) — Streamlit's built-in
  column stacking handles the responsive layout; no extra breakpoint code
  needed

## Known gotchas (hit while building the redesign)

- **Plotly y-axis labels clipped**: left margin too small for 4-digit S&P
  prices cut off the leading digits. `automargin=True` alone did not fix
  it — needed an explicit `margin=dict(l=55, ...)`.
- **Fixed-position decorative background painted over all content**: a
  `position: fixed` aurora layer needs the actual content container
  (`.block-container` / `stAppViewContainer`) to have `position: relative`
  for its `z-index` to have any effect. Without it, `z-index` on a static
  element is ignored and the fixed layer wins.
- **Streamlit alert coloring**: the visible background lives on
  `[data-testid="stAlertContainer"]` (and further nested
  `stAlertContent{Success,Warning,Error}` divs), not the outer `.stAlert`.
  A low-opacity color wash there blends with the blurred aurora backdrop
  behind it and turns muddy/olive — a solid accent border reads much more
  cleanly against a busy animated background.
- Global `direction: rtl` (needed for the Hebrew UI) does not itself break
  Plotly rendering as long as margins are sized correctly — an earlier
  suspicion that RTL was clipping the axis was a red herring; it was the
  margin.

## Verifying UI changes

No project-specific run skill exists yet. To check a change visually:
Playwright isn't a permanent dependency — install it ad hoc in `venv`
(`pip install playwright && python -m playwright install chromium`), launch
`streamlit run app.py --server.headless true`, drive it with a small script
(navigate, screenshot), then uninstall Playwright again so it doesn't linger
in `requirements.txt`/`venv`.
