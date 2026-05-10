# ---------------------------------------------------------------------------
# Template script for alliance or strata descriptions
# Author: Timm Nawrocki, Amanda Droghini, Rhiannon Glover, Lindsey Flagstad, Alaska Center for Conservation Science
# Last Updated: 2026-02-10
# Usage: Must be executed in a Python 3.12+ installation.
# Description: "Template script for alliance or strata descriptions" provides a template for writing descriptions for alliances or strata from the AKVEG Database and a data entry file.
# ---------------------------------------------------------------------------

# Define target alliance code
unit_code = '29_ArcticBrownMossSedgePeatlandMinerotrophic'

# Import libraries
import os
from dbfread import DBF
import markdown
import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio
import plotly.express as px
import plotly.graph_objects as go
import kaleido
from akutils import connect_database_postgresql
from akutils import query_to_dataframe

# Initialize kaleido
kaleido.get_chrome_sync()

#### SET UP DIRECTORIES, FILES, AND FIELDS
####____________________________________________________

# Set root directory
drive = 'C:/'
root_folder = 'ACCS_Work'

# Define folder structure
database_repository = os.path.join(drive, root_folder, 'Repositories/akveg-database')
credentials_folder = os.path.join(drive, root_folder, 'Administrative/Credentials/akveg_private_read')
description_folder = os.path.join(drive, root_folder, 'Repositories/class-descriptions')
input_folder = os.path.join(description_folder, '00_data_entry')
plot_folder = os.path.join(description_folder, '03_plot_html')
output_folder = os.path.join(description_folder, '04_description_html')

# Define input data
veg_input = os.path.join(drive, root_folder,
                         'Projects/VegetationEcology/DoD_Navy_Arctic/Data/Data_Output/evt/round_20260123',
                         'ArcticCoastal_Vegetation_1600mmu_10m_3338.tif')
elevation_input = os.path.join(drive, root_folder,
                               'Data/topography',
                               'Elevation_10m_3338.tif')
slope_input = os.path.join(drive, root_folder,
                           'Data/topography',
                           'Slope_10m_3338.tif')
schema_input = os.path.join(drive, root_folder,
                            'Projects/VegetationEcology/AKVEG_Map/Data/Data_Input',
                            'schema_data/AKVEG_Schema_20260119.xlsx')
text_input = os.path.join(input_folder, f'{unit_code}.md')

# Define queries
taxa_file = os.path.join(database_repository, 'queries/00_taxonomy.sql')
project_file = os.path.join(database_repository, 'queries/01_project.sql')
site_visit_file = os.path.join(database_repository, 'queries/03_site_visit.sql')
vegetation_file = os.path.join(database_repository, 'queries/05_vegetation.sql')
abiotic_file = os.path.join(database_repository, 'queries/06_abiotic_top_cover.sql')
tussock_file = os.path.join(database_repository, 'queries/07_whole_tussock_cover.sql')
ground_file = os.path.join(database_repository, 'queries/08_ground_cover.sql')
structural_file = os.path.join(database_repository, 'queries/09_structural_group_cover.sql')
shrub_file = os.path.join(database_repository, 'queries/11_shrub_structure.sql')
environment_file = os.path.join(database_repository, 'queries/12_environment.sql')
soilmetrics_file = os.path.join(database_repository, 'queries/13_soil_metrics.sql')
soilhorizons_file = os.path.join(database_repository, 'queries/14_soil_horizons.sql')

#### DEFINE FUNCTIONS
####------------------------------

# Define 10th percentile
def percentile_10(x):
    return x.quantile(0.10)

# Define 25th percentile
def percentile_25(x):
    return x.quantile(0.25)

# Define 75th percentile
def percentile_75(x):
    return x.quantile(0.75)

# Define 90th percentile
def percentile_90(x):
    return x.quantile(0.90)

# Define a function to parse text from a markdown file
def parse_markdown(text_input, label):
    # Import package
    import re

    # Define pattern
    pattern = r'\*\*' + label + r':\*\*\s*(.*)'

    # Set empty outputs
    text_output = None

    # Parse markdown by label
    try:
        with open(text_input, 'r', encoding='utf-8') as input_file:
            content = input_file.read()
        match = re.search(pattern, content)
        if match:
            text_output = match.group(1).strip()

    # Provide error warning
    except FileNotFoundError:
        print(f"Error: The file {text_input} was not found.")

    # Return outputs
    return text_output

#### PARSE TEXT DESCRIPTIONS
####____________________________________________________

# Parse unit name
unit_name = parse_markdown(text_input, 'Unit Name')
level_text = parse_markdown(text_input, 'Level')
photo_text = parse_markdown(text_input, 'Photos')
photo_list = photo_text.split(', ')

#### QUERY AND FILTER AKVEG SITE VISITS
####------------------------------

# Create a connection to the AKVEG PostgreSQL database
authentication_file = os.path.join(credentials_folder, 'authentication_akveg_private.csv')
database_connection = connect_database_postgresql(authentication_file)

# Read taxonomy standard from AKVEG Database
taxa_read = open(taxa_file, 'r')
taxa_query = taxa_read.read()
taxa_read.close()
taxa_data = query_to_dataframe(database_connection, taxa_query)

# Read site visit data from AKVEG Database
site_visit_read = open(site_visit_file, 'r')
site_visit_query = site_visit_read.read()
site_visit_read.close()
site_visit_data = query_to_dataframe(database_connection, site_visit_query)
site_visit_data['obs_datetime'] = pd.to_datetime(site_visit_data['observe_date'])
site_visit_data['obs_year'] = site_visit_data['obs_datetime'].dt.year

# Create geodataframe
site_visit_data = gpd.GeoDataFrame(
    site_visit_data,
    geometry=gpd.points_from_xy(site_visit_data.longitude_dd,
                                site_visit_data.latitude_dd),
    crs='EPSG:4269')

# Convert geodataframe to EPSG:3338
site_visit_data = site_visit_data.to_crs(crs='EPSG:3338')

# Extract coordinates in EPSG:3338
site_visit_data['cent_x'] = site_visit_data.geometry.x
site_visit_data['cent_y'] = site_visit_data.geometry.y

# Filter by observation year
site_visit_data = site_visit_data[site_visit_data['obs_year'] >= 2000]

# Filter by perspective
site_visit_data = site_visit_data[site_visit_data['perspective'] == 'ground']

# Filter by taxonomic scopes
site_visit_data = site_visit_data[
    site_visit_data['scope_vascular'].isin(['exhaustive', 'non-trace species'])
]

# Identify site visits appropriate for analyses of bryophytes
bryophyte_sites = site_visit_data[
    site_visit_data['scope_bryophyte'].isin(['exhaustive', 'non-trace species', 'common species'])
]

# Identify site visits appropriate for analyses of lichens
lichen_sites = site_visit_data[
    site_visit_data['scope_lichen'].isin(['exhaustive', 'non-trace species', 'common species'])
]

# Identify coordinates from site visit data
coordinates = [(x, y) for x, y in zip(site_visit_data.geometry.x, site_visit_data.geometry.y)]

# Extract raster EVT to sites
with rasterio.open(veg_input) as src:
    # Extract raster values
    extracted_values = src.sample(coordinates)
    # Append values to data frame
    site_visit_data['raster_value'] = [x[0] for x in extracted_values]

# Extract elevation raster to sites
with rasterio.open(elevation_input) as src:
    # Extract raster values
    extracted_values = src.sample(coordinates)
    # Append values to data frame
    site_visit_data['elevation_m'] = [x[0] for x in extracted_values]

