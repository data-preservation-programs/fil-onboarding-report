#!/usr/bin/env python3
import os
from datetime import datetime, timedelta, timezone

import altair as alt
import pandas as pd
import streamlit as st

import database as db
from client import StatsClient
from streamlitstyle import hide_streamlit_style
from utils import int_client_id

TITLE = "Data Onboarding to Filecoin"
ICON = "./assets/filecoin-symbol.png"
CACHE = "/tmp/spadecsvcache"

os.makedirs(CACHE, exist_ok=True)

st.set_page_config(page_title=TITLE, page_icon=ICON, layout="wide")
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

st.title(TITLE)

st.warning(
    """
    This dashboard was deprecated on 2024-04-20.

    Here are great existing and working Filecoin dashboards that cover similar topics:

    * [Starboard](https://dashboard.starboard.ventures/dashboard)
    * [Filecoin Dune Daily Metrics](https://dune.com/kalen/filecoin-daily-metrics)
    * [Filecoin Pulse](https://filecoinpulse.pages.dev/) (PoC)
"""
)

def humanize(s):
    if s >= 1024 * 1024 * 1024:
        return f"{s / 1024 / 1024 / 1024:,.2f} EB"
    if s >= 1024 * 1024:
        return f"{s / 1024 / 1024:,.2f} PB"
    if s >= 1024:
        return f"{s / 1024:,.1f} TB"
    return f"{s:,.1f} GB"


def temporal_bars(data, bin, period, ylim, state, color):
    ch = alt.Chart(data, height=250)
    ch = ch.mark_bar(
        color="#0090FF") if state == "Onchain" else ch.mark_bar()
    return ch.encode(
        x=alt.X(f"{bin}(Day):T", title=period),
        y=alt.Y(f"sum({state}):Q", axis=alt.Axis(format=",.0f"), title=f"{state} Size",
                scale=alt.Scale(domain=[0, ylim])),
        tooltip=[alt.Tooltip(f"{bin}(Day):T", title=period),
                 alt.Tooltip("sum(Onchain):Q", format=",.0f", title="Onchain"),
                 alt.Tooltip("client_name:N", title="Client Name")],
        color=color

    ).interactive(bind_y=False).configure_axisX(grid=False)


def calculate_mean_std_for_last_n_days(df, col, n=14):
    window = df[col].tail(n + 1).head(n)  # ignore yesterday

    return window.mean(), window.std()


def get_client_ids(ids):
    client_identifiers = ids.split(",")
    return [int_client_id(i) for i in client_identifiers]


ldf = datetime.today().date()
fdf = ldf.replace(year=ldf.year - 1)
fday, lday = st.sidebar.slider("Date Range", value=(
    fdf, ldf), min_value=fdf, max_value=ldf)
lday = lday + timedelta(1)

size_df = db.top_clients_for_last_week(
    first_day=lday - pd.DateOffset(weeks=1), last_day=lday, top_n=10)
size_df["Onchain"] = size_df["Onchain"] * 1.0 / 1024

st.sidebar.markdown("## Top 10 onboarders in the last week")
st.sidebar.dataframe(size_df.style.format(
    {"Onchain": "{:,.0f} TB"}), use_container_width=True)

# Set client id
query_params = st.experimental_get_query_params()
default_ids = "01131298"  # Internet archive
if 'client_id' in query_params:
    default_ids = ",".join(query_params['client_id'])

client_ids = st.sidebar.text_input(
    "Comma separated list of Filecoin Address ids (integer addresses ex: 01131298 works as well)", default_ids)
client_ids = get_client_ids(client_ids)

# Setup stats client and get client names
stats_client = StatsClient()
stats_client.calculate_client_id_to_name_map()

# Run database queries
cp_ct_sz = db.copies_count_size(
    first_day=fday, last_day=lday, client_ids=client_ids)
daily_sizes = db.active_or_published_daily_size(
    first_day=fday, last_day=lday, client_ids=client_ids)
total_daily_sizes = db.total_active_or_published_daily_size()
daily_sizes = daily_sizes.dropna(subset=["Day"])

# Daily sizes will have a new client_name column with names from StatsClient populated based on a given client_id
daily_sizes['client_name'] = daily_sizes['client_id'].apply(
    stats_client.get_client_name)

client_names = daily_sizes['client_name'].tolist()
client_names_unique = daily_sizes['client_name'].unique().tolist()
client_names_joined = ', '.join(client_names_unique)

st.subheader("Aggregated")
base = alt.Chart(total_daily_sizes).encode(x=alt.X("Day:T"))
ch = alt.layer(
    base.mark_line().transform_window(
        sort=[{"field": "Day"}],
        TotalOnChain="sum(Onchain)"
    ).encode(y="TotalOnChain:Q"),
).interactive(bind_y=False).configure_axisX(grid=False)
st.altair_chart(ch, use_container_width=True)

cols = st.columns(1)
cols[0].metric("Total onboarded data", humanize(
    total_daily_sizes.Onchain.sum()), help="Total onboarded data")

