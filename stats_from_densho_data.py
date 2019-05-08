# -*- coding: utf-8 -*-
"""
Created on Tue May  7 21:51:50 2019

@author: erhla
"""

df = pd.read_csv('far_cleanup.csv', usecols=['far', 'family_number',
       'last_name_corrected', 'first_name_corrected', 'date_of_birth', 
       'sex', 'marital_status', 'citizenship', 'type_of_original_entry', 'pre-evacuation_address',
       'pre-evacuation_state', 'date_of_original_entry', 'type_of_final_departure', 
       'date_of_final_departure', 'final_departure_state'])

cols_to_datetime = ['date_of_birth', 'date_of_final_departure', 'date_of_original_entry']

for col in cols_to_datetime:
    df[col] = pd.to_datetime(df[col], errors='coerce')

df['age_at_departure'] = df['date_of_final_departure'] - df['date_of_birth']
df['time_incarcerated'] = df['date_of_final_departure'] - df['date_of_original_entry']

outcomes = {'hospitalized': ['Term-Mental', 'TD-Inst', 'Term-I Hosp', 'Term-I (Hosp)'],
            'repatriated': ['Repat-Grip', 'Ind-Repat', 'Term-RePat', 'Ind-Repat'],
            'jail': ['Ind-Penal'],
            'army': ['Term-AF', 'Ind-AF'],
            'college': ['Ind-Educ'],
            'segregated': ['T-S'],
            'died': ['D'],
            'join_family': ['Ind-JnFam', 'TD-JnFam WG'],
            'community_invitation': ['Ind-Invit'],
            'employed': ['Ind-Empl'],
            'granted': ['Term W-G', 'Term-with Grant']}


mixed_race = ['Japanese and Other, No spouse [6]', 'Japanese and White, No spouse [5]',       
       'Japanese and White, Spouse: Japanese [J]',
       'Japanese and White, Spouse: White [W]',
       'Japanese and Other, Spouse: Japanese [K]',
       'White and Other, Spouse: Japanese [2]',
       'Japanese and Other, Spouse: White [X]',
       'Japanese and White, Spouse: Japanese and White [M]',
       'Japanese, Spouse: Japanese and Other [O]']

mixed_marriage = ['Japanese, Spouse: White [V]','White, Spouse: Japanese [S]', 
                  'Other, Spouse: Japanese [1]','Japanese, Spouse: Japanese and White [L]',
       'White, Spouse: Japanese and White [T]', 'White, No spouse [8]']



for outcome, vals in outcomes.items():
    sliced = df[df.type_of_final_departure.isin(vals)]
    count = sliced.shape[0]
    print('~~~~~~~~~~')
    print('outcome:', outcome, count)
    print('avg age', round(sliced.age_at_departure.mean().days / 365.25, 3), 'years')
    print('avg time incarcerated per person', round(sliced.time_incarcerated.dt.days.sum() 
                                                    / (365.25 * count), 2), 'years')
    print('gender', round(100 * (sliced[sliced['sex'] == 'M'].shape[0] / count), 3), '% male')
    print('citizenship', round(100 * (sliced[sliced['citizenship'] == 'C'].shape[0] / count), 3), '% citizens')
    print('top five', sliced.groupby('final_departure_state').size().sort_values(ascending=False)[:5])
    print('\n')
