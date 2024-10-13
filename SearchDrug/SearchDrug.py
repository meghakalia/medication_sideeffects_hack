# import requests
# from bs4 import BeautifulSoup
#
#
# # Function to perform the GET request and extract drug info using BeautifulSoup
# def fetch_drug_info(drug_name: str):
#     url = f'https://dailymed.nlm.nih.gov/dailymed/search.cfm?labeltype=all&query={drug_name}&audience=consumer'
#
#     headers = {
#         'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
#         'accept-language': 'en-US,en;q=0.9',
#         'priority': 'u=0, i',
#         'referer': f'https://dailymed.nlm.nih.gov/dailymed/search.cfm?labeltype=all&query={drug_name}&audience=consumer',
#         'sec-ch-ua': '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
#         'sec-ch-ua-mobile': '?0',
#         'sec-ch-ua-platform': '"Windows"',
#         'sec-fetch-dest': 'document',
#         'sec-fetch-mode': 'navigate',
#         'sec-fetch-site': 'same-origin',
#         'sec-fetch-user': '?1',
#         'upgrade-insecure-requests': '1',
#         'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36'
#     }
#
#     # Perform the GET request
#     response = requests.get(url, headers=headers)
#
#     if response.status_code == 200:
#         soup = BeautifulSoup(response.text, 'html.parser')
#         drug_results = []
#         links = []
#
#         # Find the search results
#         articles = soup.find_all('article', class_='row')
#
#         for article in articles:
#             drug_name = article.find('h2', class_='drug-name').text.strip()
#             ndc_codes = article.find('span', class_='ndc-codes').text.strip()
#
#             # Handle possible missing packager info
#             packager_element = article.find('li', text=lambda x: x and 'Packager' in x)
#             packager = packager_element.find_next(
#                 'span').text.strip() if packager_element else 'Packager information not found'
#
#             drug_results.append({
#                 'drug_name': drug_name,
#                 'ndc_codes': ndc_codes,
#                 'packager': packager
#             })
#
#             # Extract all links to drug information pages
#             link_element = article.find('a', href=lambda href: href and 'drugInfo.cfm?setid=' in href)
#             if link_element:
#                 links.append(f"https://dailymed.nlm.nih.gov{link_element['href']}")
#
#         return drug_results, links
#     else:
#         return f"Error: {response.status_code}", []
#
#
# # Example usage
# if __name__ == "__main__":
#     drug_info, drug_links = fetch_drug_info("aspirin")
#
#     # Print drug info
#     for info in drug_info:
#         print(f"Drug Name: {info['drug_name']}")
#         print(f"NDC Codes: {info['ndc_codes']}")
#         print(f"Packager: {info['packager']}")
#         print("-" * 40)
#
#     # Print all the extracted drug links
#     print("Extracted Drug Information Links:")
#     for link in drug_links:
#         print(link)


import requests
from bs4 import BeautifulSoup
import os


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


# Function to extract set_id from URLs and download corresponding PDFs
def download_pdfs(links):
    pdf_dir = 'pdfs'
    os.makedirs(pdf_dir, exist_ok=True)  # Create directory to save PDFs if it doesn't exist

    for link in links:
        # Extract set_id from the link
        set_id = link.split('setid=')[-1].split('&')[0]
        pdf_url = f"https://dailymed.nlm.nih.gov/dailymed/medguide.cfm?setid={set_id}"

        # Download the PDF
        response = requests.get(pdf_url)
        if response.status_code == 200:
            pdf_path = os.path.join(pdf_dir, f"{set_id}.pdf")
            with open(pdf_path, 'wb') as pdf_file:
                pdf_file.write(response.content)
            print(f"Downloaded PDF for set_id {set_id}")
        else:
            print(f"Failed to download PDF for set_id {set_id}, status code: {response.status_code}")


# Example usage
if __name__ == "__main__":
    drug_info, drug_links = fetch_drug_info("aspirin")

    # Print drug info
    for info in drug_info:
        print(f"Drug Name: {info['drug_name']}")
        print(f"NDC Codes: {info['ndc_codes']}")
        print(f"Packager: {info['packager']}")
        print("-" * 40)

    # Print all the extracted drug links
    print("Extracted Drug Information Links:")
    for link in drug_links:
        print(link)

    # Download PDFs for all set_ids in the links
    download_pdfs(drug_links)