st.subheader("Client specific")
cols = st.columns(1)
cols[0].metric("Total onboarded data for **{client_names}**".format(client_names=client_names_joined), humanize(
    daily_sizes.Onchain.sum()), help="Total onboarded data")

cols = st.columns(4)
cols[0].metric("Unique data size", humanize(cp_ct_sz.Size.sum()), help="Total unique active/published pieces in the "
                                                                       "Filecoin network")
cols[1].metric("Unique files", f"{cp_ct_sz.Count.sum():,.0f} files", help="Total unique active/published pieces in "
                                                                          "the Filecoin network")
cols[2].metric("4+ Replications unique data size", humanize(cp_ct_sz[cp_ct_sz.Copies >= 4].Size.sum()),
               help="Unique active/published pieces with at least four replications in the Filecoin network")
cols[3].metric("4+ Replications unique files", f"{cp_ct_sz[cp_ct_sz.Copies >= 4].Count.sum():,.0f} files",
               help="Unique active/published pieces with at least four replications in the Filecoin network")

cols = st.columns(4)
last = daily_sizes[daily_sizes["Day"] >= lday - pd.DateOffset(days=1)]
cols[0].metric("Onboarded Last Day", humanize(last.Onchain.sum()),
               help="Total packed and on-chain sizes of unique files of the last day")
last = daily_sizes[daily_sizes["Day"] >= lday - pd.DateOffset(days=7)]
cols[1].metric("Onboarded Last Week", humanize(last.Onchain.sum()),
               help="Total packed and on-chain sizes of unique files of the last week")
last = daily_sizes[daily_sizes["Day"] >= lday - pd.DateOffset(days=30)]
cols[2].metric("Onboarded Last Month", humanize(last.Onchain.sum()),
               help="Total packed and on-chain sizes of unique files of the last month")
last = daily_sizes[daily_sizes["Day"] >= lday - pd.DateOffset(days=365)]
cols[3].metric("Onboarded Last Year", humanize(last.Onchain.sum()),
               help="Total packed and on-chain sizes of unique files of the last year")

tbs = st.tabs(["Accumulated", "Daily", "Weekly", "Monthly",
               "Quarterly", "Yearly", "Status", "Data"])

rt = daily_sizes.set_index("Day").sort_index()
rtv = rt[["Onchain"]]

ranges = {
    "Day": rtv.groupby(pd.Grouper(freq="D")).sum().to_numpy().max(),
    "Week": rtv.groupby(pd.Grouper(freq="W")).sum().to_numpy().max(),
    "Month": rtv.groupby(pd.Grouper(freq="M")).sum().to_numpy().max(),
    "Quarter": rtv.groupby(pd.Grouper(freq="Q")).sum().to_numpy().max(),
    "Year": rtv.groupby(pd.Grouper(freq="Y")).sum().to_numpy().max()
}

base = alt.Chart(daily_sizes).encode(x=alt.X("Day:T"))
ch = alt.layer(
    base.mark_area().transform_window(
        sort=[{"field": "Day"}],
        TotalOnChain="sum(Onchain)"
    ).encode(y="TotalOnChain:Q", color="client_name"),
).interactive(bind_y=False).configure_axisX(grid=False)
tbs[0].altair_chart(ch, use_container_width=True)

ch = temporal_bars(daily_sizes, "utcyearmonthdate", "Day",
                   ranges["Day"], "Onchain", "client_name")
tbs[1].altair_chart(ch, use_container_width=True)

ch = temporal_bars(daily_sizes, "yearweek", "Week",
                   ranges["Week"], "Onchain", "client_name")
tbs[2].altair_chart(ch, use_container_width=True)

ch = temporal_bars(daily_sizes, "yearmonth", "Month",
                   ranges["Month"], "Onchain", "client_name")
tbs[3].altair_chart(ch, use_container_width=True)

ch = temporal_bars(daily_sizes, "yearquarter", "Quarter",
                   ranges["Quarter"], "Onchain", "client_name")
tbs[4].altair_chart(ch, use_container_width=True)

ch = temporal_bars(daily_sizes, "year", "Year",
                   ranges["Year"], "Onchain", "client_name")
tbs[5].altair_chart(ch, use_container_width=True)

pro_ct = db.provider_item_counts(
    first_day=fday, last_day=lday, client_ids=client_ids)
dl_st_ct = db.deal_count_by_status(
    first_day=fday, last_day=lday, client_ids=client_ids)
trm_ct = db.terminated_deal_count_by_reason(
    first_day=fday, last_day=lday, client_ids=client_ids)
idx_age = db.index_age()

cols = tbs[6].columns((3, 2, 2))
with cols[0]:
    ch = alt.Chart(cp_ct_sz, title="Active/Published Copies").mark_bar().encode(
        x="Count:Q",
        y=alt.Y("Copies:O", sort="-y"),
        tooltip=["Copies:O", alt.Tooltip("Count:Q", format=",")]
    ).configure_axisX(grid=False)
    st.altair_chart(ch, use_container_width=True)
