import numpy as np
import pandas as pd
# importing re module for the filtering of data, ie, splitting, cleaning etc.
import re

class Data_Analysis:
    def __init__(self):
        self.file = pd.read_csv("Indian_startups_funding.csv")
        self.file.drop(columns=['Unnamed: 0'], inplace=True) #Removing the unnamed index
        self.file.set_index("Sr No", inplace=True)
        self.file.rename(columns={"amount" : "Amount(in Cr)"}, inplace=True)

    def normalize_name(self, name): #Standardizing names that has the same meaning, ie, 100X.VC, 100x VC etc.
        name = name.lower() 
        name = re.sub(r'[^a-z0-9]', '', name)
        return name
    
    # Returning different Investor names
    def Fetch_Investors(self):
        self.file["investors"] = self.file["investors"].fillna("Undisclosed")
        all_investors = self.file["investors"].apply(lambda x: re.split(r"\s*(?:,|/|&|\||\+|\band\b)\s*", str(x), flags=re.IGNORECASE)).sum() # Making a list of investors by removing special characters

        cleaned_investors = [
            investor.strip()
            for investor in all_investors
            if investor.strip() and investor.strip().lower() != "undisclosed"
        ]
        normalized_map = {}
        for inv in cleaned_investors:
            norm = self.normalize_name(inv)
            if norm not in normalized_map:
                normalized_map[norm] = inv
        return sorted(set(normalized_map.values()))
    
    # Returning list of different startups
    def Fetch_Startups(self):
        all_startups = sorted(set(self.file["startup"].dropna().to_list()))
        return all_startups
    
    #Extracting 5 Biggest and 5 Recent Investments
    def Investments(self):
        recent_investments = self.file.tail(5)[["year", "startup"]]
        # print(recent_investments)
        bigg = self.file.sort_values(["Amount(in Cr)"], ascending=False).head(5)
        biggets_investments = bigg[["startup", "Amount(in Cr)"]]
        # print(biggets_investments)
        return [recent_investments, biggets_investments]

    def Startup_Investment(self, startup):
        group_by_obj = self.file.groupby("startup")
        if startup not in group_by_obj.groups:
            return pd.DataFrame(columns=["investors", "Amount(in Cr)", "round"])
        startup_df = group_by_obj.get_group(startup)
        return startup_df.sort_values(["Amount(in Cr)"], ascending=False).head(5)[["investors", "Amount(in Cr)", "round"]]

    def Roundwise_Startup_Investment(self, startup, round):
        group_by_obj2 = self.file.groupby(["startup", "round"])
        if (startup, round) not in group_by_obj2.groups:
            return pd.DataFrame(columns=self.file.columns)
        startup_rounwise = group_by_obj2.get_group((startup, round))
        return startup_rounwise
    
    def Investor_Analysis(self, investor):
        df = self.file.copy()
        df = df[df['investors'].notna()]

        investor_norm = self.normalize_name(investor)

        def match_investor(row):
            names = re.split(r"\s*(?:,|/|&|\||\+|\band\b)\s*", str(row))
            return any(self.normalize_name(name) == investor_norm for name in names)

        investor_df = df[df['investors'].apply(match_investor)]
        if investor_df.empty:
            return pd.DataFrame(), pd.Series(dtype='float64'), pd.Series(dtype='float64'), pd.Series(dtype='float64')

        # Top startup investments
        top_investments = investor_df.groupby('startup')['Amount(in Cr)'].sum().sort_values(ascending=False).head(5)

        # Sector-wise funding
        sector_split = investor_df.groupby('vertical')['Amount(in Cr)'].sum().sort_values(ascending=False)

        # Year-over-year funding
        yoy_series = investor_df.groupby('year')['Amount(in Cr)'].sum()

        # Recent 5 (by index)
        recent_df = investor_df.sort_index(ascending=False).head(5)[['startup', 'vertical', 'city', 'round', 'Amount(in Cr)', 'year']].set_index("startup")

        return recent_df, top_investments, sector_split, yoy_series