# Extract slope raster to sites
with rasterio.open(slope_input) as src:
    # Extract raster values
    extracted_values = src.sample(coordinates)
    # Append values to data frame
    site_visit_data['slope_deg'] = [x[0] for x in extracted_values]

# Replace value with label
raster_attributes = DBF(veg_input + '.vat.dbf', load=True)
attribute_data = pd.DataFrame(iter(raster_attributes))
site_visit_data = pd.merge(left=site_visit_data,
                           right=attribute_data,
                           left_on='raster_value',
                           right_on='VALUE',
                           how='left')
site_visit_data = site_visit_data.drop(labels=['raster_value', 'VALUE', 'COUNT'], axis=1)
site_visit_data = site_visit_data.rename(columns={'LABEL': 'veg_type'})

# Filter to unit name
site_visit_data = site_visit_data[site_visit_data['veg_type'] == unit_name]

# Select columns
site_visit_data = site_visit_data[['site_visit_code', 'project_code', 'site_code', 'data_tier',
                                   'observe_date', 'scope_vascular', 'scope_bryophyte', 'scope_lichen',
                                   'perspective', 'cover_method', 'structural_class', 'homogeneous',
                                   'plot_dimensions_m', 'latitude_dd', 'longitude_dd',
                                   'cent_x', 'cent_y', 'veg_type', 'elevation_m', 'slope_deg']]

# Rename fields for export as shapefile to meet shapefile field character length constraint
export_point_data = site_visit_data.rename(columns={'site_visit_code': 'st_vst',
                                                    'project_code': 'prjct_cd',
                                                    'site_code': 'st_code',
                                                    'observe_date': 'obs_date',
                                                    'scope_vascular': 'scp_vasc',
                                                    'scope_bryophyte': 'scp_bryo',
                                                    'scope_lichen': 'scp_lich',
                                                    'perspective': 'perspect',
                                                    'cover_method': 'cvr_mthd',
                                                    'structural_class': 'strc_class',
                                                    'homogeneous': 'hmgneous',
                                                    'plot_dimensions_m': 'plt_dim_m',
                                                    'latitude_dd': 'lat_dd',
                                                    'longitude_dd': 'long_dd',
                                                    'elevation_m': 'elev_m'
                                                    })

# Export site visit data to shapefile (uncomment for shapefile export)
#site_point_output = os.path.join(site_folder, unit_code + '_SiteVisits_3338.shp')
#site_point_data = gpd.GeoDataFrame(
#    export_point_data,
#    geometry=gpd.points_from_xy(site_visit_data.cent_x,
#                                site_visit_data.cent_y),
#    crs='EPSG:3338')
#site_point_data.to_file(site_point_output)

# Write where statement for site visits
input_sql = '\r\nWHERE site_visit.site_visit_code IN ('
for site_visit in site_visit_data['site_visit_code']:
    input_sql = input_sql + r"'" + site_visit + r"', "
input_sql = input_sql[:-2] + r');'

# Read project data from AKVEG Database for selected site visits
project_read = open(project_file, 'r')
project_query = project_read.read()
project_read.close()
project_query = project_query.replace(';', input_sql)
project_data = query_to_dataframe(database_connection, project_query).sort_values('project_code')

#### QUERY AND PROCESS AKVEG VEGETATION COVER DATA
####------------------------------

# Read vegetation cover data from AKVEG Database for selected site visits
vegetation_read = open(vegetation_file, 'r')
vegetation_query = vegetation_read.read()
vegetation_read.close()
vegetation_query = vegetation_query.replace(';', input_sql)
vegetation_data = query_to_dataframe(database_connection, vegetation_query)

# Enforce numeric data type
vegetation_data['cover_percent'] = (pd.to_numeric(vegetation_data['cover_percent'])
                                    # Replace -999 explicit absence values with 0
                                    .replace(-999, 0))

# Enforce absolute cover
vegetation_data = vegetation_data[
    vegetation_data['cover_type'].isin(['absolute foliar cover', 'absolute canopy cover'])
]

# Enforce live vegetation
vegetation_data = vegetation_data[vegetation_data['dead_status'] == False]

# Join vegetation and taxa data
vegetation_data = pd.merge(left=vegetation_data,
                           right=taxa_data,
                           left_on='name_accepted',
                           right_on='taxon_name',
                           how='left')

# Select vegetation data fields
vegetation_data = vegetation_data[[
    'site_visit_code', 'name_accepted', 'cover_percent',
    'taxon_genus', 'taxon_level', 'taxon_category', 'taxon_habit'
]]

# Correct ambiguous taxon habits
vegetation_data = (vegetation_data
                   .replace('dwarf shrub, shrub', 'shrub')
                   .replace('dwarf shrub, shrub, tree', 'shrub'))

# Filter data appropriate for vascular plant analyses
vascular_data = vegetation_data[vegetation_data['taxon_category'].isin([
    'monocot', 'eudicot', 'fern', 'gymnosperm', 'horsetail', 'lycophyte'
])]

# Filter data appropriate for bryophyte analyses
bryophyte_data = vegetation_data[vegetation_data['site_visit_code'].isin(
    bryophyte_sites['site_visit_code'].tolist()
)]
bryophyte_data = bryophyte_data[bryophyte_data['taxon_category'].isin([
    'liverwort', 'moss', 'hornwort', 'functional group', 'unknown'
])]
bryophyte_data = bryophyte_data[(bryophyte_data['taxon_category'] != 'functional group')
                                | ((bryophyte_data['taxon_category'] != 'functional group')
                                   & (bryophyte_data['name_accepted'].isin([
            'non-thalloid liverwort', 'thalloid liverwort', 'feathermoss (other)',
            'feathermoss (N-fixing)', 'Sphagnum moss', 'turf moss'
        ])))
                                | ((bryophyte_data['taxon_category'] != 'unknown')
                                   & (bryophyte_data['name_accepted'].isin([
            'liverwort', 'moss'
        ])))]

# Perform bryophyte aggregation
bryophyte_unique = bryophyte_data['name_accepted'].unique()
bryophyte_data['name_accepted'] = np.where(bryophyte_data['taxon_genus'] == 'Brachythecium',
                                           'Brachythecium', bryophyte_data['name_accepted'])
bryophyte_data['name_accepted'] = np.where(bryophyte_data['taxon_genus'] == 'Calliergon',
                                           'Calliergon', bryophyte_data['name_accepted'])
bryophyte_data['name_accepted'] = np.where(bryophyte_data['taxon_genus'] == 'Cinclidium',
                                           'Cinclidium', bryophyte_data['name_accepted'])
bryophyte_data['name_accepted'] = np.where(bryophyte_data['taxon_genus'] == 'Dicranum',
                                           'Dicranum', bryophyte_data['name_accepted'])
bryophyte_data['name_accepted'] = np.where(bryophyte_data['taxon_genus'] == 'Drepanocladus',
                                           'Drepanocladus', bryophyte_data['name_accepted'])
bryophyte_data['name_accepted'] = np.where(bryophyte_data['taxon_genus'] == 'Hamatocaulis',
                                           'Hamatocaulis', bryophyte_data['name_accepted'])
bryophyte_data['name_accepted'] = np.where(bryophyte_data['taxon_genus'] == 'Loeskypnum',
                                           'Loeskypnum', bryophyte_data['name_accepted'])
bryophyte_data['name_accepted'] = np.where(bryophyte_data['taxon_genus'] == 'Meesia',
                                           'Meesia', bryophyte_data['name_accepted'])
bryophyte_data['name_accepted'] = np.where(bryophyte_data['taxon_genus'] == 'Polytrichum',
                                           'Polytrichum', bryophyte_data['name_accepted'])
