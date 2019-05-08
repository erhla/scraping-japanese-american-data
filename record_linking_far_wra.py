# -*- coding: utf-8 -*-
"""
Created on Tue May  7 23:28:31 2019

@author: erhla
"""
import pandas as pd
import recordlinkage

far = pd.read_csv('far_cleanup.csv', usecols=['far', 'family_number',
       'last_name_corrected', 'first_name_corrected', 'date_of_birth', 'year_of_birth',
       'sex', 'marital_status', 'citizenship', 'type_of_original_entry', 'pre-evacuation_address',
       'pre-evacuation_state', 'date_of_original_entry', 'type_of_final_departure', 
       'date_of_final_departure', 'final_departure_state'])

cols_to_datetime = ['date_of_birth', 'date_of_final_departure', 'date_of_original_entry']

for col in cols_to_datetime:
    far[col] = pd.to_datetime(far[col], errors='coerce')

far['age_at_departure'] = far['date_of_final_departure'] - far['date_of_birth']
far['time_incarcerated'] = far['date_of_final_departure'] - far['date_of_original_entry']

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
  
    
wra['m_birthyear'] = wra['m_birthyear'].astype('str')
far['year_of_birth'] = far['year_of_birth'].astype('str')

cols_to_lowercase = [('m_lastname', 'last_name_corrected'), ('m_firstname', 'first_name_corrected')]
for wra_col, far_col in cols_to_lowercase:
    wra[wra_col] = wra[wra_col].str.lower()
    far[far_col] = far[far_col].str.lower()

indexer = recordlinkage.Index()
indexer.add(recordlinkage.index.Block(left_on='m_familyno', right_on='family_number'))
#indexer.add(recordlinkage.index.Block(left_on='m_gender', right_on='sex'))
#indexer.add(recordlinkage.index.Block(left_on='m_originalstate', right_on='pre-evacuation_state'))
#indexer.add(recordlinkage.index.SortedNeighbourhood(left_on='m_birthyear', right_on='year_of_birth'))

#recordlinkage.index.SortedNeighbourhood(left_on='m_familyno', right_on='family_number', window=3)
candidate_links = indexer.index(wra, far)

compare = recordlinkage.Compare()

compare.string('m_birthyear', 'year_of_birth', method='jarowinkler')
compare.string('m_lastname', 'last_name_corrected', method='levenshtein')
compare.string('m_firstname', 'first_name_corrected', method='jarowinkler')
#compare.string('m_familyno', 'family_number', method='levenshtein')
compare.exact('m_gender', 'sex')
compare.string('m_originalstate', 'pre-evacuation_state', method='levenshtein')

tst = compare.compute(candidate_links, wra, far)
tst['score'] = tst[0] * tst[1] * tst[2] * tst[3] * tst[4]

#predicted links
tst[tst['score'] > 0.90]