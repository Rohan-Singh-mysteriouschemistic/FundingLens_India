import streamlit as st
import pandas as pd
# importing re module for the filtering of data, ie, splitting, cleaning etc.
import re
import matplotlib.pyplot as plt
from Analysis import Data_Analysis

main_obj = Data_Analysis()

st.set_page_config(layout="wide", page_title="Startup Funding Dashboard")
st.title("🚀 Startup-Funding Dashboard")

# Sidebar Setup
st.sidebar.title("Startup Funding Analysis")
option = st.sidebar.selectbox("Choose to Analyse...", ["Overall Analysis", "StartUps", "Investors", "Investor Comparison"])

# ======================== Overall Analysis ======================== #
if option == "Overall Analysis":
    st.subheader("🔎 Filter Dataset")
    col1, col2, col3 = st.columns(3)

    with col1:
        selected_year = st.selectbox("Select Year", options=["All"] + sorted(main_obj.file['year'].dropna().unique().tolist()))

    with col2:
        selected_sector = st.selectbox("Select Sector", options=["All"] + sorted(main_obj.file['vertical'].dropna().unique().tolist()))

    with col3:
        funding_min, funding_max = st.slider("Funding Amount Range (₹ Cr)", min_value=float(main_obj.file['Amount(in Cr)'].min()), max_value=float(main_obj.file['Amount(in Cr)'].max()), value=(float(main_obj.file['Amount(in Cr)'].min()), float(main_obj.file['Amount(in Cr)'].max())))
    filtered_df = main_obj.file.copy()

    if selected_year != "All":
        filtered_df = filtered_df[filtered_df['year'] == selected_year]
    if selected_sector != "All":
        filtered_df = filtered_df[filtered_df['vertical'] == selected_sector]
    filtered_df = filtered_df[(filtered_df['Amount(in Cr)'] >= funding_min) & (filtered_df['Amount(in Cr)'] <= funding_max)].set_index("startup")

    st.dataframe(filtered_df, use_container_width=True)

    st.markdown("---")
    

    total_funding = main_obj.file['Amount(in Cr)'].sum()
    max_funding = main_obj.file['Amount(in Cr)'].max()
    avg_funding = main_obj.file['Amount(in Cr)'].mean()
    total_startups = main_obj.file['startup'].nunique()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💰 Total Funding", f"₹ {total_funding:.2f} Cr")
    col2.metric("🚀 Max Single Investment", f"₹ {max_funding:.2f} Cr")
    col3.metric("📊 Avg Investment", f"₹ {avg_funding:.2f} Cr")
    col4.metric("🏢 Funded Startups", total_startups)

    st.subheader("📌 Sector-wise Investment Analysis")
    sector_amounts = main_obj.file.groupby('vertical')['Amount(in Cr)'].sum().sort_values(ascending=False).head(10)
    sector_counts = main_obj.file['vertical'].value_counts().head(10)

    col5, col6 = st.columns(2)
    with col5:
        st.markdown("### 💰 Top Sectors by Total Amount")
        fig1, ax1 = plt.subplots(figsize=(6, 6))
        ax1.pie(sector_amounts, labels=sector_amounts.index, autopct='%1.1f%%', startangle=90, wedgeprops={'edgecolor': 'white'})
        ax1.axis('equal')
        st.pyplot(fig1)

    with col6:
        st.markdown("### 📊 Top Sectors by Number of Fundings")
        fig2, ax2 = plt.subplots(figsize=(6, 6))
        ax2.pie(sector_counts, labels=sector_counts.index, autopct='%1.1f%%', startangle=90, wedgeprops={'edgecolor': 'white'})
        ax2.axis('equal')
        st.pyplot(fig2)

    st.subheader("📅 Top Funded Startups by Year")
    top_startups_by_year = main_obj.file.groupby(['year', 'startup'])['Amount(in Cr)'].sum().reset_index()
    top_startups_by_year = top_startups_by_year.sort_values(['year', 'Amount(in Cr)'], ascending=[True, False])

    years = sorted(top_startups_by_year['year'].unique())
    for i in range(0, len(years), 3):
        cols = st.columns(3)
        for j in range(3):
            if i + j < len(years):
                year = years[i + j]
                with cols[j]:
                    st.markdown(f"#### {year}")
                    top5 = top_startups_by_year[top_startups_by_year['year'] == year].head(5).set_index("year")
                    st.dataframe(top5, use_container_width=True)

    st.subheader("🏆 Top Funded Startups Overall")
    top_startups = main_obj.file.groupby('startup')['Amount(in Cr)'].sum().sort_values(ascending=False).head(10)
    st.bar_chart(top_startups)

    st.subheader("💼 Top Investors (Total Funding Amount)")
    all_investor_entries = main_obj.file[['investors', 'Amount(in Cr)']].dropna()
    investor_amounts = {}

    for _, row in all_investor_entries.iterrows():
        investors = re.split(r"\s*(?:,|/|&|\||\+|\band\b)\s*", str(row['investors']), flags=re.IGNORECASE)
        for investor in investors:
            investor = investor.strip()
            if investor and investor.lower() != "undisclosed":
                investor_amounts[investor] = investor_amounts.get(investor, 0) + row['Amount(in Cr)']

    investor_series = pd.Series(investor_amounts).sort_values(ascending=False).head(10)
    st.bar_chart(investor_series)