bryophyte_data['name_accepted'] = np.where(bryophyte_data['taxon_genus'] == 'Pseudocalliergon',
                                           'Pseudocalliergon', bryophyte_data['name_accepted'])
bryophyte_data['name_accepted'] = np.where(bryophyte_data['taxon_genus'] == 'Racomitrium',
                                           'Racomitrium', bryophyte_data['name_accepted'])
bryophyte_data['name_accepted'] = np.where(bryophyte_data['taxon_genus'] == 'Rhizomnium',
                                           'Rhizomnium', bryophyte_data['name_accepted'])
bryophyte_data['name_accepted'] = np.where(bryophyte_data['taxon_genus'] == 'Sarmentypnum',
                                           'Sarmentypnum', bryophyte_data['name_accepted'])
bryophyte_data['name_accepted'] = np.where(bryophyte_data['taxon_genus'] == 'Scorpidium',
                                           'Scorpidium', bryophyte_data['name_accepted'])
bryophyte_data['name_accepted'] = np.where(bryophyte_data['taxon_genus'] == 'Sphagnum',
                                           'Sphagnum', bryophyte_data['name_accepted'])

# Calculate bryophyte sums
bryophyte_data = (bryophyte_data.groupby(['site_visit_code', 'name_accepted'])['cover_percent']
                  .sum()
                  .to_frame()
                  .reset_index())
bryophyte_data = pd.merge(left=bryophyte_data,
                          right=taxa_data,
                          left_on='name_accepted',
                          right_on='taxon_name',
                          how='left')
bryophyte_data = bryophyte_data[[
    'site_visit_code', 'name_accepted', 'cover_percent',
    'taxon_genus', 'taxon_level', 'taxon_category', 'taxon_habit'
]]

# Filter data appropriate for lichen analyses
lichen_data = vegetation_data[vegetation_data['site_visit_code'].isin(
    lichen_sites['site_visit_code'].tolist()
)]
lichen_data = lichen_data[lichen_data['taxon_category'] == 'lichen']
lichen_data = lichen_data[(lichen_data['taxon_category'] != 'functional group')
                          | ((lichen_data['taxon_category'] != 'functional group')
                             & (lichen_data['name_accepted'].isin([
            'arboreal lichen', 'crustose lichen (orange)', 'crustose lichen (non-orange)',
            'foliose lichen (other)', 'foliose lichen (N-fixing)', 'forage lichen',
            'fruticose lichen (N-fixing)', 'fruticose lichen (other)'
        ])))
                          | ((lichen_data['taxon_category'] != 'unknown')
                             & (lichen_data['name_accepted'].isin([
            'lichen', 'crustose lichen', 'fruticose lichen', 'foliose lichen'
        ])))]

# Perform bryophyte aggregation
lichen_unique = lichen_data['name_accepted'].unique()
lichen_data['name_accepted'] = np.where(lichen_data['taxon_genus'] == 'Bryoria',
                                        'Bryoria', lichen_data['name_accepted'])
lichen_data['name_accepted'] = np.where(lichen_data['taxon_genus'] == 'Dactylina',
                                        'Dactylina', lichen_data['name_accepted'])
lichen_data['name_accepted'] = np.where(lichen_data['taxon_genus'] == 'Lobaria',
                                        'Lobaria', lichen_data['name_accepted'])
lichen_data['name_accepted'] = np.where(lichen_data['taxon_genus'] == 'Masonhalea',
                                        'Masonhalea richardsonii', lichen_data['name_accepted'])
lichen_data['name_accepted'] = np.where(lichen_data['taxon_genus'] == 'Nephroma',
                                        'Nephroma', lichen_data['name_accepted'])
lichen_data['name_accepted'] = np.where(lichen_data['taxon_genus'] == 'Peltigera',
                                        'Peltigera', lichen_data['name_accepted'])
lichen_data['name_accepted'] = np.where(lichen_data['taxon_genus'] == 'Sphaerophorus',
                                        'Sphaerophorus', lichen_data['name_accepted'])
lichen_data['name_accepted'] = np.where(lichen_data['taxon_genus'] == 'Stereocaulon',
                                        'Stereocaulon', lichen_data['name_accepted'])
lichen_data['name_accepted'] = np.where(lichen_data['taxon_genus'] == 'Thamnolia',
                                        'Thamnolia', lichen_data['name_accepted'])

# Calculate lichen sums
lichen_data = (lichen_data.groupby(['site_visit_code', 'name_accepted'])['cover_percent']
               .sum()
               .to_frame()
               .reset_index())
lichen_data = pd.merge(left=lichen_data,
                       right=taxa_data,
                       left_on='name_accepted',
                       right_on='taxon_name',
                       how='left')
lichen_data = lichen_data[[
    'site_visit_code', 'name_accepted', 'cover_percent',
    'taxon_genus', 'taxon_level', 'taxon_category', 'taxon_habit'
]]

#### QUERY OTHER AKVEG DATA
####------------------------------

# Read abiotic top cover data from AKVEG Database for selected site visits
abiotic_read = open(abiotic_file, 'r')
abiotic_query = abiotic_read.read()
abiotic_read.close()
abiotic_query = abiotic_query.replace(';', input_sql)
abiotic_data = query_to_dataframe(database_connection, abiotic_query)
abiotic_data['cover_percent'] = pd.to_numeric(abiotic_data['cover_percent'])

# Read whole tussock cover data from AKVEG Database for selected site visits
tussock_read = open(tussock_file, 'r')
tussock_query = tussock_read.read()
tussock_read.close()
tussock_query = tussock_query.replace(';', input_sql)
tussock_data = query_to_dataframe(database_connection, tussock_query)

# Read ground cover data from AKVEG Database for selected site visits
ground_read = open(ground_file, 'r')
ground_query = ground_read.read()
ground_read.close()
ground_query = ground_query.replace(';', input_sql)
ground_data = query_to_dataframe(database_connection, ground_query)

# Read structural group cover data from AKVEG Database for selected site visits
structural_read = open(structural_file, 'r')
structural_query = structural_read.read()
structural_read.close()
structural_query = structural_query.replace(';', input_sql)
structural_data = query_to_dataframe(database_connection, structural_query)

# Read shrub structure data from AKVEG Database for selected site visits
shrub_read = open(shrub_file, 'r')
shrub_query = shrub_read.read()
shrub_read.close()
shrub_query = shrub_query.replace(';', input_sql)
shrub_data = query_to_dataframe(database_connection, shrub_query)

# Read environment data from AKVEG Database for selected site visits
environment_read = open(environment_file, 'r')
environment_query = environment_read.read()
environment_read.close()
environment_query = environment_query.replace(';', input_sql)
environment_data = query_to_dataframe(database_connection, environment_query)

# Read soil metrics data from AKVEG Database for selected site visits
soilmetrics_read = open(soilmetrics_file, 'r')
soilmetrics_query = soilmetrics_read.read()
soilmetrics_read.close()
soilmetrics_query = soilmetrics_query.replace(';', input_sql)
soilmetrics_data = query_to_dataframe(database_connection, soilmetrics_query)

# Read soil horizons data from AKVEG Database for selected site visits
soilhorizons_read = open(soilhorizons_file, 'r')
soilhorizons_query = soilhorizons_read.read()
soilhorizons_read.close()
soilhorizons_query = soilhorizons_query.replace(';', input_sql)
soilhorizons_data = query_to_dataframe(database_connection, soilhorizons_query)

#### PROCESS VEGETATION STRUCTURE
####____________________________________________________

