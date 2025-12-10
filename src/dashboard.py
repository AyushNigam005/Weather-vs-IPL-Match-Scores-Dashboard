# src/dashboard.py

import streamlit as st
import pandas as pd
import plotly.express as px

from data_prep import load_and_prepare


st.set_page_config(
    page_title="Weather vs IPL Match Scores",
    page_icon="🏏",
    layout="wide",
)


@st.cache_data
def get_merged_data() -> pd.DataFrame:
    return load_and_prepare()


def sidebar_filters(df: pd.DataFrame):
    st.sidebar.title("Filters")

    seasons = sorted(df["season"].dropna().unique()) if "season" in df.columns else []
    cities = sorted(df["city"].dropna().unique())
    teams = sorted(
        pd.unique(
            pd.concat([df.get("team1", pd.Series(dtype=str)),
                       df.get("team2", pd.Series(dtype=str))])
        ).dropna()
    )

    selected_season = (
        st.sidebar.multiselect("Season", options=seasons, default=seasons)
        if seasons
        else None
    )
    selected_city = st.sidebar.multiselect("City", options=cities, default=cities)
    selected_teams = st.sidebar.multiselect("Team (appears as team1 or team2)",
                                            options=teams, default=teams)

    temp_min, temp_max = float(df["temp_c"].min()), float(df["temp_c"].max())
    selected_temp_range = st.sidebar.slider(
        "Temperature Range (°C)",
        min_value=round(temp_min - 1, 1),
        max_value=round(temp_max + 1, 1),
        value=(round(temp_min - 1, 1), round(temp_max + 1, 1))
    )

    return {
        "season": selected_season,
        "city": selected_city,
        "teams": selected_teams,
        "temp_range": selected_temp_range,
    }


def apply_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    filtered = df.copy()

    if filters["season"] is not None:
        filtered = filtered[filtered["season"].isin(filters["season"])]

    filtered = filtered[filtered["city"].isin(filters["city"])]

    # Filter by teams (either side)
    if filters["teams"]:
        mask_team1 = filtered.get("team1", "").isin(filters["teams"])
        mask_team2 = filtered.get("team2", "").isin(filters["teams"])
        filtered = filtered[mask_team1 | mask_team2]

    tmin, tmax = filters["temp_range"]
    filtered = filtered[(filtered["temp_c"] >= tmin) & (filtered["temp_c"] <= tmax)]

    return filtered


def show_kpis(df: pd.DataFrame):
    st.subheader("Key Match & Weather Overview")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Matches", len(df))

    with col2:
        st.metric("Avg Total Runs", f"{df['total_runs'].mean():.1f}")

    with col3:
        st.metric("Avg Temperature (°C)", f"{df['temp_c'].mean():.1f}")

    with col4:
        if "humidity" in df.columns:
            st.metric("Avg Humidity (%)", f"{df['humidity'].mean():.1f}")
        else:
            st.metric("Avg Humidity (%)", "N/A")


def chart_temp_vs_runs(df: pd.DataFrame):
    st.subheader("Temperature vs Total Runs (Match-level Scatter Plot)")
    fig = px.scatter(
        df,
        x="temp_c",
        y="total_runs",
        hover_data=["city", "venue", "team1", "team2", "date_str"],
        labels={"temp_c": "Temperature (°C)", "total_runs": "Total Runs"},
        trendline="ols",
    )
    st.plotly_chart(fig, use_container_width=True)


def chart_runs_over_time(df: pd.DataFrame):
    st.subheader("Runs & Temperature Over Time")

    # Sort by date
    df_sorted = df.sort_values("date")

    fig = px.line(
        df_sorted,
        x="date",
        y="total_runs",
        color="city",
        labels={"date": "Date", "total_runs": "Total Runs"},
        title="Match Scores Over Time",
    )
    st.plotly_chart(fig, use_container_width=True)

    fig2 = px.line(
        df_sorted,
        x="date",
        y="temp_c",
        color="city",
        labels={"date": "Date", "temp_c": "Temperature (°C)"},
        title="Temperature Over Time",
    )
    st.plotly_chart(fig2, use_container_width=True)


def chart_runs_by_temp_bucket(df: pd.DataFrame):
    st.subheader("Average Total Runs by Temperature Bucket")

    if "temp_bucket" not in df.columns:
        st.info("Temperature bucket info not available.")
        return

    group = (
        df.groupby("temp_bucket")["total_runs"]
        .mean()
        .reset_index()
        .sort_values("temp_bucket")
    )

    fig = px.bar(
        group,
        x="temp_bucket",
        y="total_runs",
        labels={"temp_bucket": "Temperature Bucket", "total_runs": "Average Total Runs"},
    )
    st.plotly_chart(fig, use_container_width=True)


def chart_runs_by_weather_type(df: pd.DataFrame):
    if "weather_type" not in df.columns:
        return

    st.subheader("Average Total Runs by Weather Type")
    group = (
        df.groupby("weather_type")["total_runs"]
        .mean()
        .reset_index()
        .sort_values("total_runs", ascending=False)
    )

    fig = px.bar(
        group,
        x="weather_type",
        y="total_runs",
        labels={"weather_type": "Weather Type", "total_runs": "Average Total Runs"},
    )
    st.plotly_chart(fig, use_container_width=True)


def show_insights(df: pd.DataFrame):
    st.subheader("Quick Insights (Static Logic – You’ll Refine in Blog)")

    avg_runs_hot = df[df["temp_c"] >= df["temp_c"].median()]["total_runs"].mean()
    avg_runs_cool = df[df["temp_c"] < df["temp_c"].median()]["total_runs"].mean()

    st.markdown(
        f"""
- 📌 **Matches on hotter days (>= median temp)** had an average of **{avg_runs_hot:.1f} runs**.  
- 🧊 **Matches on cooler days (< median temp)** had an average of **{avg_runs_cool:.1f} runs**.  

You can refine this section in your blog using your full dataset.
        """
    )


def main():
    st.title("🌦️ Weather vs 🏏 IPL Match Scores Dashboard")

    st.markdown(
        """
This dashboard explores how **weather conditions** (temperature, humidity, etc.)
relate to **IPL match scores**.  
Use the filters on the left to drill down by season, city and teams.
        """
    )

    df = get_merged_data()

    filters = sidebar_filters(df)
    filtered_df = apply_filters(df, filters)

    if filtered_df.empty:
        st.warning("No data after applying filters. Try expanding your selections.")
        return

    show_kpis(filtered_df)

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        chart_temp_vs_runs(filtered_df)
    with col2:
        chart_runs_by_temp_bucket(filtered_df)

    st.markdown("---")

    chart_runs_over_time(filtered_df)

    st.markdown("---")

    chart_runs_by_weather_type(filtered_df)

    st.markdown("---")

    show_insights(filtered_df)


if __name__ == "__main__":
    main()
