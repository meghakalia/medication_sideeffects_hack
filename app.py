from fastapi import FastAPI, Query
from SearchDrug.SearchDrug import fetch_drug_info
import requests

app = FastAPI()


# Define the /drug_search endpoint
@app.get("/drug_search")
def drug_search(drug_name: str = Query(..., description="Name of the drug to search"),
                drug_symptoms: str = Query(None, description="Symptoms to search for")):
    try:
        return {"drug_name": drug_name, "symptoms": drug_symptoms, "data": "here will be the data..."}
        # Call the function to fetch the drug info
        drug_info = fetch_drug_info(drug_name)
        return {"drug_name": drug_name, "data": drug_info}
    except Exception as e:
        return {"error": str(e)}
