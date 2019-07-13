# -*- coding: utf-8 -*-
"""
Created on Tue May  7 23:28:31 2019

@author: erhla
"""
#cd Documents/GitHub/names-rawdata/processed/
import pandas as pd
import recordlinkage


#reading in dataframes and specific columns
wra = pd.read_csv('wra_cleanup.csv', usecols=['m_camp', 'm_lastname', 'm_firstname',
       'm_birthyear', 'm_gender', 'm_originalstate', 'm_familyno',
       'm_individualno', 'w_assemblycenter', 'w_originaladdress', 'w_birthcountry', 
       'w_fatheroccupus', 'w_fatheroccupabr', 'w_yearsschooljapan', 'w_gradejapan',
       'w_schooldegree', 'w_yearofusarrival', 'w_timeinjapan',
       'w_notimesinjapan', 'w_ageinjapan', 'w_militaryservice',
       'w_maritalstatus', 'w_ethnicity', 'w_birthplace', 'w_citizenshipstatus',
       'w_highestgrade', 'w_language', 'w_religion', 'w_occupqual1',
       'w_occupqual2', 'w_occupqual3', 'w_occuppotn1', 'w_occuppotn2',
       'w_filenumber'])

far = pd.read_csv('far_cleanup.csv', usecols=['far', 'family_number',
       'last_name_corrected', 'first_name_corrected', 'date_of_birth', 'year_of_birth',
       'sex', 'marital_status', 'citizenship', 'type_of_original_entry', 'pre-evacuation_address',
       'pre-evacuation_state', 'date_of_original_entry', 'type_of_final_departure', 
       'date_of_final_departure', 'final_departure_state'])


#formatting year_of_birth column uniformly
far['year_of_birth'] = far['year_of_birth'].fillna('0')
far['year_of_birth'] = far['year_of_birth'].astype(str)
far.loc[far['year_of_birth'].str.contains('y')] = '0'
far.loc[far['year_of_birth'].str.contains('/')] = '0'
far['year_of_birth'] = far['year_of_birth'].str.slice(0,4)
wra['m_birthyear'] = wra['m_birthyear'].astype('str')

#datetime columns for creating calculated columns
cols_to_datetime = ['date_of_birth', 'date_of_final_departure', 'date_of_original_entry']

for col in cols_to_datetime:
    far[col] = pd.to_datetime(far[col], errors='coerce')

far['age_at_departure'] = far['date_of_final_departure'] - far['date_of_birth']
far['time_incarcerated'] = far['date_of_final_departure'] - far['date_of_original_entry']

#forcing all letters to be lowercase to facilitate string matching
cols_to_lowercase = [('m_lastname', 'last_name_corrected'), ('m_firstname', 'first_name_corrected')]
for wra_col, far_col in cols_to_lowercase:
    wra[wra_col] = wra[wra_col].str.lower()
    far[far_col] = far[far_col].str.lower()

#adding unique_ids
wra['ind_id'] = wra.index.tolist()
far['ind_id'] = far.index.tolist()

#starting record linkage
indexer = recordlinkage.Index()

#blocking on family number
indexer.add(recordlinkage.index.Block(left_on='m_familyno', right_on='family_number'))
candidate_links = indexer.index(wra, far)
compare = recordlinkage.Compare()

#generating similarity scores for birth year, last name, first name, gender, and pre-evacuation state
compare.string('m_birthyear', 'year_of_birth', method='jarowinkler')
compare.string('m_lastname', 'last_name_corrected', method='levenshtein')
compare.string('m_firstname', 'first_name_corrected', method='jarowinkler')
compare.exact('m_gender', 'sex')
compare.string('m_originalstate', 'pre-evacuation_state', method='levenshtein')

#computing links and link score
links = compare.compute(candidate_links, wra, far)
links['score'] = links[0] * links[1] * links[2] * links[3] * links[4]

#keeping the top match for each entry, dropping all matches with below 85% similarity
links = links.reset_index()
matches = links.sort_values('score', ascending=False).drop_duplicates('level_0')
good_matches = matches[matches['score'] > 0.85]

#storing link_id (generated from the index of good_matches)
wra["link_id"] = 0
far["link_id"] = 0
adj_indx = [x + 1000000 for x in good_matches.index.tolist()]
wra.loc[good_matches['level_0'], 'link_id'] = adj_indx
far.loc[good_matches['level_1'], 'link_id'] = adj_indx

#approximately 27k from wra and 69k from far unmatched
far_tiny = far[far['link_id'] == 0]
wra_tiny = wra[wra['link_id'] == 0]

#making camp names the same
far_tiny['far'] = far_tiny.far.str.slice(0, -1)
wra_tiny['m_camp'] = wra_tiny.m_camp.str.slice(2)
wra_tiny.loc[wra_tiny['m_camp'] == 'amache', 'm_camp'] = 'granada'
wra_tiny.loc[wra_tiny['m_camp'] == '-tulelake', 'm_camp'] = 'tulelake'


#'B', 'Birth-Ind.Lv.', 




def group_cnt(df, col_name):
    return df.groupby(col_name).size().sort_values(ascending=False)

        

def check_link(wra_idx, far_idx):
    print(far.iloc[far_idx])
    print(wra.iloc[wra_idx])

def find_record(parameters_dict):
    wra_cur = wra
    far_cur = far
    for key, val in parameters_dict.items():
        if key == "camp":
            wra_cur = wra_cur[wra_cur["m_camp"]]


#indexer.add(recordlinkage.index.Block(left_on='m_gender', right_on='sex'))
#indexer.add(recordlinkage.index.Block(left_on='m_originalstate', right_on='pre-evacuation_state'))
#indexer.add(recordlinkage.index.SortedNeighbourhood(left_on='m_birthyear', right_on='year_of_birth'))