# Calculate woody canopy height
canopy_data = shrub_data[shrub_data['height_type'].isin(
    ['point-intercept mean', 'mean']
)]['height_cm'].dropna().to_frame()
canopy_data['height_cm'] = pd.to_numeric(canopy_data['height_cm'])
canopy_data = canopy_data[canopy_data['height_cm'] != -999]
canopy_data = (canopy_data['height_cm']
               .agg(['mean',
                     'std',
                     'median',
                     'min',
                     'max',
                     percentile_10,
                     percentile_25,
                     percentile_75,
                     percentile_90])
               .to_frame()
               .transpose())

# Calculate whole tussock cover
tussock_data = tussock_data[tussock_data['cover_type'].isin(
    ['absolute foliar cover', 'absolute canopy cover']
)]['cover_percent'].dropna().to_frame()
tussock_data['cover_percent'] = pd.to_numeric(tussock_data['cover_percent'])
tussock_data = tussock_data[tussock_data['cover_percent'] != -999]
tussock_data = (tussock_data['cover_percent']
                .agg(['mean',
                      'std',
                      'median',
                      'min',
                      'max',
                      percentile_10,
                      percentile_25,
                      percentile_75,
                      percentile_90])
                .to_frame()
                .transpose())

# Create structure statistics
table_structure = (pd.concat([canopy_data, tussock_data], axis=0)
                   .reset_index()
                   .rename(columns={'index': 'Characteristic',
                                    'mean': 'Mean',
                                    'percentile_10': '10th Percentile',
                                    'percentile_90': '90th Percentile'}))
table_structure['Characteristic'] = np.where(table_structure['Characteristic'] == 'height_cm',
                                             'Woody Canopy Height (cm)',
                                             table_structure['Characteristic'])
table_structure['Characteristic'] = np.where(table_structure['Characteristic'] == 'cover_percent',
                                             'Whole Tussock Cover (%)',
                                             table_structure['Characteristic'])
table_structure = table_structure[['Characteristic', 'Mean', '10th Percentile', '90th Percentile']]
table_structure = table_structure.round(1)

# Calculate vascular structure
structure_vascular = (vascular_data
                      # Calculate pivot table to sum taxon habit cover while filling zeros
                      .pivot_table(index='site_visit_code',
                                   columns='taxon_habit',
                                   values='cover_percent',
                                   aggfunc='sum',
                                   fill_value=0)
                      # Calculate mean cover by taxon habit
                      .mean()
                      .to_frame(name='mean')
                      .rename(columns={'taxon_habit': 'structure'})
                      )

# Calculate bryophyte structure
structure_bryophyte = (bryophyte_data
                       # Calculate pivot table to sum taxon habit cover while filling zeros
                       .pivot_table(index='site_visit_code',
                                    columns='taxon_habit',
                                    values='cover_percent',
                                    aggfunc='sum',
                                    fill_value=0)
                       # Calculate mean cover by taxon habit
                       .mean()
                       .to_frame(name='mean')
                       .rename(columns={'taxon_habit': 'structure'})
                       )

# Calculate lichen structure
structure_lichen = (lichen_data
                    # Calculate pivot table to sum taxon habit cover while filling zeros
                    .pivot_table(index='site_visit_code',
                                 columns='taxon_habit',
                                 values='cover_percent',
                                 aggfunc='sum',
                                 fill_value=0)
                    # Calculate mean cover by taxon habit
                    .mean()
                    .to_frame(name='mean')
                    .rename(columns={'taxon_habit': 'structure'})
                    )

# Concatenate biotic structure
structure_biotic = pd.concat([structure_vascular, structure_bryophyte, structure_lichen], axis=0)

# Calculate biotic sum
biotic_sum = structure_biotic['mean'].sum()
abiotic_remainder = 100 - biotic_sum

# Calculate abiotic top cover mean
structure_abiotic = (abiotic_data.groupby('abiotic_element')['cover_percent']
                     .mean()
                     .to_frame(name='mean')
                     .rename(columns={'abiotic_element': 'structure'}))

# Rescale abiotic top cover data
abiotic_sum = structure_abiotic['mean'].sum()
abiotic_adjustment = abiotic_remainder / abiotic_sum
structure_abiotic['mean'] = structure_abiotic['mean'] * abiotic_adjustment

# Concatenate rows from structure and abiotic summary tables
structure_summary = (pd.concat([structure_biotic, structure_abiotic], axis=0)
                     .round(1))

# Remove zero values
structure_summary = (structure_summary[structure_summary['mean'] > 0]
                     .reset_index()
                     .rename(columns={'index': 'structure'}))
structure_summary = structure_summary[['structure', 'mean']]
structure_summary['structure'] = (structure_summary['structure']
                                  .str.title()
                                  .replace('Spore-Bearing', 'Spore-bearing'))

# Define standard element colors
structure_colors = {
    'Coniferous Tree': '#346429',
    'Broadleaf Tree': '#87C58F',
    'Shrub': '#6A1837',
    'Dwarf Shrub': '#466F81',
    'Graminoid': '#DF9E9E',
    'Forb': '#C5BCD5',
    'Spore-bearing': '#B6BF8C',
    'Moss': '#59C8A8',
    'Liverwort': '#C8F1E5',
    'Lichen': '#FFFFBE',
    'Water': '#BEE8FF',
    'Litter (< 2mm)': '#CDAA66',
    'Dead Standing Woody Vegetation': '#897044',
    'Soil': '#828282'
}

# Create structure treemap plot
structure_plot = px.treemap(
    structure_summary,
    path=['structure'],
    values='mean',
    color='structure',
    color_discrete_map=structure_colors
)

# Update plot formatting
structure_plot.update_traces(
    # Increase label font size
    textfont=dict(size=18),
    # Restrict hover to show only the label and the mean value (formatted)
    hovertemplate='<b>%{label}</b><br>Mean: %{value:.1f}%<extra></extra>'
)

# Update layout for margins and dimensions
structure_plot.update_layout(
    margin=dict(t=0, l=0, r=0, b=0),
    autosize=True,
    width=None,
    height=400
)

# Export to HTML (interactive) and PNG (publication)
structure_output = os.path.join(plot_folder, unit_code + '_Structure.html')
structure_plot.write_html(structure_output, config={'responsive': True})

#### PROCESS DIAGNOSTIC SPECIES SETS
####____________________________________________________

# Read diagnostic schema data
schema_data = pd.read_excel(schema_input, sheet_name='foliar_cover')[[
    'target', 'constituents'
]].rename(columns={'target': 'diagnostic set'}).dropna()
schema_data['diagnostic set'].unique()

# Join diagnostic schema to vascular data
diagnostic_vascular = pd.merge(left=vascular_data,
                               right=schema_data,
                               left_on='name_accepted',
                               right_on='constituents',
                               how='inner')
diagnostic_vascular = (diagnostic_vascular
                       .groupby(['site_visit_code', 'diagnostic set'])['cover_percent']
                       .sum()
                       .to_frame()
                       .reset_index())

# Join diagnostic schema to bryophyte data
diagnostic_bryophyte = pd.merge(left=bryophyte_data,
                                right=schema_data,
                                left_on='name_accepted',
                                right_on='constituents',
                                how='inner')
diagnostic_bryophyte = (diagnostic_bryophyte
                        .groupby(['site_visit_code', 'diagnostic set'])['cover_percent']
                        .sum()
                        .to_frame()
                        .reset_index())

# Calculate diagnostic constancy for vascular plants
constancy_diagnostic_vasc = (diagnostic_vascular['diagnostic set']
                             .value_counts()
                             .to_frame()
                             .rename(columns={'count': 'occurrences'}))
constancy_diagnostic_vasc['constancy'] = (constancy_diagnostic_vasc['occurrences']
                                          / len(diagnostic_vascular['site_visit_code'].unique())) * 100

