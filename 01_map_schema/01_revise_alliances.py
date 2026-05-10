# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Revise alliances
# Author: Timm Nawrocki
# Last Updated: 2026-05-09
# Usage: Execute in Python 3.9+.
# Description: 'Revise alliances' updates the relationship of the AKVEG Map class schema to alliances in a particular version of the AKNVC.
# ---------------------------------------------------------------------------

# Define version
version = '3.0.3'

# Import packages
import os
import pandas as pd

#### SET UP DIRECTORIES, FILES, AND FIELDS
####____________________________________________________

# Set root directory
drive = 'C:/'
root_folder = 'ACCS_Work'

# Define folder structure
repository_folder = os.path.join(drive, root_folder, 'Repositories/class-descriptions')
aknvc_folder = os.path.join(drive, root_folder, f'Projects/VegetationEcology/AKNVC/Data/version_{version}/processed')

# Define input files
schema_input = os.path.join(repository_folder, 'AKVEG_MapClass_Schema.csv')
aknvc_input = os.path.join(aknvc_folder, f'AKNVC_{version}.xlsx')

# Define output files
schema_output = os.path.join(repository_folder, 'AKVEG_MapClass_Schema_20260509.csv') # For development purposes

#### DEFINE ALLIANCE RELATIONSHIPS
####____________________________________________________

# INSTRUCTIONS: Update the table below to list all alliance codes from the AKNVC that fit within each map class. Only create entries for map classes that target subgroups or alliances. If a map class lacks any described alliances but should have alliances in the future, enter the placeholder text 'undescribed'.

# Define a nested dictionary containing relationships for each map class
class_alliances = {
    # 262.	Arctic Sphagnum-Sedge Peatland, Ombrotrophic
    262: ['undescribed'],
    # 263.	Arctic Brown Moss-Sedge Peatland, Minerotrophic
    263: ['undescribed'],
    # 272.	Arctic Tussock Dwarf Shrub Tundra
    272: ['A2438', 'A2439'],
    # 281.	Arctic Herbaceous Inland Dune
    281: ['A0043ak', 'A0045ak', 'A4294', 'A4295'],
    # 283.	Arctic Dryas (-Willow) Dwarf Shrub
    283: ['A4333', 'A4335'],
    # 284.	Arctic Ericaceous (-Dryas) Dwarf Shrub
    284: ['A4332', 'A4334', 'A4336'],
    # 302.	Arctic Coastal & Estuarine Barren
    302: ['undescribed'],
    # 304.	Arctic Salt-intruded Tundra
    304: ['undescribed'],
    # 305.	Arctic Coastal Dwarf Willow Graminoid
    305: ['A2217', 'A4312'],
    # 306.	Arctic Coastal Salt Marsh
    306: ['A2121', 'A2122', 'A2123', 'A4311', 'A4313'],
    # 315.	Arctic Barren & Sparsely Vegetated Active Floodplain
    315: ['A4362'],
    # 313.	Arctic Dryas (-Willow-Ericaceous) Floodplain
    313: ['undescribed'],
    # 314.	Arctic Herbaceous Active Floodplain
    314: ['undescribed']
}

#### PROCESS AKNVC ALLIANCES
####____________________________________________________

# Read input data sheets
schema_data = pd.read_csv(schema_input)[['bioclimatic_zone', 'structure', 'category', 'physiography_limit',
                                         'code', 'map_class', 'target', 'macrogroup_code', 'macrogroup',
                                         'group_code', 'group']]
alliance_data = pd.read_excel(aknvc_input, sheet_name='mid_levels')

# Join alliance by group
print('Joining alliances by group...')
schema_alliances = pd.merge(schema_data, alliance_data, on='group_code')
schema_alliances = schema_alliances[['code', 'map_class', 'alliance_code', 'alliance_akname']]

# Create a Boolean mask starting with all rows set to True
mask = pd.Series(True, index=schema_alliances.index)

# Loop through the dictionary and update the Boolean mask
print('Creating valid alliance mask...')
for code, retained_list in class_alliances.items():
    is_current_code = schema_alliances['code'] == code
    is_retained_alliance = schema_alliances['alliance_code'].isin(retained_list)
    mask = mask & (~is_current_code | is_retained_alliance)

# Apply the inclusion mask to the dataframe
schema_alliances = schema_alliances[mask]

# Collapse alliance correspondence into code list
print('Collapsing list of alliances...')
collapse_alliances = (schema_alliances
                      .groupby('code')['alliance_code']
                      .apply(lambda x: ', '.join(x.dropna().astype(str)))
                      .reset_index()
                      .rename(columns={'alliance_code': 'alliance_codes'}))

# Identify all map classes that do not correspond to any alliances
missing_codes = set(schema_data['code']) - set(collapse_alliances['code'])

# Generate rows for missing map classes
if missing_codes:
    missing_rows = []
    for code in missing_codes:
        # Identify target from schema
        target = schema_data.loc[schema_data['code'] == code, 'target'].values[0]
        # Define placeholder value
        if class_alliances.get(code) == ['undescribed']:
            placeholder_value = 'undescribed'
        elif target == 'complex':
            placeholder_value = 'complex'
        else:
            placeholder_value = 'none'
        # Append data row
        missing_rows.append({'code': code, 'alliance_codes': placeholder_value})
    # Convert missing rows to dataframe
    missing_data = pd.DataFrame(missing_rows)
    # Combine original collapsed data with generated missing rows
    collapse_alliances = pd.concat([collapse_alliances, missing_data], ignore_index=True)

#### EXPORT MAP SCHEMA
####____________________________________________________

print('Exporting map schema...')

# Join the alliance lists
schema_data = pd.merge(schema_data, collapse_alliances, on='code', how='left')

# Sort all export tables by map class code
schema_data = schema_data.sort_values(by='code')

# Export data
schema_data.to_csv(schema_output, encoding='utf-8', index=False)
