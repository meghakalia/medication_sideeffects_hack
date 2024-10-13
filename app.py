from fastapi import FastAPI, Query
import requests

app = FastAPI()


# Function to perform the GET request to the DailyMed site using `requests`
def fetch_drug_info(drug_name: str):
    url = f'https://dailymed.nlm.nih.gov/dailymed/search.cfm?labeltype=all&query={drug_name}&audience=consumer'

    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'cookie': '_ga=GA1.1.1215018488.1726843442; _gid=GA1.4.546978294.1728847524;',
        'priority': 'u=0, i',
        'referer': f'https://dailymed.nlm.nih.gov/dailymed/search.cfm?labeltype=all&query={drug_name}&audience=consumer',
        'sec-ch-ua': '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36'
    }

    response = requests.get(url, headers=headers)
    return response.text


# Define the /drug_search endpoint
@app.get("/drug_search")
def drug_search(drug_name: str = Query(..., description="Name of the drug to search")):
    try:
        # Call the function to fetch the drug info
        drug_info = fetch_drug_info(drug_name)
        return {"drug_name": drug_name, "data": drug_info}
    except Exception as e:
        return {"error": str(e)}

# To run the app
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)
