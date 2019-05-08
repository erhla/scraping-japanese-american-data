# -*- coding: utf-8 -*-
"""
Created on Tue May  7 23:28:31 2019

@author: erhla
"""
import pandas as pd
import recordlinkage

far = pd.read_csv('far_cleanup.csv')
wra = pd.read_csv('wra_cleanup.csv')


indexer = recordlinkage.index.SortedNeighbourhood(left_on='m_lastname',
                                                 right_on='last_name_corrected')
candidate_links = indexer.index(wra, far)

compare = recordlinkage.Compare()


compare.numeric('m_birthyear', 'year_of_birth')
compare.string('m_familyno', 'family_number', method='levenshtein')
compare.string('m_firstname', 'first_name_corrected', method='jarowinkler')
