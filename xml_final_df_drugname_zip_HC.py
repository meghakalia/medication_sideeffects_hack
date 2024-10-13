import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import pandas as pd
import zipfile
# Sample XML data

# Function to search for reports based on active ingredient
def search_reports_by_active_ingredient( active_ingredient):
    with zipfile.ZipFile('1_ADR24Q2.xml.zip', 'r') as zip_file:
    # Check if the XML file exists in the ZIP
        if '1_ADR24Q2.xml' in zip_file.namelist():
        # Read the XML file
            with zip_file.open('1_ADR24Q2.xml') as xml_file:




                tree = ET.parse(xml_file)
                root = tree.getroot()
                matching_reports = []
                reaction_counter = Counter()
    
                safety_reports = root.findall('safetyreport')
    
                for report in safety_reports:
                    patient = report.find('patient')
                    if patient is not None:
                        drugs = patient.findall('drug')
                        for drug in drugs:
                # Check if active ingredient matches
                            active_substance = drug.find('medicinalproduct')
                            if active_substance is not None and active_ingredient.lower() in active_substance.text.lower():
                                matching_reports.append(report)
                    
                    # Extract reactions from this report
                            reactions = patient.findall('reaction')
                            for reaction in reactions:
                                reaction_name = reaction.find('reactionmeddrapt')
                                if reaction_name is not None:
                            # Increment the count for this reaction
                                    reaction_counter[reaction_name.text] += 1
                            break  # Stop once the matching drug is found in this report
        reaction_df = pd.DataFrame(reaction_counter.items(), columns=['Reaction', 'Frequency'])
        reaction_df = reaction_df.sort_values(by='Frequency', ascending=False).reset_index(drop=True)
        # reaction_df.to_json('data.json', orient='records', lines=True)
        dict_result = reaction_df.to_dict(orient='records')

    
        return  dict_result

# xml_file_path='faers_xml_2024q2/1_ADR24Q2.xml.zip'
# xml_name='1_ADR24Q2.xml'
# Example search: find reports with the active ingredient 'INTERFERON BETA-1A'
active_ingredient = "advil"
reaction_df = search_reports_by_active_ingredient( active_ingredient)

# Print number of matching reports
# print(f"Number of reports with active ingredient '{active_ingredient}': {len(matching_reports)}")

# Create a DataFrame from the reaction counts
# reaction_df = pd.DataFrame(reaction_counts.items(), columns=['Reaction', 'Frequency'])

# Sort the DataFrame by frequency in descending order
# reaction_df = reaction_df.sort_values(by='Frequency', ascending=False).reset_index(drop=True)

# Display the reaction frequency table
print("\nReaction Frequency Table:")
print(reaction_df)

# Optionally, if you want to save the table to a CSV file
# reaction_df.to_csv("reaction_frequency_table.csv", index=False)
