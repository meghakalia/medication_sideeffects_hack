import xml.etree.ElementTree as ET
from collections import Counter
import pandas as pd
import zipfile

# Function to search for reports based on active ingredient
def search_reports_by_active_ingredient(active_ingredient):
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

                # Convert the reaction counter to a DataFrame
                reaction_df = pd.DataFrame(reaction_counter.items(), columns=['Reaction', 'Frequency'])
                reaction_df = reaction_df.sort_values(by='Frequency', ascending=False).reset_index(drop=True)
                
                # Return the DataFrame as a dictionary
                return reaction_df.to_dict(orient='records')

if __name__ == '__main__':
    active_ingredient = "advil"
    reaction_df = search_reports_by_active_ingredient(active_ingredient)

    print("\nReaction Frequency Table:")
    print(reaction_df)
