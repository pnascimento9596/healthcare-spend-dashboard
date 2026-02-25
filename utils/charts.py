"""Plotly chart functions for the healthcare spend dashboard."""
import plotly.express as px
import plotly.graph_objects as go

import pandas as pd


HEALTHCARE_COLORS = [
    "#0e4d92",
    "#1a73a7",
    "#2196F3",
    "#00897B",
    "#4DB6AC",
    "#26A69A",
    "#5C6BC0",
    "#7986CB",
    "#42A5F5",
    "#80CBC4",
]

CONTRACT_COLORS = {
    "GPO": "#1a73a7",
    "Local": "#4DB6AC",
    "Off-Contract": "#ef5350",
}

LAYOUT_DEFAULTS = dict(
    font=dict(family="Inter, sans-serif", size=13, color="#1a1a2e"),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=20, r=20, t=40, b=20),
    hoverlabel=dict(
        bgcolor="white",
        font_size=13,
        font_family="Inter, sans-serif",
    ),
)


def _format_dollars(value: float) -> str:
    """Format a dollar value for display on charts."""
    if value >= 1_000_000:
        return f"${value / 1_000_000:.1f}M"
    if value >= 1_000:
        return f"${value / 1_000:.0f}K"
    return f"${value:,.0f}"


def spend_by_category(df: pd.DataFrame) -> go.Figure:
    """Create a horizontal bar chart of spend by category.

    Args:
        df: Filtered DataFrame.

    Returns:
        Plotly Figure with horizontal bars sorted descending.
    """
    cat_spend = (
        df.groupby("spend_category", as_index=False)["total_amount"]
        .sum()
        .sort_values("total_amount", ascending=True)
    )

    fig = go.Figure(
        go.Bar(
            x=cat_spend["total_amount"],
            y=cat_spend["spend_category"],
            orientation="h",
            marker_color=HEALTHCARE_COLORS[1],
            text=[
                _format_dollars(v) for v in cat_spend["total_amount"]
            ],
            textposition="outside",
            textfont=dict(size=12, color="#1a1a2e"),
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Spend: $%{x:,.0f}<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        **LAYOUT_DEFAULTS,
        title=dict(
            text="Spend by Category",
            font=dict(size=16, color="#1a1a2e"),
        ),
        xaxis=dict(
            showgrid=False,
            showticklabels=False,
            zeroline=False,
        ),
        yaxis=dict(showgrid=False),
        height=400,
    )

    return fig


def monthly_spend_trend(df: pd.DataFrame) -> go.Figure:
    """Create a stacked area chart of monthly spend by category.

    Args:
        df: Filtered DataFrame.

    Returns:
        Plotly Figure with stacked area chart.
    """
    df_monthly = (
        df.assign(
            month=df["transaction_date"].dt.to_period("M").dt.to_timestamp()
        )
        .groupby(["month", "spend_category"], as_index=False)[
            "total_amount"
        ]
        .sum()
    )

    cat_order = (
        df.groupby("spend_category")["total_amount"]
        .sum()
        .sort_values(ascending=False)
        .index.tolist()
    )

    fig = px.area(
        df_monthly,
        x="month",
        y="total_amount",
        color="spend_category",
        category_orders={"spend_category": cat_order},
        color_discrete_sequence=HEALTHCARE_COLORS,
    )

    fig.update_layout(
        **LAYOUT_DEFAULTS,
        title=dict(
            text="Monthly Spend Trend",
            font=dict(size=16, color="#1a1a2e"),
        ),
        xaxis=dict(
            title="",
            showgrid=False,
            dtick="M2",
            tickformat="%b %Y",
        ),
        yaxis=dict(
            title="",
            showgrid=True,
            gridcolor="rgba(0,0,0,0.06)",
            tickprefix="$",
            tickformat=",.0s",
        ),
        legend=dict(
            title="",
            orientation="h",
            yanchor="top",
            y=-0.15,
            xanchor="center",
            x=0.5,
            font=dict(size=11),
        ),
        height=450,
    )

    fig.update_traces(
        hovertemplate="<b>%{x|%b %Y}</b><br>$%{y:,.0f}<extra></extra>",
        line=dict(width=0.5),
    )

    return fig


def top_vendors_by_spend(df: pd.DataFrame, top_n: int = 15) -> go.Figure:
    """Create a horizontal stacked bar of top vendors by contract type.

    Args:
        df: Filtered DataFrame.
        top_n: Number of top vendors to show.

    Returns:
        Plotly Figure with stacked horizontal bars.
    """
    vendor_total = (
        df.groupby("vendor_name")["total_amount"]
        .sum()
        .nlargest(top_n)
        .index.tolist()
    )

    df_top = df[df["vendor_name"].isin(vendor_total)]
    vendor_contract = (
        df_top.groupby(
            ["vendor_name", "contract_type"], as_index=False
        )["total_amount"]
        .sum()
    )

    vendor_order = (
        df_top.groupby("vendor_name")["total_amount"]
        .sum()
        .sort_values(ascending=True)
        .index.tolist()
    )

    fig = go.Figure()

    for ct in ["GPO", "Local", "Off-Contract"]:
        ct_data = vendor_contract[
            vendor_contract["contract_type"] == ct
        ]
        ct_data = ct_data.set_index("vendor_name").reindex(
            vendor_order, fill_value=0
        )

        fig.add_trace(
            go.Bar(
                y=ct_data.index,
                x=ct_data["total_amount"],
                name=ct,
                orientation="h",
                marker_color=CONTRACT_COLORS[ct],
                hovertemplate=(
                    "<b>%{y}</b><br>"
                    f"{ct}: " + "$%{x:,.0f}<extra></extra>"
                ),
            )
        )

    total_by_vendor = (
        df_top.groupby("vendor_name")["total_amount"]
        .sum()
        .reindex(vendor_order)
    )
    fig.add_trace(
        go.Scatter(
            y=vendor_order,
            x=total_by_vendor.values,
            mode="text",
            text=[_format_dollars(v) for v in total_by_vendor.values],
            textposition="middle right",
            textfont=dict(size=11, color="#1a1a2e"),
            showlegend=False,
            hoverinfo="skip",
        )
    )

    fig.update_layout(
        **LAYOUT_DEFAULTS,
        barmode="stack",
        title=dict(
            text=f"Top {top_n} Vendors by Spend",
            font=dict(size=16, color="#1a1a2e"),
        ),
        xaxis=dict(
            showgrid=False,
            showticklabels=False,
            zeroline=False,
            range=[0, total_by_vendor.max() * 1.18],
        ),
        yaxis=dict(showgrid=False),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.05,
            xanchor="center",
            x=0.5,
        ),
        height=500,
    )

    return fig