# Calculate diagnostic constancy for bryophytes
constancy_diagnostic_bryo = (diagnostic_bryophyte['diagnostic set']
                             .value_counts()
                             .to_frame()
                             .rename(columns={'count': 'occurrences'}))
constancy_diagnostic_bryo['constancy'] = (constancy_diagnostic_bryo['occurrences']
                                          / len(diagnostic_bryophyte['site_visit_code'].unique())) * 100

# Concatenate constancy tables
constancy_diagnostic = pd.concat([constancy_diagnostic_vasc.reset_index(),
                                  constancy_diagnostic_bryo.reset_index()], axis=0)

# Summarize diagnostic sets for vascular plants
cover_diagnostic_vasc = (diagnostic_vascular
                         # Calculate pivot table to sum cover while filling zeros
                         .pivot_table(index='site_visit_code',
                                      columns='diagnostic set',
                                      values='cover_percent',
                                      aggfunc='sum',
                                      fill_value=0)
                         .agg(['mean',
                               'std',
                               'median',
                               'min',
                               'max',
                               percentile_10,
                               percentile_25,
                               percentile_75,
                               percentile_90])
                         .transpose()
                         )

# Summarize diagnostic sets for bryophytes
cover_diagnostic_bryo = (diagnostic_bryophyte
                         # Calculate pivot table to sum cover while filling zeros
                         .pivot_table(index='site_visit_code',
                                      columns='diagnostic set',
                                      values='cover_percent',
                                      aggfunc='sum',
                                      fill_value=0)
                         .agg(['mean',
                               'std',
                               'median',
                               'min',
                               'max',
                               percentile_10,
                               percentile_25,
                               percentile_75,
                               percentile_90])
                         .transpose()
                         )

# Concatenate cover tables
cover_diagnostic = pd.concat([cover_diagnostic_vasc, cover_diagnostic_bryo], axis=0)

# Join diagnostic data
stats_diagnostic = (pd.merge(left=constancy_diagnostic.reset_index(),
                             right=cover_diagnostic.reset_index(),
                             on='diagnostic set',
                             how='left')
                    .round(1)
                    .rename(columns={'percentile_10': '10th percentile',
                                     'percentile_25': '25th percentile',
                                     'percentile_75': '75th percentile',
                                     'percentile_90': '90th percentile'}))

# Filter floristic data for constancy and mean cover limits
stats_diagnostic = stats_diagnostic[(stats_diagnostic['75th percentile'] >= 1)
                                    & (((stats_diagnostic['constancy'] >= 25)
                                        & (stats_diagnostic['mean'] >= 2))
                                       | ((stats_diagnostic['constancy'] >= 50)
                                          & (stats_diagnostic['mean'] >= 1)))]
stats_diagnostic = stats_diagnostic.sort_values(by='mean', ascending=True)

# Calculate range
stats_diagnostic['range_width'] = stats_diagnostic['90th percentile'] - stats_diagnostic['10th percentile']

# Create custom data array
custom_diagnostic = np.stack([stats_diagnostic['constancy'], stats_diagnostic['90th percentile']], axis=-1)

# Calculate plot height
height_diagnostic = 50 * len(stats_diagnostic)

# Create floristic range plot
diagnostic_plot = go.Figure()
diagnostic_plot.add_trace(go.Bar(
    y=stats_diagnostic['diagnostic set'],
    x=stats_diagnostic['range_width'],
    base=stats_diagnostic['10th percentile'],
    orientation='h',
    width=0.4,
    name='10th-90th Range',
    marker=dict(
        color=stats_diagnostic['constancy'],
        colorscale='Viridis',
        colorbar=dict(title='Constancy'),
        line=dict(width=0)
    ),
    showlegend=True,
    customdata=custom_diagnostic,
    hovertemplate='%{y}<br>Constancy: %{customdata[0]}%<br>10th Percentile: %{base}%<br>90th Percentile: %{customdata[1]}%<extra></extra>'
))

# Add scatterplot for means
diagnostic_plot.add_trace(go.Scatter(
    y=stats_diagnostic['diagnostic set'],
    x=stats_diagnostic['mean'],
    mode='markers',
    name='Mean',
    marker=dict(
        color='black',
        size=20,
        symbol='line-ns-open',
        line=dict(width=2)
    ),
    hovertemplate='%{y}<br>Mean Cover: %{x}%<extra></extra>',
))

# Update Layout
diagnostic_plot.update_layout(
    # title='Cover Range 25th to 75th Percentile',
    xaxis_title='Cover Value (%)',
    yaxis_title='Taxon/Set',
    height=height_diagnostic,
    margin=dict(l=10, r=10, t=80, b=80),
    template='plotly_white',
    showlegend=False,
    font=dict(size=18),
    xaxis=dict(
        showline=True,
        linecolor='black',
        linewidth=1,
        ticks='outside',
        ticklen=6,
        showgrid=True,
        gridcolor='lightgrey'
    ),
    legend=dict(
        yanchor="bottom",
        y=0.02,
        xanchor="right",
        x=0.98,
        bgcolor="rgba(255,255,255,0.8)"
    )
)

# Update layout for margins and dimensions
diagnostic_plot.update_layout(
    margin=dict(t=0, l=0, r=0, b=0),
    autosize=True,
    width=None,
    height=height_diagnostic
)

# Export to HTML (interactive) and PNG (publication)
diagnostic_output = os.path.join(plot_folder, unit_code + '_DiagnosticSets.html')
diagnostic_plot.write_html(diagnostic_output, config={'responsive': True})

#### PROCESS SPECIES COMPOSITION
####____________________________________________________

# Calculate vascular constancy
constancy_vascular = (vascular_data['name_accepted']
                      .value_counts()
                      .to_frame()
                      .rename(columns={'count': 'occurrences'}))
constancy_vascular['constancy'] = (constancy_vascular['occurrences']
                                   / len(vascular_data['site_visit_code'].unique())) * 100

# Calculate bryophyte constancy
constancy_bryophyte = (bryophyte_data['name_accepted']
                       .value_counts()
                       .to_frame()
                       .rename(columns={'count': 'occurrences'}))
constancy_bryophyte['constancy'] = (constancy_bryophyte['occurrences']
                                    / len(bryophyte_data['site_visit_code'].unique())) * 100

# Calculate lichen constancy
constancy_lichen = (lichen_data['name_accepted']
                    .value_counts()
                    .to_frame()
                    .rename(columns={'count': 'occurrences'}))
constancy_lichen['constancy'] = (constancy_lichen['occurrences']
                                 / len(lichen_data['site_visit_code'].unique())) * 100

# Concatenate constancy tables
constancy_composition = pd.concat([constancy_vascular.reset_index(),
                                   constancy_bryophyte.reset_index(),
                                   constancy_lichen.reset_index()], axis=0)

# Calculate vascular cover statistics
cover_vascular = (vascular_data
                  # Calculate pivot table to sum cover while filling zeros
                  .pivot_table(index='site_visit_code',
                               columns='name_accepted',
                               values='cover_percent',
                               aggfunc='sum',
                               fill_value=0)
                  .agg(['mean',
                        'std',
                        'median',
                        'min',
                        'max',
                        percentile_10,
                        percentile_25,
                        percentile_75,
                        percentile_90])
                  .transpose()
                  )

# Calculate bryophyte cover statistics
cover_bryophyte = (bryophyte_data
                   # Calculate pivot table to sum cover while filling zeros
                   .pivot_table(index='site_visit_code',
                                columns='name_accepted',
                                values='cover_percent',
                                aggfunc='sum',
                                fill_value=0)
                   .agg(['mean',
                         'std',
                         'median',
                         'min',
                         'max',
                         percentile_10,
                         percentile_25,
                         percentile_75,
                         percentile_90])
                   .transpose()
                   )

