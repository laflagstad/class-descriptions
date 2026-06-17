# Description Data Entry Template

**Instructions:** After entering data, delete this instruction section. *Only replace text that is shown in Italics in this data entry template.* Once you replace the italicized text, remove the italics (except for taxon names). Do not modify any bracketed text, such as [bracketed_text]. Bracketed text will be replaced by data summaries from the AKVEG Database. Do not modify plain text, which is standard language for all descriptions. Alliance descriptions will follow a similar format but use a different repository in the AKNVC project.
•	Alliances are defined as a vegetation classification unit containing one or more associations, and defined by a characteristic range of species composition, habitat conditions, physiognomy, and diagnostic species, typically at least one of which is found in the uppermost or dominant stratum of the vegetation.
•	This guidance is meant to prompt consistent description. As the ecology of types differs, so will the order and emphasis of the information provided. The end goal is a consistent presentation of information using standardized terminology that does not sacrifice a natural flow and clarity of language.
•	For all sections, try to use terminology accepted by AKVEG to the extent possible. This is especially important for discussions of physiography, geomorphology, macro and micro topography, moisture regime, and drainage. 

## Overview

**Unit Name:** *Enter map class name.*

**Level:** Map Class

**Code:** *Enter map class code (i.e., raster value in map and code in AKVEG schema).*

**Concept:** This [level] *Provide a succinct overview of the type that addresses the vegetation structure, floristics, and environment. The text should present:  
•	structural class(es)
•	the characteristic range of species composition (dominant and indicator species)
•	vegetation pattern (semi, dis, or continuous) and extent (small, large, linear, marginal)
•	an evaluation of rarity on landscape (i.e., rare, uncommon, common, ubiquitous)
•	habitat conditions, which may include descriptors of: soils, moisture regime, associated landforms, or limiting physiology, for example: coastal, freshwater wetland, alpine, floodplain
Example text:
This map class encompasses low shrubs and bunchgrasses indicated by the sagebrush Artemisia frigida and combinations of the bunch grasses Calamagrostis purpurascens, Bromus pumpellianus, and Festuca altaica. This uncommon type develops as discontinuous patches in well-drained mineral soils across south-facing, rocky slopes; it is associated with river bluffs in the boreal and pingos in the Arctic.*  

**Photos:** *Enter a comma separated list of three to five representative photos. Use the photo file path or server url.*

## Placement in AKNVC Hierarchy

**Macrogroup Code:** *Enter the macrogroup code (starting with "M").*

**Macrogroup:** *Enter the macrogroup name.*

**Group Code:** *Enter the group code (starting with "G").*

**Group:** *Enter the group name.*

## Vegetation

### Structure

**Structural Description:** This [level] *Provide a paragraph addressing the typical structure of the vegetation. Avoid duplicating information provided in other sections. The text should present:  
•	Dominant life forms presented in order of strata or structural dominance
•	Non-dominant, associated life forms
•	How life forms are related to the environment, if relevant. For example: tree form (full stature, dwarf, krummholz) shrub form (tall, low, dwarf, prostrate), root morphology (rhizomes, stolons, tussocks), herb form (high or low stature or erect, cushion, creeping); lichen category (arboreal, foliose, fruticose, crustose); moss category (feather or turf, acrocarpous or pleurocarpous mosses)
•	If informative, a statement on the presence or absence of woody and non-vascular species, and/or tussocks
•	if vegetation is sparse, discuss the dominant abiotic ground cover(s)
Example text:
This map class is characterized by low shrubs, bunchgrasses, and dry-site lichens; a diversity of forbs and turf mosses are associated at low abundance. While bare soil is characteristic of developing steppe, biotic soil crust is an important ground cover in mature sites with stable substrates. Mixed coniferous-deciduous woodlands may develop at the periphery.*

**Structural Class:** *Enter one or more structural classes from the AKVEG Data Dictionary*

Table 1. Mean and range for structural characteristics for [unit_name].

[table_structure]

[structure_plot]

Figure 1. Plot of structural group proportions for [unit_name].

### Floristics

**Floristics Description:** This [level] *Provide a paragraph discussing plant species composition with emphasis on diagnostic taxa. The text should expand on the floristics of each dominant life form mentioned in the Structural Description and provide context by discussing adaptations to the environment. Avoid duplicating information provided in other sections. The text should present:  
•	Dominant, indicator (a combination of frequency and abundance), differential (species that separates the alliance from other alliances), and character (a general term to be uses when not able to provide a more specific term such as dominant, indicator, or differential) species by strata or structural dominance. Within strata species should be listed in decreasing order of importance (i.e., fidelity) if known. 
•	Life cycles of diagnostic plants (annual or perennial, deciduous or evergreen) if relevant
•	Species adaptations related to reproduction, desiccation, inundation, cold, salinity, as appropriate.
•	an evaluation of the overall diversity of the type (e.g., diverse assemblage or monoculture)
Example text:
This map class is indicated by combinations of the low and dwarf shrubs Artemisia frigida, Amelanchier alnifolia, Elaeagnus commutata, Shepherdia canadensis, Juniperus communis, and Arctostaphylos uva-ursi; the grasses Calamagrostis purpurascens, Bromus pumpellianus, Festuca altaica, and Poa glauca; and the forbs Artemisia arctica, Artemisia alaskana, Bupleurum americanum, and Saxifraga tricuspidata. Woodland associations co-dominated by Populus tremuloides and Picea glauca may occur peripherally. Vascular plant cover is often sparse with bare soil, biotic soil crust, or lichen occupying the interstices. Foliose lichens are represented by species in the Dermatocarpon, Diploschistes, Endocarpon, Fulgensia, Psora, Toninia, and Xanthoparmelia genera. Dry site mosses such as Rhytidium rugosum and Tortula ruralis may co-occur.  Predominance of cyanobacteria in the Collema genus suggests that biotic soil crusts make important contributions to the nitrogen budget of steppe ecosystems. Steppe bluffs support a disproportionately high diversity and abundance of rare plant taxa including critically imperiled Botrychium campestre var. lineare, Cryptantha shackletteana, Orobanche fasciculata, and Townsendia hookeri.*

