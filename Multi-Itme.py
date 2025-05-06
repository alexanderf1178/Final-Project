import requests
import pandas as pd
from datetime import datetime, timezone

API_KEY = "xxxxxxxxx"
url = "https://api.keepa.com/product"

# List of ASINs to fetch data
asin_list = ["B0D1XD1ZV3", "B00E4GACB8", "B0CWXNS552", "B0DNZCJ93D", "B0CXG3HMX1", "B0DWHTTKHM", "B0CVS1XHJL", "B0113UZJE2", "B09715G57M", "B01LR5S6HK"]

for asin in asin_list:
    params = {
        "key": API_KEY,
        "domain": 1,  # Amazon.com
        "asin": asin,
        "history": 1  # Requesting price history
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()

        # Validate the presence of price history data
        if "products" in data and data["products"]:
            if "csv" in data["products"][0] and data["products"][0]["csv"]:
                raw_price_data = data["products"][0]["csv"][0]
            else:
                print(f"No price data available for ASIN: {asin}")
                continue  # Skip this ASIN if no data is found
        else:
            print(f"Invalid API response for ASIN: {asin}")
            continue

        price_data = []
        base_date = datetime(1970, 1, 1, tzinfo=timezone.utc)  # Unix epoch base date

        for i in range(0, len(raw_price_data), 2):  # Step through list in pairs
            timestamp = raw_price_data[i]
            price = raw_price_data[i + 1] if i + 1 < len(raw_price_data) else None  # Amazon price

            # Ensure price is valid
            if price is None or price == -1:
                continue  # Skip this entry if the price is missing or invalid

            adjusted_timestamp = (timestamp + 21564000) * 60  # Convert minutes to seconds
            converted_date = datetime.fromtimestamp(adjusted_timestamp, timezone.utc).strftime("%Y-%m-%d")

            price_in_dollars = round(price / 100)  # Convert price from cents to dollars and round

            price_data.append({"Date": converted_date, "Price": price_in_dollars})

        # Convert to DataFrame
        df = pd.DataFrame(price_data)

        # Drop duplicate dates, keeping only the latest price for each day
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.sort_values(by=["Date"]).groupby("Date", as_index=False).last()

        # Generate a full date range
        full_date_range = pd.date_range(start=df["Date"].min(), end=df["Date"].max(), freq="D")

        # Reindex dataframe to include all dates and forward-fill missing prices
        df = df.set_index("Date").reindex(full_date_range).ffill().reset_index()

        # Rename the index column back to "Date"
        df.rename(columns={"index": "Date"}, inplace=True)

        # Export CSV files
        csv_filename = f"keepa_price_history_Current Best Sellers_{asin}.csv"
        df.to_csv(csv_filename, index=False)
        print(f"Completed price history for ASIN {asin} exported to {csv_filename}")

    else:
        print(f"Error retrieving data for ASIN {asin}: {response.status_code}, {response.text}")