# ======================== Start-Up Analysis ======================== #
elif option == "StartUps":
    startup_opt = st.sidebar.selectbox("Select a Startup", main_obj.Fetch_Startups())
    btn1 = st.sidebar.button("🔎 Analyse Startup")

    if btn1:
        st.title(f"📊 {startup_opt} Analysis")
        startup_df = main_obj.Startup_Investment(startup_opt).set_index("investors")
        if startup_df.empty:
            st.warning("No investment data found for this startup.")
        else:
            st.subheader("💸 Top 5 Investments")
            st.dataframe(startup_df)

        st.subheader("🏷 Round-wise Investments")
        funding_rounds = [
            'Angel', 'Angel / Seed Funding', 'Angel Funding', 'Angel Round',
            'Bridge Round', 'Corporate Round', 'Crowd Funding', 'Debt', 'Debt Financing',
            'Debt Funding', 'Debt and Preference Capital', 'Debt-Funding', 'Equity',
            'Equity Based Funding', 'Funding Round', 'Grant', 'Inhouse Funding',
            'Maiden Round', 'Mezzanine', 'Non-Equity Assistance', 'Post-IPO Debt',
            'Post-IPO Equity', 'Pre-Series A', 'Pre-Seed', 'Private', 'Private Equity',
            'Private Funding', 'PrivateEquity', 'Secondary Market', 'Seed',
            'Seed / Angel Funding', 'Seed / Angle Funding', 'Seed Funding', 'Seed Round',
            'Series A', 'Series B', 'Series B (Extension)', 'Series C', 'Series D',
            'Series E', 'Series F', 'Series G', 'Series H', 'Series J', 'Single Venture',
            'Structured Debt', 'Term Loan', 'Undisclosed', 'Venture', 'Venture - Series Unknown', 'Venture Round'
        ]

        for round_name in sorted(set(funding_rounds)):
            round_df = main_obj.Roundwise_Startup_Investment(startup_opt, round_name)[["investors", "Amount(in Cr)", "year", "state"]].set_index("investors")
            if not round_df.empty:
                st.markdown(f"### 💼 {round_name}")
                st.dataframe(round_df)