with cols[1]:
    ch = alt.Chart(dl_st_ct).mark_arc().encode(
        theta="Count:Q",
        color=alt.Color("Status:N",
                        scale=alt.Scale(domain=["active", "published", "terminated"], range=[
                            "teal", "orange", "red"]),
                        legend=alt.Legend(title="Deal Status", orient="top")),
        tooltip=["Status:N", alt.Tooltip("Count:Q", format=",")]
    )
    st.altair_chart(ch, use_container_width=True)
with cols[2]:
    ch = alt.Chart(trm_ct).mark_arc().encode(
        theta="Count:Q",
        color=alt.Color("Reason:N", scale=alt.Scale(domain=["expired", "slashed"], range=["orange", "red"]),
                        legend=alt.Legend(title="Termination Reason", orient="top")),
        tooltip=["Reason:N", alt.Tooltip("Count:Q", format=",")]
    )
    st.altair_chart(ch, use_container_width=True)

cols = tbs[7].columns((6, 4, 4, 3))
with cols[0]:
    st.caption("Daily Activity")
    st.dataframe(daily_sizes.style.format(
        {"Day": lambda t: t.strftime("%Y-%m-%d"), "Onchain": "{:,.0f}", "Pieces": "{:,.0f}"}),
        use_container_width=True)
with cols[1]:
    st.caption("Service Providers")
    st.dataframe(pro_ct.style.format(
        {"Provider": "f0{}", "Count": "{:,}"}), use_container_width=True)
with cols[2]:
    st.caption("Active/Published Copies")
    st.dataframe(cp_ct_sz.set_index(cp_ct_sz.columns[0]).style.format({"Count": "{:,}", "Size": "{:,.0f}"}),
                 use_container_width=True)
with cols[3]:
    st.caption("Deal Status")
    st.dataframe(dl_st_ct.set_index(
        dl_st_ct.columns[0]), use_container_width=True)
    st.caption("Termination Reason")
    st.dataframe(trm_ct.set_index(trm_ct.columns[0]), use_container_width=True)
    st.write(
        f"_Updated: {(datetime.now(timezone.utc) - idx_age.iloc[0, 0]).total_seconds() / 60:,.0f} minutes ago._")

# with st.expander("### Experimental: Projection"):
#     form = st.form(key='projection')
#     c1, c2, c3 = st.columns(3)
#     with c1:
#         target_size = st.number_input("Full dataset size (TB)", min_value=0,
#                                       value=1024)  # Defaults to 1 PiB for now, change it to LDN
#     with c2:
#         last_n = st.number_input("Number of days for window", min_value=2, value=14,
#                                  help="Average onboarding rate is calculated over last n days, where n is the input of this field")
#     with c3:
#         onb_rate = st.number_input("Target onboarding rate (TB)/day", min_value=0, value=10)
#
#     mean, std = calculate_mean_std_for_last_n_days(daily_sizes, 'Onchain', last_n)
#     current_size = daily_sizes['Onchain'].sum()
#     t_delta = (target_size * 1024 - current_size) / mean
#     est_end_date = lday + timedelta(days=t_delta)
#
#     target_t_delta = (target_size * 1024 - current_size) / (int(onb_rate) * 1024)
#     target_end_date = lday + timedelta(days=target_t_delta)
#
#     cols = st.columns(4)
#     cols[0].metric("Expected finish date using mean onboarding rate", str(est_end_date),
#                    help="Expected finish date based on the mean daily onboarding rate over last {last_n} days".format(
#                        last_n=last_n))
#     cols[1].metric("Expected finish date using target onboarding rate", str(target_end_date),
#                    help="Expected finish date based on the target daily onboarding rate")
#     cols[2].metric("Mean daily onboarding rate over last {last_n} days".format(last_n=last_n), humanize(mean))
#     cols[3].metric("Standard Deviation of daily onboarding rate over last {last_n} days".format(last_n=last_n),
#                    humanize(std))
#
#     cols = st.columns(1)
#
#     estimated_line = pd.DataFrame({
#         'Day': [lday, est_end_date],
#         'TotalOnChain': [current_size, int(target_size) * 1024],
#
#     })
#
#     target_line = pd.DataFrame({
#         'Day': [lday, target_end_date],
#         'TotalOnChain': [current_size, int(target_size) * 1024]
#     })
#
#     # Create the base chart with color encoding and legend title
#     base = alt.Chart(daily_sizes).mark_line(size=4, color="#ff2b2b").transform_window(
#         sort=[{"field": "Day"}],
#         TotalOnChain="sum(Onchain)"
#     ).encode(x="Day:T", y="TotalOnChain:Q")
#
#     # Create the estimated and target lines with color encoding
#     est_line_plot = alt.Chart(estimated_line).mark_line(color='green').encode(x="Day:T", y="TotalOnChain:Q")
#     target_line_plot = alt.Chart(target_line).mark_line(color='blue').encode(x="Day:T", y="TotalOnChain:Q")
#
#     # Layer the three components with the base chart, estimated line, and target line
#     ch = alt.layer(base, est_line_plot, target_line_plot).configure_axisX(grid=False)
#
#     cols[0].altair_chart(ch, use_container_width=True)