# Calculate lichen cover statistics
cover_lichen = (lichen_data
                # Calculate pivot table to sum cover while filling zeros
                .pivot_table(index='site_visit_code',
                             columns='name_accepted',
                             values='cover_percent',
                             aggfunc='sum',
                             fill_value=0)
                .agg(['mean',
                      'std',
                      'median',
                      'min',
                      'max',
                      percentile_10,
                      percentile_25,
                      percentile_75,
                      percentile_90])
                .transpose()
                )

# Concatenate cover tables
cover_composition = pd.concat([cover_vascular, cover_bryophyte, cover_lichen], axis=0)

# Join statistics for species composition
stats_composition = (pd.merge(left=constancy_composition,
                              right=cover_composition,
                              on='name_accepted',
                              how='left')
                     .round(1)
                     .rename(columns={'percentile_10': '10th percentile',
                                      'percentile_25': '25th percentile',
                                      'percentile_75': '75th percentile',
                                      'percentile_90': '90th percentile'}))

# Filter floristic data for constancy and mean cover limits
stats_composition = stats_composition[(stats_composition['75th percentile'] >= 1)
                                      & (((stats_composition['constancy'] >= 25)
                                          & (stats_composition['mean'] >= 2))
                                         | ((stats_composition['constancy'] >= 50)
                                            & (stats_composition['mean'] >= 1)))]
stats_composition = stats_composition.sort_values(by='mean', ascending=True)

# Create composition display table
table_composition = (stats_composition[
                         ['name_accepted', 'constancy', 'mean', 'std',
                          '10th percentile', '90th percentile']
                     ].sort_values(by='mean', ascending=False)
                     .rename(columns={'name_accepted': 'Taxon (Accepted Name)',
                                      'constancy': 'Constancy (%)',
                                      'mean': 'Mean (Cover %)',
                                      'std': 'Std. Dev. (Cover %)',
                                      '10th percentile': '10th Percentile (Cover %)',
                                      '90th percentile': '90th Percentile (Cover %)'}))

# Calculate range
stats_composition['range_width'] = stats_composition['75th percentile'] - stats_composition['25th percentile']

# Append taxon habit
stats_composition = pd.merge(left=stats_composition,
                             right=taxa_data,
                             left_on='name_accepted',
                             right_on='taxon_name',
                             how='left')
stats_composition['taxon_habit'] = (stats_composition['taxon_habit']
                                    .str.title()
                                    .replace('Spore-Bearing', 'Spore-bearing'))
stats_composition['taxon_habit'] = np.where(stats_composition['name_accepted'] == 'moss', 'Moss',
                                            stats_composition['taxon_habit'])

# Assign bar colors
bar_colors = stats_composition['taxon_habit'].map(structure_colors)

# Create custom data array
custom_data = np.stack([stats_composition['taxon_habit'], stats_composition['75th percentile']], axis=-1)

# Calculate plot height
height_composition = 50 * len(stats_composition)

# Create floristic composition range plot
composition_plot = go.Figure()
composition_plot.add_trace(go.Bar(
    y=stats_composition['name_accepted'],
    x=stats_composition['range_width'],
    base=stats_composition['25th percentile'],
    orientation='h',
    width=0.4,
    name='25th-75th Range',
    marker=dict(
        color=bar_colors,
        line=dict(width=0)
    ),
    customdata=custom_data,
    hovertemplate='%{y}<br>Habit: %{customdata[0]}<br>25th Percentile: %{base}%<br>75th Percentile: %{customdata[1]}%<extra></extra>',
    # Remove legend
    showlegend=False
))

# Add scatterplot for means
composition_plot.add_trace(go.Scatter(
    y=stats_composition['name_accepted'],
    x=stats_composition['mean'],
    mode='markers',
    name='Mean',
    marker=dict(
        color='black',
        size=20,
        symbol='line-ns-open',
        line=dict(width=2)
    ),
    hovertemplate='%{y}<br>Mean Cover: %{x}%<extra></extra>',
))

# Identify taxon habits
taxon_habits = stats_composition['taxon_habit'].unique()
for habit in taxon_habits:
    color = structure_colors.get(habit)
    # Add an empty bar trace for each habit to generate a legend entry
    composition_plot.add_trace(go.Bar(
        x=[None], y=[None],
        name=habit,
        marker_color=color,
        marker_line_width=0
    ))

# Update Layout
composition_plot.update_layout(
    # title='Cover Range 25th to 75th Percentile',
    xaxis_title='Cover Value (%)',
    yaxis_title='Taxon',
    height=height_composition,
    margin=dict(l=10, r=10, t=80, b=80),
    template='plotly_white',
    showlegend=True,
    font=dict(size=18),
    xaxis=dict(
        showline=True,
        linecolor='black',
        linewidth=1,
        ticks='outside',
        ticklen=6,
        showgrid=True,
        gridcolor='lightgrey'
    ),
    legend=dict(
        yanchor="bottom",
        y=0.02,
        xanchor="right",
        x=0.98,
        bgcolor="rgba(255,255,255,0.8)"
    )
)

# Update layout for margins and dimensions
composition_plot.update_layout(
    margin=dict(t=0, l=0, r=0, b=0),
    autosize=True,
    width=None,
    height=height_composition
)

# Export to HTML (interactive) and PNG (publication)
composition_output = os.path.join(plot_folder, unit_code + '_SpeciesComposition.html')
composition_plot.write_html(composition_output, config={'responsive': True})

#### PROCESS ENVIRONMENT DATA
####____________________________________________________

# Calculate physiography
physiography_data = environment_data['physiography'].dropna().to_frame()
physiography_frequency = physiography_data['physiography'].value_counts().to_frame().reset_index()
physiography_frequency['frequency'] = (physiography_frequency['count'] / len(physiography_data)) * 100
physiography_frequency = physiography_frequency[physiography_frequency['frequency'] >= 10]
physiography_list = physiography_frequency['physiography'].unique()
physiography_text = ''
for x in physiography_list:
    physiography_text = physiography_text + x + '; '
physiography_text = physiography_text[:-2]

# Calculate geomorphology
geomorph_data = environment_data['geomorphology'].dropna().to_frame()
geomorph_frequency = geomorph_data['geomorphology'].value_counts().to_frame().reset_index()
geomorph_frequency['frequency'] = (geomorph_frequency['count'] / len(geomorph_data)) * 100
geomorph_frequency = geomorph_frequency[geomorph_frequency['frequency'] >= 10]
geomorph_list = geomorph_frequency['geomorphology'].unique()
geomorph_text = ''
for x in geomorph_list:
    geomorph_text = geomorph_text + x + '; '
geomorph_text = geomorph_text[:-2]

# Calculate macrotopography
macrotopo_data = environment_data['macrotopography'].dropna().to_frame()
macrotopo_frequency = macrotopo_data['macrotopography'].value_counts().to_frame().reset_index()
macrotopo_frequency['frequency'] = (macrotopo_frequency['count'] / len(macrotopo_data)) * 100
macrotopo_frequency = macrotopo_frequency[macrotopo_frequency['frequency'] >= 10]
macrotopo_list = macrotopo_frequency['macrotopography'].unique()
macrotopo_text = ''
for x in macrotopo_list:
    macrotopo_text = macrotopo_text + x + '; '
macrotopo_text = macrotopo_text[:-2]

