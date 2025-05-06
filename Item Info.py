import requests
import pandas as pd

API_KEY = "45kpvfidpbdc7jhfvod2duokk519rlcptohortto2duqpi8jcij9027tvn671i0p"
url = "https://api.keepa.com/product"

# List of ASINs to fetch descriptions
asin_list = ["B0D1XD1ZV3", "B00E4GACB8", "B0CWXNS552", "B0CXG3HMX1", "B0CVS1XHJL", "B0113UZJE2", "B09715G57M", "B01LR5S6HK"]

# Initialize an empty list to store product data
product_data = []

for asin in asin_list:
    params = {
        "key": API_KEY,
        "domain": 1,  # Amazon.com
        "asin": asin
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()

        if "products" in data and data["products"]:
            product = data["products"][0]
            title = product.get("title", "Title not available")
            description = product.get("description", "Description not available")

            product_data.append({"ASIN": asin, "Title": title, "Description": description})
        else:
            print(f"No product data found for ASIN: {asin}")

    else:
        print(f"Error retrieving data for ASIN {asin}: {response.status_code}, {response.text}")

# Convert to DataFrame and export to Excel
df = pd.DataFrame(product_data)
excel_filename = "keepa_product_descriptions_Current Best Sellers.xlsx"
df.to_excel(excel_filename, index=False)

print(f"Product descriptions exported to {excel_filename}")