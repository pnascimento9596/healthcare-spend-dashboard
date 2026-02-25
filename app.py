"""Healthcare Procurement Spend Analytics Dashboard."""
import streamlit as st

from utils.data_processing import (
    apply_filters,
    calculate_kpis,
    calculate_prior_period,
    load_data,
)
from utils.charts import (
    contract_type_by_category,
    facility_ppi_mix,
    monthly_spend_trend,
    off_contract_opportunities,
    spend_by_category,
    spend_by_facility,
    top_vendors_by_spend,
    vendor_treemap,
)

st.set_page_config(
    page_title="Healthcare Spend Analytics",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

CUSTOM_CSS = """
<style>
    /* KPI cards */
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] > div[data-testid="stVerticalBlockBorderWrapper"] > div > div[data-testid="stVerticalBlock"] > div.kpi-card {
        background: #ffffff;
        border-radius: 8px;
        padding: 20px 16px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        text-align: center;
    }
    .kpi-card {
        background: #ffffff;
        border-radius: 8px;
        padding: 20px 16px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        text-align: center;
    }
    .kpi-value {
        font-size: 28px;
        font-weight: 700;
        color: #1a1a2e;
        margin: 0;
        line-height: 1.2;
    }
    .kpi-label {
        font-size: 13px;
        color: #6b7280;
        margin: 4px 0 0 0;
        font-weight: 400;
    }
    .kpi-delta {
        font-size: 12px;
        margin: 4px 0 0 0;
    }
    .kpi-delta.positive {
        color: #10b981;
    }
    .kpi-delta.negative {
        color: #ef4444;
    }
    .kpi-delta.neutral {
        color: #6b7280;
    }
    .kpi-warning {
        color: #ef4444 !important;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Sidebar styling */
    .filter-count {
        background: #1a73a7;
        color: white;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 13px;
        display: inline-block;
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 8px 20px;
    }

    /* Section header */
    .section-header {
        font-size: 13px;
        font-weight: 600;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
    }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def _format_spend(value: float) -> str:
    """Format spend as $XX.XM or $XX.XK."""
    if value >= 1_000_000:
        return f"${value / 1_000_000:.1f}M"
    if value >= 1_000:
        return f"${value / 1_000:.1f}K"
    return f"${value:,.0f}"


def _format_delta(current: float, prior: float) -> tuple[str, str]:
    """Format KPI delta as string and CSS class."""
    if prior == 0:
        return "—", "neutral"
    pct_change = (current - prior) / prior * 100
    if pct_change > 0:
        return f"+{pct_change:.1f}%", "positive"
    if pct_change < 0:
        return f"{pct_change:.1f}%", "negative"
    return "0.0%", "neutral"


def _render_kpi_card(
    label: str,
    value: str,
    delta_text: str = "",
    delta_class: str = "neutral",
    extra_class: str = "",
) -> str:
    """Render a KPI card as HTML."""
    value_class = f"kpi-value {extra_class}".strip()
    delta_html = ""
    if delta_text:
        delta_html = (
            f'<p class="kpi-delta {delta_class}">'
            f"vs. prior period: {delta_text}</p>"
        )
    return (
        f'<div class="kpi-card">'
        f'<p class="{value_class}">{value}</p>'
        f'<p class="kpi-label">{label}</p>'
        f"{delta_html}"
        f"</div>"
    )


df_full = load_data()

# --- Sidebar Filters ---
with st.sidebar:
    st.markdown("### Filters")

    min_date = df_full["transaction_date"].min().date()
    max_date = df_full["transaction_date"].max().date()

    if "filter_reset" not in st.session_state:
        st.session_state["filter_reset"] = 0

    reset_key = st.session_state["filter_reset"]

    date_range = st.date_input(
        "Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        key=f"date_range_{reset_key}",
    )

    all_facilities = sorted(df_full["facility_name"].unique().tolist())
    selected_facilities = st.multiselect(
        "Facility",
        options=all_facilities,
        default=all_facilities,
        key=f"facilities_{reset_key}",
    )

    all_categories = sorted(
        df_full["spend_category"].unique().tolist()
    )
    selected_categories = st.multiselect(
        "Spend Category",
        options=all_categories,
        default=all_categories,
        key=f"categories_{reset_key}",
    )

    vendor_spend_order = (
        df_full.groupby("vendor_name")["total_amount"]
        .sum()
        .sort_values(ascending=False)
        .index.tolist()
    )
    selected_vendors = st.multiselect(
        "Vendor",
        options=vendor_spend_order,
        default=[],
        placeholder="All vendors",
        key=f"vendors_{reset_key}",
    )

    all_contract_types = sorted(
        df_full["contract_type"].unique().tolist()
    )
    selected_contracts = st.multiselect(
        "Contract Type",
        options=all_contract_types,
        default=[],
        placeholder="All contract types",
        key=f"contracts_{reset_key}",
    )

    ppi_only = st.checkbox(
        "PPI Only",
        value=False,
        key=f"ppi_{reset_key}",
    )

    # Count active filters
    active_filters = 0
    if isinstance(date_range, tuple) and len(date_range) == 2:
        if date_range[0] != min_date or date_range[1] != max_date:
            active_filters += 1
    if set(selected_facilities) != set(all_facilities):
        active_filters += 1
    if set(selected_categories) != set(all_categories):
        active_filters += 1
    if selected_vendors:
        active_filters += 1
    if selected_contracts:
        active_filters += 1
    if ppi_only:
        active_filters += 1

    if active_filters > 0:
        st.markdown(
            f'<span class="filter-count">'
            f"{active_filters} filter"
            f"{'s' if active_filters != 1 else ''} active"
            f"</span>",
            unsafe_allow_html=True,
        )

    if st.button("Reset All Filters", use_container_width=True):
        st.session_state["filter_reset"] = reset_key + 1
        st.rerun()

    st.divider()
    st.caption(
        "Data reflects synthetic procurement data modeled "
        "on real healthcare spend patterns."
    )

# Parse date range
if isinstance(date_range, tuple) and len(date_range) == 2:
    filter_date_range = (date_range[0], date_range[1])
else:
    filter_date_range = (min_date, max_date)

df_filtered = apply_filters(
    df_full,
    date_range=filter_date_range,
    facilities=selected_facilities if selected_facilities else None,
    categories=(
        selected_categories if selected_categories else None
    ),
    vendors=selected_vendors if selected_vendors else None,
    contract_types=(
        selected_contracts if selected_contracts else None
    ),
    ppi_only=ppi_only,
)

# --- Header ---
kpis = calculate_kpis(df_filtered)
prior_kpis = calculate_prior_period(
    df_full, filter_date_range[0], filter_date_range[1]
)

date_display_start = filter_date_range[0].strftime("%b %Y")
date_display_end = filter_date_range[1].strftime("%b %Y")

st.markdown("## Healthcare Procurement Spend Analytics")
st.markdown(
    f'<p style="color: #6b7280; margin-top: -10px; font-size: 15px;">'
    f"Multi-facility spend analysis across "
    f"{date_display_start} – {date_display_end} | "
    f"{kpis['transaction_count']:,} transactions"
    f"</p>",
    unsafe_allow_html=True,
)

# --- KPI Cards ---
kpi_cols = st.columns(5)

spend_delta_text, spend_delta_class = _format_delta(
    kpis["total_spend"], prior_kpis["total_spend"]
)
with kpi_cols[0]:
    st.markdown(
        _render_kpi_card(
            "Total Spend",
            _format_spend(kpis["total_spend"]),
            spend_delta_text,
            spend_delta_class,
        ),
        unsafe_allow_html=True,
    )

txn_delta_text, txn_delta_class = _format_delta(
    kpis["transaction_count"], prior_kpis["transaction_count"]
)
with kpi_cols[1]:
    st.markdown(
        _render_kpi_card(
            "Transactions",
            f"{kpis['transaction_count']:,}",
            txn_delta_text,
            txn_delta_class,
        ),
        unsafe_allow_html=True,
    )

with kpi_cols[2]:
    st.markdown(
        _render_kpi_card("Unique Vendors", str(kpis["unique_vendors"])),
        unsafe_allow_html=True,
    )

ppi_warning = "kpi-warning" if kpis["ppi_spend_pct"] > 50 else ""
with kpi_cols[3]:
    st.markdown(
        _render_kpi_card(
            "PPI Spend %",
            f"{kpis['ppi_spend_pct']:.1f}%",
            extra_class=ppi_warning,
        ),
        unsafe_allow_html=True,
    )

with kpi_cols[4]:
    st.markdown(
        _render_kpi_card(
            "Avg Transaction",
            f"${kpis['avg_transaction']:,.0f}",
        ),
        unsafe_allow_html=True,
    )

st.markdown("")

# --- Charts ---
if df_filtered.empty:
    st.warning("No data matches the current filters.")
    st.stop()

tab1, tab2, tab3, tab4 = st.tabs([
    "Spend Overview",
    "Vendor Analysis",
    "Facility Comparison",
    "Contract Analysis",
])

with tab1:
    col1, col2 = st.columns([1, 1.5])
    with col1:
        st.plotly_chart(
            spend_by_category(df_filtered),
            use_container_width=True,
        )
    with col2:
        st.plotly_chart(
            monthly_spend_trend(df_filtered),
            use_container_width=True,
        )

with tab2:
    col1, col2 = st.columns([1.2, 1])
    with col1:
        st.plotly_chart(
            top_vendors_by_spend(df_filtered),
            use_container_width=True,
        )
    with col2:
        st.plotly_chart(
            vendor_treemap(df_filtered),
            use_container_width=True,
        )

with tab3:
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(
            spend_by_facility(df_filtered),
            use_container_width=True,
        )
    with col2:
        st.plotly_chart(
            facility_ppi_mix(df_filtered),
            use_container_width=True,
        )

with tab4:
    col1, col2 = st.columns([1.2, 1])
    with col1:
        st.plotly_chart(
            contract_type_by_category(df_filtered),
            use_container_width=True,
        )
    with col2:
        st.markdown(
            '<p class="section-header">'
            "Off-Contract Spend Opportunities"
            "</p>",
            unsafe_allow_html=True,
        )
        st.caption(
            "Categories with >20% off-contract spend represent "
            "potential savings from contract renegotiation."
        )
        opp_df = off_contract_opportunities(df_filtered)
        if opp_df.empty:
            st.info(
                "No categories exceed the 20% off-contract threshold "
                "in the current filter selection."
            )
        else:
            opp_display = opp_df.copy()
            opp_display["Total Category Spend"] = opp_display[
                "Total Category Spend"
            ].apply(lambda v: f"${v:,.0f}")
            opp_display["Off-Contract Spend"] = opp_display[
                "Off-Contract Spend"
            ].apply(lambda v: f"${v:,.0f}")
            opp_display["Off-Contract %"] = opp_display[
                "Off-Contract %"
            ].apply(lambda v: f"{v:.1f}%")
            st.dataframe(
                opp_display,
                use_container_width=True,
                hide_index=True,
            )

# --- Data Explorer ---
st.divider()

with st.expander("View Transaction Detail"):
    st.dataframe(
        df_filtered.sort_values(
            "transaction_date", ascending=False
        ).reset_index(drop=True),
        use_container_width=True,
        height=400,
    )

    csv_data = df_filtered.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download Filtered Data as CSV",
        data=csv_data,
        file_name="healthcare_spend_filtered.csv",
        mime="text/csv",
    )