# Calculate microtopography
microtopo_data = environment_data['microtopography'].dropna().to_frame()
microtopo_frequency = microtopo_data['microtopography'].value_counts().to_frame().reset_index()
microtopo_frequency['frequency'] = (microtopo_frequency['count'] / len(microtopo_data)) * 100
microtopo_frequency = microtopo_frequency[microtopo_frequency['frequency'] >= 10]
microtopo_list = microtopo_frequency['microtopography'].unique()
microtopo_text = ''
for x in microtopo_list:
    microtopo_text = microtopo_text + x + '; '
microtopo_text = microtopo_text[:-2]

# Calculate moisture regime
moisture_data = environment_data['moisture_regime'].dropna().to_frame()
moisture_frequency = moisture_data['moisture_regime'].value_counts().to_frame().reset_index()
moisture_frequency['frequency'] = (moisture_frequency['count'] / len(moisture_data)) * 100
moisture_frequency = moisture_frequency[moisture_frequency['frequency'] >= 20]
moisture_list = moisture_frequency['moisture_regime'].unique()
moisture_text = ''
for x in moisture_list:
    moisture_text = moisture_text + x + '; '
moisture_text = moisture_text[:-2]

# Calculate restrictive layer
restrict_data = environment_data['restrictive_type'].dropna().to_frame()
restrict_frequency = restrict_data['restrictive_type'].value_counts().to_frame().reset_index()
restrict_frequency['frequency'] = (restrict_frequency['count'] / len(restrict_data)) * 100
restrict_frequency = restrict_frequency[restrict_frequency['frequency'] >= 20]
restrict_list = restrict_frequency['restrictive_type'].unique()
restrict_text = ''
for x in restrict_list:
    restrict_text = restrict_text + x + '; '
restrict_text = restrict_text[:-2]

# Calculate surface water
surfacewater_data = environment_data['surface_water'].dropna().to_frame()
surfacewater_frequency = surfacewater_data['surface_water'].value_counts().to_frame()
surfacewater_frequency['frequency'] = (surfacewater_frequency['count'] / len(surfacewater_data)) * 100
surfacewater_frequency = surfacewater_frequency[surfacewater_frequency['frequency'] >= 20]
surfacewater_frequency = str(round(surfacewater_frequency.at[True, 'frequency'], 1)) + '%'

# Calculate elevation
elevation_data = site_visit_data[['site_visit_code', 'elevation_m']].dropna()
elevation_data['elevation_m'] = pd.to_numeric(elevation_data['elevation_m'])
elevation_data = elevation_data[elevation_data['elevation_m'] != -32768]
elevation_data = (elevation_data['elevation_m']
                  .agg(['mean',
                        'std',
                        'median',
                        'min',
                        'max',
                        percentile_10,
                        percentile_25,
                        percentile_75,
                        percentile_90])
                  .to_frame()
                  .transpose())

# Calculate slope
slope_data = site_visit_data[['site_visit_code', 'slope_deg']].dropna()
slope_data['slope_deg'] = pd.to_numeric(slope_data['slope_deg'])
slope_data = slope_data[slope_data['slope_deg'] != -32768]
slope_data = (slope_data['slope_deg']
              .agg(['mean',
                    'std',
                    'median',
                    'min',
                    'max',
                    percentile_10,
                    percentile_25,
                    percentile_75,
                    percentile_90])
              .to_frame()
              .transpose())

# Calculate water depth
waterdepth_data = environment_data[['site_visit_code', 'depth_water_cm']].dropna()
waterdepth_data['depth_water_cm'] = pd.to_numeric(waterdepth_data['depth_water_cm'])
waterdepth_data = waterdepth_data[waterdepth_data['depth_water_cm'] != -999]
waterdepth_data = (waterdepth_data['depth_water_cm']
                   .agg(['mean',
                         'std',
                         'median',
                         'min',
                         'max',
                         percentile_10,
                         percentile_25,
                         percentile_75,
                         percentile_90])
                   .to_frame()
                   .transpose())

# Calculate moss duff depth
mossduff_data = environment_data['depth_moss_duff_cm'].dropna().to_frame()
mossduff_data['depth_moss_duff_cm'] = pd.to_numeric(mossduff_data['depth_moss_duff_cm'])
mossduff_data = mossduff_data[mossduff_data['depth_moss_duff_cm'] != -999]
mossduff_data = (mossduff_data['depth_moss_duff_cm']
                 .agg(['mean',
                       'std',
                       'median',
                       'min',
                       'max',
                       percentile_10,
                       percentile_25,
                       percentile_75,
                       percentile_90])
                 .to_frame()
                 .transpose())

# Calculate restrictive layer depth
restictdepth_data = environment_data['depth_restrictive_layer_cm'].dropna().to_frame()
restictdepth_data['depth_restrictive_layer_cm'] = pd.to_numeric(
    restictdepth_data['depth_restrictive_layer_cm']
)
restictdepth_data = restictdepth_data[restictdepth_data['depth_restrictive_layer_cm'] != -999]
restictdepth_data = (restictdepth_data['depth_restrictive_layer_cm']
                     .agg(['mean',
                           'std',
                           'median',
                           'min',
                           'max',
                           percentile_10,
                           percentile_25,
                           percentile_75,
                           percentile_90])
                     .to_frame()
                     .transpose())

# Calculate pH
pH_data = soilmetrics_data['ph'].dropna().to_frame()
pH_data['ph'] = pd.to_numeric(pH_data['ph'])
pH_data = pH_data[pH_data['ph'] != -999]
pH_data = (pH_data['ph']
           .agg(['mean',
                 'std',
                 'median',
                 'min',
                 'max',
                 percentile_10,
                 percentile_25,
                 percentile_75,
                 percentile_90])
           .to_frame()
           .transpose())

# Calculate conductivity
conductivity_data = soilmetrics_data['conductivity_mus'].dropna().to_frame()
conductivity_data['conductivity_mus'] = pd.to_numeric(conductivity_data['conductivity_mus'])
conductivity_data = conductivity_data[conductivity_data['conductivity_mus'] != -999]
conductivity_data = (conductivity_data['conductivity_mus']
                     .agg(['mean',
                           'std',
                           'median',
                           'min',
                           'max',
                           percentile_10,
                           percentile_25,
                           percentile_75,
                           percentile_90])
                     .to_frame()
                     .transpose())

# Concatenate quantitative metrics
stats_environment = (pd.concat([elevation_data,
                               slope_data,
                               waterdepth_data,
                               mossduff_data,
                               restictdepth_data,
                               pH_data,
                               conductivity_data], axis=0)
                     .reset_index()
                     .rename(columns={'index': 'Characteristic',
                                      'mean': 'Mean',
                                      'percentile_10': '10th Percentile',
                                      'percentile_90': '90th Percentile'}))

# Create environment display table
environment_mapping = {
    'elevation_m': 'Elevation (m)',
    'slope_deg': 'Slope (°)',
    'depth_water_cm': 'Depth Water (cm)ǂ',
    'depth_moss_duff_cm': 'Depth Moss/Duff (cm)',
    'depth_restrictive_layer_cm': 'Depth Restrictive Layer (cm)',
    'ph': 'pH',
    'conductivity_mus': 'Conductivity (mus)'
}
table_environment = (stats_environment[
    ['Characteristic', 'Mean', '10th Percentile', '90th Percentile']
]
                     .copy()
                     .round(1))
table_environment['Characteristic'] = table_environment['Characteristic'].replace(environment_mapping)

#### COMPILE HTML OUTPUT
####____________________________________________________

# Define html output
html_output = os.path.join(output_folder, unit_code + '.html')

