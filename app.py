from fastapi import FastAPI, Query
from SearchDrug.SearchDrug import research_drug_and_symptoms
from reddit_scrape_side_effect import reddit_side_effects
import requests
from  xml_final_df_drugname_zip_HC import search_reports_by_active_ingredient

app = FastAPI()


# Define the /drug_search endpoint
@app.get("/drug_search")
def drug_search(drug_name: str = Query(..., description="Name of the drug to search"),
                drug_symptoms: str = Query(None, description="Symptoms to search for")):
    try:
        # Call the function to fetch the drug info
        return research_drug_and_symptoms(drug_name, drug_symptoms)
    except Exception as e:
        return {"error": str(e)}


@app.get("/reddit_search")
def reddit_search(drug_name: str = Query(..., description="Subreddits to search"),
                  symptoms: str = Query(None, description="Symptoms to search for")):
    try:
        # Call the function to fetch the drug info
        return reddit_side_effects(drug_name, symptoms)
    except Exception as e:
        return {"error": str(e)}


@app.get("/drug_search_xml")
def drug_search_xml(drug_name: str = Query(..., description="Name of the drug to search")):
    try:
        # Call the function to fetch the drug info
        return search_reports_by_active_ingredient(drug_name)
    except Exception as e:
        return {"error": str(e)}