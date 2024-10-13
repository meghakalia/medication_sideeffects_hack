import requests
from bs4 import BeautifulSoup
import os
import openai
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.environ['OPENAI_API_KEY']


def review_drug_info_for_sympthoms(drug_name: str, symptoms: str, drug_info: str):
    # todo: improve the prompt if needed..
    prompt = f"You are an expert medical professional, you need to review a medical documentations and help a patient understand if their symptoms are an expected side effect or there is another issue." \
             f"Did you find the '{symptoms}' in the following text and return relevant sentences:\n\n{drug_info}. Provide your thought, reasoning and action for your response in a clear and concise manner."

    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1000,  # Maximum tokens to be returned in the response
        temperature=0.0  # Temperature controls randomness. Lower is more deterministic.
    )

    return response.choices[0].message.content.strip()


# Function to perform the GET request and extract drug info using BeautifulSoup
def fetch_drug_info(drug_name: str):
    url = f'https://dailymed.nlm.nih.gov/dailymed/search.cfm?labeltype=all&query={drug_name}&audience=consumer'

    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
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

    # Perform the GET request
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        drug_results = []
        links = []

        # Find the search results
        articles = soup.find_all('article', class_='row')

        for article in articles:
            drug_name = article.find('h2', class_='drug-name').text.strip()
            ndc_codes = article.find('span', class_='ndc-codes').text.strip()

            # Handle possible missing packager info
            packager_element = article.find('li', text=lambda x: x and 'Packager' in x)
            packager = packager_element.find_next(
                'span').text.strip() if packager_element else 'Packager information not found'

            drug_results.append({
                'drug_name': drug_name,
                'ndc_codes': ndc_codes,
                'packager': packager
            })

            # Extract all links to drug information pages
            link_element = article.find('a', href=lambda href: href and 'drugInfo.cfm?setid=' in href)
            if link_element:
                links.append(f"https://dailymed.nlm.nih.gov{link_element['href']}")

        return drug_results, links
    else:
        return f"Error: {response.status_code}", []


# Function to scrape each drug information page for additional links with the same set_id
def scrape_and_download(set_id, page_url, drug_name):
    # Perform GET request to the drug info page
    response = requests.get(page_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        page_text = soup.get_text(separator="\n", strip=True)
        print(page_text)
        return page_text
        # todo: skip PDF downloads for now...
        # Create a directory for saving PDFs
        # pdf_dir = 'pdfs_{}'.format(drug_name)
        # os.makedirs(pdf_dir, exist_ok=True)

        # pdf_links = []
        #
        # # Find all links that contain the set_id
        # links = soup.find_all('a', href=lambda href: href and f"setid={set_id}" in href)
        #
        # for link in links:
        #     href = link.get('href', '')  # Get the href attribute
        #     if 'type=pdf' in href:  # Check if the href contains 'type=pdf'
        #         pdf_links.append(href)

        # for pdf_url in pdf_links:
        #     pdf_response = requests.get("https://dailymed.nlm.nih.gov/"+pdf_url)
        #     if pdf_response.status_code == 200:
        #         pdf_path = os.path.join(pdf_dir, f"{set_id}.pdf")
        #         with open(pdf_path, 'wb') as pdf_file:
        #             pdf_file.write(pdf_response.content)
        #         print(f"Downloaded PDF for set_id {set_id} ")
        #     else:
        #         print(
        #             f"Failed to download PDF for set_id {set_id}, status code: {pdf_response.status_code}")
    else:
        print(f"Failed to scrape the drug info page: {page_url}, status code: {response.status_code}")
        return None


def research_drug_and_symptoms(drug_name: str, symptoms: str):
    # Call the function to fetch the drug info
    drug_info, drug_links = fetch_drug_info(drug_name)

    if not drug_links:
        print("No drug information found for the given search query.")
        return {"drug_name": drug_name, "symptoms": symptoms, "data": "No drug information found for the given search query."}

    for link in drug_links:
        print(link)

    # for now take only the first link
    drug_info_main_page_link = drug_links[0]
    main_set_id = drug_info_main_page_link.split('setid=')[-1].split('&')[0]

    scraped_text = scrape_and_download(main_set_id, drug_info_main_page_link, drug_name)

    review_text = review_drug_info_for_sympthoms(drug_name, symptoms, scraped_text)

    # print(f"relevant PDF fiels scraped and downloaded to the pdfs_{drug_name} directory.")

    return {"drug_name": drug_name, "symptoms": symptoms, "data": drug_info, "link_data": drug_info_main_page_link, "review_text": review_text}


# Example usage
if __name__ == "__main__":
    res = research_drug_and_symptoms("aspirin", "headache")
    print(res)
    print("-" * 40)