# Format photo html
photo_html = ''.join([
    f'<a href="{url}"><img src="{url}" width="200" alt="Photo" style="margin: 5px; display: inline-block; vertical-align: top;"></a>'
    for url in photo_list
])
photo_html = '<p><b>Photos (Click Images to Enlarge):</b></p>' + photo_html

# Define iframe html
url_precursor = 'https://accs.uaa.alaska.edu/files/map-classes/plots/'
structure_iframe = f'''<iframe 
    src="{url_precursor + os.path.split(structure_output)[1]}" 
    width="100%" 
    height="400" 
    frameborder="0" 
    scrolling="no" 
    style="border: none; display: block; overflow: hidden;">
</iframe>'''
diagnostic_iframe = f'''<iframe 
    src="{url_precursor + os.path.split(diagnostic_output)[1]}" 
    width="100%" 
    height="{height_diagnostic + 10}" 
    frameborder="0" 
    scrolling="no" 
    style="border: none; display: block; overflow: hidden;">
</iframe>'''
composition_iframe = f'''<iframe 
    src="{url_precursor + os.path.split(composition_output)[1]}" 
    width="100%" 
    height="{height_composition + 10}" 
    frameborder="0" 
    scrolling="no" 
    style="border: none; display: block; overflow: hidden;">
</iframe>'''

# Define Replacements
title_replace = f'**Unit Name:** {unit_name}'
photo_replace = f'**Photos:** {photo_text}'
replacements = {
    '# Description Data Entry': f'# {unit_name}',
    title_replace: '',
    '[unit_name]': unit_name,
    '[level]': level_text.lower(),
    photo_replace: photo_html,
    '[table_structure]': table_structure.to_html(
        classes='table table-bordered', index=False, border=0
    ),
    '[structure_plot]': structure_iframe,
    '[diagnostic_plot]': diagnostic_iframe,
    '[table_composition]': table_composition.to_html(
        classes='table table-bordered', index=False, border=0
    ),
    '[composition_plot]': composition_iframe,
    '[physiography_text]': physiography_text,
    '[geomorph_text]': geomorph_text,
    '[macrotopo_text]': macrotopo_text,
    '[microtopo_text]': microtopo_text,
    '[moisture_text]': moisture_text,
    '[restrict_text]': restrict_text,
    '[surfacewater_frequency]': surfacewater_frequency,
    '[table_environment]': table_environment.to_html(
        classes='table table-bordered', index=False, border=0
    )
}

# Process markdown file to html
with open(text_input, 'r', encoding='utf-8') as input_file:
    md_content = input_file.read()

# Replace text placeholders with html
for key, value in replacements.items():
    md_content = md_content.replace(key, str(value))

# Render tables
html_content = markdown.markdown(md_content, extensions=['tables', 'toc'])

# Define styles
rmarkdown_style = """
<style>
    body {
        font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
        font-size: 16px;
        line-height: 1.6;
        color: #333;
        background-color: #fff;
        margin: 0;
        padding: 0;
    }

    /* Layout Wrapper */
    .wrapper {
        display: flex;
        max-width: 1200px;
        margin: 0 auto;
    }

    /* Sidebar Navigation (TOC) */
    #TOC {
        width: 250px;
        position: fixed;
        top: 0;
        left: 0;
        bottom: 0;
        overflow-y: auto;
        padding: 40px 20px;
        background-color: #f8f8f8;
        border-right: 1px solid #e7e7e7;
        font-size: 0.9em;
    }
    #TOC ul {
        list-style: none;
        padding-left: 0;
        margin: 0;
    }
    #TOC ul ul {
        padding-left: 20px; /* Indent nested levels */
    }
    #TOC li {
        margin-bottom: 8px;
    }
    #TOC a {
        color: #333;
        text-decoration: none;
        display: block;
        padding: 6px 10px;
        border-radius: 4px;
        transition: background-color 0.1s;
    }
    #TOC a:hover {
        color: #337ab7;
        background-color: #eee;
    }

    /* Main Content */
    .main-content {
        margin-left: 270px; /* Sidebar width + gap */
        padding: 40px 40px;
        max-width: 850px;
        flex: 1;
    }

    /* Typography */
    h1, h2, h3 {
        color: #333;
        font-weight: 600;
        margin-bottom: 0.5em;
        scroll-margin-top: 20px; /* Offset for anchor links */
    }
    h1 { font-size: 2.2em; border-bottom: 1px solid #eee; padding-bottom: 10px; }
    h2 { font-size: 1.6em; border-bottom: 1px solid #eee; padding-bottom: 5px; }
    h3 { font-size: 1.3em; }

    /* Tables */
    table {
        width: 100%;
        margin-bottom: 20px;
        border-collapse: collapse;
        font-size: 0.9em;
    }
    th, td { padding: 8px 12px; text-align: left; border-top: 1px solid #ddd; }
    th { font-weight: bold; border-bottom: 2px solid #ddd; }
    tr:hover {
        background-color: #e6f7ff;
    }

    /* Images */
    img {
        max-width: 100%;
        display: block; /* Default block, inline-block handled inline */
        margin: 20px auto;
        box-shadow: 0 0 5px rgba(0,0,0,0.1);
    }

    /* Links */
    .main-content a { color: #337ab7; text-decoration: none; }
    .main-content a:hover { text-decoration: underline; }

    /* Mobile Responsive */
    @media (max-width: 768px) {
        #TOC {
            position: relative;
            width: 100%;
            height: auto;
            border-right: none;
            border-bottom: 1px solid #e7e7e7;
        }
        .main-content {
            margin-left: 0;
            padding: 20px;
        }
        .wrapper { display: block; }
    }
</style>
"""

# JavaScript to auto-generate TOC
toc_script = """
<script>
document.addEventListener("DOMContentLoaded", function() {
    var toc = document.getElementById('TOC');
    var content = document.querySelector('.main-content');

    // UPDATED: Only select h2 and h3
    var headers = content.querySelectorAll('h2, h3');
    var tocList = document.createElement('ul');

    if (headers.length > 0) {
        var currentLevel = 1; 
        var currentList = tocList;
        var listStack = [tocList]; 

        headers.forEach(function(header, index) {
            if (!header.id) {
                header.id = 'header-' + index;
            }

            // UPDATED: Normalize levels. 
            // h2 (level 2) becomes 1. h3 (level 3) becomes 2.
            var level = parseInt(header.tagName.substring(1)) - 1;

            // Adjust nesting
            if (level > currentLevel) {
                while (level > currentLevel) {
                    var newList = document.createElement('ul');
                    if (currentList.lastElementChild) {
                        currentList.lastElementChild.appendChild(newList);
                    } else {
                        var li = document.createElement('li');
                        currentList.appendChild(li);
                        li.appendChild(newList);
                    }
                    currentList = newList;
                    listStack.push(currentList);
                    currentLevel++;
                }
            } else if (level < currentLevel) {
                while (level < currentLevel) {
                    listStack.pop();
                    currentList = listStack[listStack.length - 1];
                    currentLevel--;
                }
            }

            var li = document.createElement('li');
            var a = document.createElement('a');
            a.href = '#' + header.id;
            a.textContent = header.textContent;
            li.appendChild(a);
            currentList.appendChild(li);
        });

        toc.appendChild(tocList);
    }
});
</script>
"""

# Create html text string
final_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{unit_name}</title>
    {rmarkdown_style}
</head>
<body>
    <div class="wrapper">
        <div id="TOC">
            </div>
        <div class="main-content">
            {html_content}
        </div>
    </div>
    {toc_script}
</body>
</html>
"""

# Export html file
with open(html_output, 'w', encoding='utf-8') as output_file:
    output_file.write(final_html)