# ======================== Investor's Analysis ======================== #
elif option == "Investors":
    investor_opt = st.sidebar.selectbox("Investors", main_obj.Fetch_Investors())
    btn2 = st.sidebar.button("Analyse")

    if btn2:
        st.title(f"{investor_opt} - Investor Analysis")

        recent_df, top_investments, sector_split, yoy_series = main_obj.Investor_Analysis(investor_opt)

        if recent_df.empty:
            st.warning("No data available for this investor.")
        else:
            st.subheader("Most Recent Investments")
            st.dataframe(recent_df, use_container_width=True)

            st.subheader("Top Investments")
            if not top_investments.empty:
                st.bar_chart(top_investments)
            else:
                st.info("No top investments to display.")

            st.subheader("Sector-wise Investment Split")
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**By Investment Amount**")
                if not sector_split.empty:
                    fig1, ax1 = plt.subplots()
                    sector_split.plot.pie(ax=ax1, autopct='%1.1f%%', startangle=90)
                    ax1.axis('equal')
                    st.pyplot(fig1)
                else:
                    st.info("No sector-wise investment data to display.")

            with col2:
                st.markdown("**By Count of Investments**")
                sector_counts = recent_df['vertical'].value_counts().head(10)
                if not sector_counts.empty:
                    fig2, ax2 = plt.subplots()
                    ax2.pie(sector_counts, labels=sector_counts.index, autopct='%1.1f%%', startangle=90)
                    ax2.axis('equal')
                    st.pyplot(fig2)
                else:
                    st.info("No sector-wise count data to display.")

            st.subheader("Year-over-Year Investment Trend")
            if not yoy_series.empty:
                st.line_chart(yoy_series)
            else:
                st.info("No YoY investment trend available for this investor.")

elif option == "Investor Comparison":
    st.title("Investor Comparison")

    all_investors = main_obj.Fetch_Investors()
    selected_investors = st.multiselect("Select Investors to Compare", all_investors)

    if selected_investors:
        compare_metric = st.radio("Compare by:", ["Top Sectors by Amount", "Investment Count", "Year over Year (YoY) Trend"])

        if compare_metric == "Top Sectors by Amount":
            st.subheader("💰 Top Sectors by Investment Amount")

            fig, ax = plt.subplots(figsize=(10, 6))

            for investor in selected_investors:
                _, top_sectors, _, _ = main_obj.Investor_Analysis(investor)
                if not top_sectors.empty:
                    ax.plot(top_sectors.index, top_sectors.values, marker='o', label=investor)

            ax.set_xlabel("Sector")
            ax.set_ylabel("Investment Amount")
            ax.set_title("Top Sectors by Investment Amount")
            ax.legend()
            ax.grid(True)
            st.pyplot(fig)

        elif compare_metric == "Investment Count":
            st.subheader("📊 Sector-wise Investment Count")

            fig, ax = plt.subplots(figsize=(10, 6))

            for investor in selected_investors:
                recent_df, _, _, _ = main_obj.Investor_Analysis(investor)
                if not recent_df.empty:
                    sector_counts = recent_df['vertical'].value_counts().head(10)
                    ax.plot(sector_counts.index, sector_counts.values, marker='o', label=investor)

            ax.set_xlabel("Sector")
            ax.set_ylabel("Number of Investments")
            ax.set_title("Top Sectors by Investment Count")
            ax.legend()
            ax.grid(True)
            st.pyplot(fig)

        elif compare_metric == "Year over Year (YoY) Trend":
            st.subheader("📈 Year-over-Year Investment Trend")

            fig, ax = plt.subplots(figsize=(10, 6))

            for investor in selected_investors:
                _, _, _, yoy_series = main_obj.Investor_Analysis(investor)
                if not yoy_series.empty:
                    ax.plot(yoy_series.index, yoy_series.values, marker='o', label=investor)

            ax.set_xlabel("Year")
            ax.set_ylabel("Investment Amount")
            ax.set_title("Year-over-Year Investment Trend")
            ax.legend()
            ax.grid(True)
            st.pyplot(fig)

    else:
        st.info("Please select at least one investor to compare.")