def vendor_treemap(df: pd.DataFrame) -> go.Figure:
    """Create a treemap showing vendor share of total spend.

    Args:
        df: Filtered DataFrame.

    Returns:
        Plotly Figure with treemap visualization.
    """
    vendor_spend = (
        df.groupby("vendor_name", as_index=False)["total_amount"]
        .sum()
        .sort_values("total_amount", ascending=False)
    )
    total = vendor_spend["total_amount"].sum()
    vendor_spend["pct"] = vendor_spend["total_amount"] / total * 100
    vendor_spend["label"] = vendor_spend.apply(
        lambda r: (
            f"{r['vendor_name']}<br>"
            f"{_format_dollars(r['total_amount'])} "
            f"({r['pct']:.1f}%)"
        ),
        axis=1,
    )

    fig = px.treemap(
        vendor_spend,
        path=["label"],
        values="total_amount",
        color="total_amount",
        color_continuous_scale=[
            HEALTHCARE_COLORS[4],
            HEALTHCARE_COLORS[1],
            HEALTHCARE_COLORS[0],
        ],
    )

    fig.update_layout(
        **LAYOUT_DEFAULTS,
        title=dict(
            text="Vendor Concentration",
            font=dict(size=16, color="#1a1a2e"),
        ),
        coloraxis_showscale=False,
        height=500,
    )

    fig.update_traces(
        textfont=dict(size=12),
        hovertemplate="<b>%{label}</b><extra></extra>",
    )

    return fig


def spend_by_facility(df: pd.DataFrame) -> go.Figure:
    """Create a grouped bar chart of spend by facility and category.

    Args:
        df: Filtered DataFrame.

    Returns:
        Plotly Figure with grouped bars.
    """
    fac_cat = (
        df.groupby(
            ["facility_name", "spend_category"], as_index=False
        )["total_amount"]
        .sum()
    )

    cat_order = (
        df.groupby("spend_category")["total_amount"]
        .sum()
        .sort_values(ascending=False)
        .index.tolist()
    )

    fac_order = (
        df.groupby("facility_name")["total_amount"]
        .sum()
        .sort_values(ascending=False)
        .index.tolist()
    )

    fig = px.bar(
        fac_cat,
        x="facility_name",
        y="total_amount",
        color="spend_category",
        category_orders={
            "spend_category": cat_order,
            "facility_name": fac_order,
        },
        color_discrete_sequence=HEALTHCARE_COLORS,
        barmode="stack",
    )

    fig.update_layout(
        **LAYOUT_DEFAULTS,
        title=dict(
            text="Spend by Facility",
            font=dict(size=16, color="#1a1a2e"),
        ),
        xaxis=dict(title="", showgrid=False, tickangle=-20),
        yaxis=dict(
            title="",
            showgrid=True,
            gridcolor="rgba(0,0,0,0.06)",
            tickprefix="$",
            tickformat=",.0s",
        ),
        legend=dict(
            title="",
            orientation="h",
            yanchor="top",
            y=-0.25,
            xanchor="center",
            x=0.5,
            font=dict(size=11),
        ),
        height=450,
    )

    fig.update_traces(
        hovertemplate=(
            "<b>%{x}</b><br>$%{y:,.0f}<extra></extra>"
        ),
    )

    return fig


