# Healthcare Spend Analysis Dashboard

## Purpose
An interactive Streamlit web application for exploring healthcare procurement spend data across a multi-hospital system. Built by a healthcare procurement analyst who has analyzed $296.5M in spend across 16 hospital systems. This is a portfolio piece — visual polish and professional presentation matter as much as functionality.

## Tech Stack
- Python 3.11+
- Streamlit for the web application
- Plotly Express for ALL charts (not matplotlib — Streamlit renders Plotly interactively)
- pandas for data manipulation

## Project Structure
```
healthcare-spend-dashboard/
├── CLAUDE.md
├── README.md
├── LICENSE
├── requirements.txt
├── .gitignore
├── app.py
├── data/
│   └── synthetic_spend_data.csv
├── utils/
│   ├── __init__.py
│   ├── data_processing.py
│   └── charts.py
├── .streamlit/
│   └── config.toml
└── screenshots/
    └── .gitkeep
```

## Commands
- Install: `pip install -r requirements.txt`
- Run app: `streamlit run app.py`
- App URL: http://localhost:8501

## Code Standards
- Use type hints on ALL function signatures and return types
- Use pathlib for all file paths
- Use st.cache_data decorator on all data loading functions
- Use st.columns for layout
- Docstrings: Google style, on every public function
- No inline comments unless explaining non-obvious domain logic
- No "TODO" or "FIXME" comments
- Imports: stdlib first, third-party second, local third, separated by blank lines
- Max line length: 88 characters
- Use f-strings for all string formatting

## Design Standards
THIS IS A PORTFOLIO PIECE. It must look professional, not like a default Streamlit demo.
- Color palette: Healthcare-appropriate blues and teals (#0e4d92, #1a73a7, #2196F3, #00897B, #4DB6AC)
- Use st.set_page_config with wide layout and custom page title/icon
- KPI cards: Use custom CSS — white background cards with subtle box shadows, large numbers, small labels
- Charts: Consistent color scheme across all charts, clean axis labels, no chart junk
- Sidebar: Clean filter layout with clear section headers
- Typography: Use markdown headers sparingly, let the data speak
- Spacing: Use st.divider() and vertical spacing to prevent visual clutter
- NO default Streamlit rainbow theme — configure a professional theme in config.toml

## Git Rules
- NEVER add "Co-Authored-By", "Generated with Claude", or any AI attribution to commit messages
- NEVER add emoji prefixes to commit messages
- Commit messages: imperative mood, concise, under 72 characters
- Examples: "Add interactive spend trend chart with category breakdown", "Style KPI cards with custom CSS"

## Domain Context
- Healthcare procurement spend categories: Orthopedics, Biomedical Equipment, Biologics, Surgical Supplies, Radiology, Clinical Engineering, Wound Care, Vascular
- PPI (Physician Preference Items) are high-cost items chosen by surgeons — typically 40-60% of supply spend
- GPO (Group Purchasing Organization) contracts offer volume-based pricing; "off-contract" purchases are usually more expensive
- Major vendors: Medtronic, Stryker, DePuy Synthes, Zimmer Biomet, Smith+Nephew, Sodexo, Agiliti, Integra LifeSciences, Teleflex, BD
- Hospital systems typically have 3-15 facilities with varying spend patterns
- Orthopedics and Biomedical Equipment are consistently the two largest spend categories