[diagnostic_plot]

Figure 2. Plot of range from 10th percentile to 90th percentile and mean for diagnostic species (and species sets) occurring in [unit_name]. Diagnostic species (sets) are included if they have constancy >= 25% and mean cover >= 2% or constancy >= 50% and mean cover >= 1%.

Table 2. Constancy and cover table for individual taxa with constancy >= 25% and mean cover >= 2% or constancy >= 50% and mean cover >= 1% occurring in [unit_name].

[table_composition]

[composition_plot]

Figure 3. Plot of range from 25th percentile to 75th percentile and mean for individual taxa occurring in [unit_name]. Individual taxa are included if they have constancy >= 25% and mean cover >= 2% or constancy >= 50% and mean cover >= 1%.

## Dynamics

**Dynamics Description:** *Provide a paragraph discussing disturbance, succession, and threats. Present disturbances in decreasing order of severity (combination of scale, duration, and intensity) and address disturbance in terms of scale, duration, and intensity. Address the vegetation types preceding and proceeding this type along a pathway of natural succession. Address threats where appropriate, discuss in terms of short and long-term, natural and anthropogenic. Let’s not shy away from including climate change as a short term, anthropogenic threat as well as a long-term natural process. 
Example text:
Large-scale disturbances affecting steppe bluffs include fire and mass wasting; smaller-scale disturbances include burrowing or grazing by rodents and ungulates. Fire and landslides are thought to favor development of this type by removing competitive forest taxa and exposing mineral soil for colonization by seedlings, thereby altering the competitive balance in favor of faster growing, more readily dispersed plants. Steppe associations depend on disturbance to persist and are thought to be seral to Populus tremuloides woodlands. Where there is sufficient moisture, Betula neoalaskana and Picea glauca are able to colonize the Populus tremuloides woodland with a dry Picea glauca forest eventually establishing. Following fire, Populus tremuloides woodlands may revert to steppe associations. As one of the warmest and driest microclimates in the boreal and Arctic, this type is susceptible to invasion by nonnative ruderal species introduced from more temperate climates.*

## Range

**Range Description:** *Provide a paragraph describing the geographic range of the type. Use standard terms, prioritizing the AKVEG bioclimatic zones (Arctic, Boreal, Northern Subpolar Oceanic, Temperate) and vegetation regions (Alaska-Yukon Central, Arctic Western, Alaska Southwest, Arctic Northern, Aleutian-Kamchatka, Alaska-Yukon Southern, Alaska Pacific, Alaska-Yukon Northern, Alaska Western, North Pacific) but using ecoregions or other geographic terms where more specificity is helpful. Do not attempt to provide a level of detail redundant with the vegetation map.
Example text:
Steppe vegetation occurs in the Arctic and Boreal bioclimatic zones. The northernmost occurrence of steppe in North America is the Arctic Coastal Plain; the Anderson River steppe in Canada’s Northwest Territory is the easternmost known occurrence of steppe in North America.*

**Rarity on Landscape:** *Enter one of the following: Ubiquitous; Common; Uncommon; Rare*

## Environment

**Environment Description**: *This paragraph should summarize the regional climate that control the distribution of the type and local environmental gradients variation within the type. Avoid duplicating information provided in other sections. Try to expand on the following as appropriate:
•	physiography, geomorphology, macro and microtopography, elevation range
•	soils, pH, salinity, presence of permafrost
•	moisture regime and drainage, with specific information on frequency and duration of inundation for types influenced by tidal and riverine flooding
Example text:
This type is associated with river bluffs fronting large braided systems in the boreal and the south-facing slopes and summits of pingos in the Arctic. Steppe vegetation develops on steep slopes (inclination 30-46°), oriented to the south (aspect 121-225°) at relatively low elevation (244 to 914 m). Soils are well-drained, silty loams to loams with low organic matter content. Permafrost is typically absent due to warm soil temperatures in the summer and poor insulation in the winter. Soil pH ranges from 6.2 to 8.0 with a mean of 7.0 and is often elevated by input of calcium carbonate-rich loess. Moisture of steppe soils is strongly limited by exposure to wind, low accumulation and residence of snow, drainage across steep slopes, and high soil evaporation and transpiration caused by the slopes’ direct orientation to the low-angled sun.*

**Physiography:** [physiography_text]

**Geomorphology:** [geomorph_text]

**Macrotopography:** [macrotopo_text]

**Microtopography:** [microtopo_text]

**Moisture Regime:** [moisture_text]

**Restrictive Layer:** [restrict_text]

**Percentage of Sites with Surface Water Present:** [surfacewater_frequency]

Table 3. Mean and range for quantitative environmental characteristics for [unit_name].

[table_environment]

ǂ Negative values represent distance to water table from soil surface while positive values represent depth of water above soil surface. Values of zero (0) represent water at the soil surface.

## Metadata

**Map Version**: *Enter the version of the map that this description is current with.*

**Described By:** *Enter the name (First Middle Initial Last) of the original description author(s).*

**Date:** *Enter the date (yyyy-mm-dd) of the original description.*

**Last Revised by:** *Enter the name (First Middle Initial Last) of the latest revision author(s).*

**Date:** *Enter the date (yyyy-mm-dd) of the revision.*

## References

*Enter any references using ESA style.*