def facility_ppi_mix(df: pd.DataFrame) -> go.Figure:
    """Create a grouped bar showing PPI vs non-PPI spend per facility.

    Args:
        df: Filtered DataFrame.

    Returns:
        Plotly Figure with grouped bars.
    """
    df_ppi = df.copy()
    df_ppi["ppi_label"] = df_ppi["ppi_flag"].map(
        {True: "PPI", False: "Non-PPI"}
    )

    fac_ppi = (
        df_ppi.groupby(
            ["facility_name", "ppi_label"], as_index=False
        )["total_amount"]
        .sum()
    )

    fac_order = (
        df.groupby("facility_name")["total_amount"]
        .sum()
        .sort_values(ascending=False)
        .index.tolist()
    )

    fig = px.bar(
        fac_ppi,
        x="facility_name",
        y="total_amount",
        color="ppi_label",
        category_orders={
            "facility_name": fac_order,
            "ppi_label": ["PPI", "Non-PPI"],
        },
        color_discrete_map={
            "PPI": "#ef5350",
            "Non-PPI": "#1a73a7",
        },
        barmode="group",
    )

    fig.update_layout(
        **LAYOUT_DEFAULTS,
        title=dict(
            text="Facility PPI Mix",
            font=dict(size=16, color="#1a1a2e"),
        ),
        xaxis=dict(title="", showgrid=False, tickangle=-20),
        yaxis=dict(
            title="",
            showgrid=True,
            gridcolor="rgba(0,0,0,0.06)",
            tickprefix="$",
            tickformat=",.0s",
        ),
        legend=dict(
            title="",
            orientation="h",
            yanchor="top",
            y=-0.25,
            xanchor="center",
            x=0.5,
        ),
        height=450,
    )

    fig.update_traces(
        hovertemplate=(
            "<b>%{x}</b><br>$%{y:,.0f}<extra></extra>"
        ),
    )

    return fig


def contract_type_by_category(df: pd.DataFrame) -> go.Figure:
    """Create a 100% stacked bar of contract mix per category.

    Args:
        df: Filtered DataFrame.

    Returns:
        Plotly Figure with 100% stacked horizontal bars.
    """
    cat_contract = (
        df.groupby(
            ["spend_category", "contract_type"], as_index=False
        )["total_amount"]
        .sum()
    )

    cat_totals = (
        cat_contract.groupby("spend_category")["total_amount"]
        .transform("sum")
    )
    cat_contract["pct"] = cat_contract["total_amount"] / cat_totals * 100

    cat_order = (
        df.groupby("spend_category")["total_amount"]
        .sum()
        .sort_values(ascending=True)
        .index.tolist()
    )

    fig = go.Figure()

    for ct in ["GPO", "Local", "Off-Contract"]:
        ct_data = cat_contract[cat_contract["contract_type"] == ct]
        ct_data = ct_data.set_index("spend_category").reindex(
            cat_order
        )

        fig.add_trace(
            go.Bar(
                y=ct_data.index,
                x=ct_data["pct"],
                name=ct,
                orientation="h",
                marker_color=CONTRACT_COLORS[ct],
                text=ct_data["pct"].apply(lambda v: f"{v:.0f}%"),
                textposition="inside",
                textfont=dict(color="white", size=11),
                hovertemplate=(
                    "<b>%{y}</b><br>"
                    f"{ct}: " + "%{x:.1f}%<extra></extra>"
                ),
            )
        )

    fig.update_layout(
        **LAYOUT_DEFAULTS,
        barmode="stack",
        title=dict(
            text="Contract Type by Category",
            font=dict(size=16, color="#1a1a2e"),
        ),
        xaxis=dict(
            title="",
            showgrid=False,
            range=[0, 100],
            ticksuffix="%",
        ),
        yaxis=dict(showgrid=False),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.05,
            xanchor="center",
            x=0.5,
        ),
        height=400,
    )

    return fig


def off_contract_opportunities(df: pd.DataFrame) -> pd.DataFrame:
    """Identify categories with >20% off-contract spend.

    Args:
        df: Filtered DataFrame.

    Returns:
        DataFrame with category, off-contract %, total spend,
        and off-contract spend for flagged categories.
    """
    cat_contract = (
        df.groupby(
            ["spend_category", "contract_type"], as_index=False
        )["total_amount"]
        .sum()
    )

    cat_totals = (
        df.groupby("spend_category", as_index=False)["total_amount"]
        .sum()
        .rename(columns={"total_amount": "total_category_spend"})
    )

    off_contract = cat_contract[
        cat_contract["contract_type"] == "Off-Contract"
    ].rename(columns={"total_amount": "off_contract_spend"})

    merged = cat_totals.merge(
        off_contract[["spend_category", "off_contract_spend"]],
        on="spend_category",
        how="left",
    )
    merged["off_contract_spend"] = merged["off_contract_spend"].fillna(0)
    merged["off_contract_pct"] = (
        merged["off_contract_spend"]
        / merged["total_category_spend"]
        * 100
    )

    opportunities = (
        merged[merged["off_contract_pct"] > 20]
        .sort_values("off_contract_pct", ascending=False)
        .reset_index(drop=True)
    )

    opportunities.columns = [
        "Spend Category",
        "Total Category Spend",
        "Off-Contract Spend",
        "Off-Contract %",
    ]

    return opportunities
