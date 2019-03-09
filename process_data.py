import pandas as pd
import csv
import collections



NAMES_CODES = [('LAST NAME', ''),
 ('FIRST NAME', ''),
 ('MIDDLE INITIAL', ''),
 ('RELOCATION PROJECT', 234),
 ('ASSEMBLY CENTER', 235),
 ('LAST PERMANENT ADDRESS', 1316),
 ('LAST PERMANENT ADDRESS STATE', 1307),
 ('LAST PERMANENT ADDRESS COUNTY', 1305),
 ('LAST PERMANENT ADDRESS POPULATION DENSITY', 1306),
 ('BIRTH PLACE OF PARENTS', 236),
 ('FATHERS OCCUPATION IN U.S.', 238),
 ('FATHERS OCCUPATION ABROAD', 238),
 ('TOTAL YEARS OF SCHOOLING IN JAPAN',237),
 ('YEARS OF SCHOOLING IN JAPAN', 239),
 ('EDUCATIONAL DEGREES', 250),
 ('YEAR OF FIRST ARRIVAL IN TERRITORIAL U.S.', ''),
 ('TOTAL LENGTH OF TIME IN JAPAN', 240),
 ('NUMBER OF TIMES IN JAPAN', 241),
 ('AGE AT TIME IN JAPAN', 242),
 ('MILITARY AND NAVAL SERVICE, PUBLIC ASSISTANCE AND PENSIONS, PHYSICAL DEFECTS', 4063),
 ('INDIVIDUAL NUMBER', ''),
 ('SEX AND MARITAL STATUS', 244),
 ('RACE OF INDIVIDUAL AND SPOUSE', 249),
 ('YEAR OF BIRTH', ''),
 ('BIRTH PLACE', 252),
 ('ALIEN REGISTRATION NUMBER, SOCIAL SECURITY NUMBER AND JAPANESE LANGUAGE SCHOOL', 245),
 ('HIGHEST GRADE COMPLETED OR GRADE ATTENDING', 246),
 ('LANGUAGE', 247),
 ('RELIGION', 4143),
 ('PRIMARY OCCUPATION', 251),
 ('SECONDARY OCCUPATION', 251),
 ('TERTIARY OCCUPATION', 251),
 ('POTENTIAL OCCUPATION 1', 251),
 ('POTENTIAL OCCUPATION 2', 251),
 ('FILE NUMBER', ''),
 ('BLANK 1', '')]

NAMES_CODES2 = [('AGE AT TIME IN JAPAN', 242),
 ('ALIEN REGISTRATION NUMBER, SOCIAL SECURITY NUMBER AND JAPANESE LANGUAGE SCHOOL',
  245),
 ('ASSEMBLY CENTER', 235),
 ('BIRTH PLACE', 252),
 ('BIRTH PLACE OF PARENTS', 236),
 ('BLANK 1', ''),
 ('EDUCATIONAL DEGREES', 250),
 ('FATHERS OCCUPATION ABROAD', 238),
 ('FATHERS OCCUPATION IN U.S.', 238),
 ('FILE NUMBER', ''),
 ('FIRST NAME', ''),
 ('HIGHEST GRADE COMPLETED OR GRADE ATTENDING', 246),
 ('INDIVIDUAL NUMBER', ''),
 ('LANGUAGE', 247),
 ('LAST NAME', ''),
 ('LAST PERMANENT ADDRESS', 1316),
 ('LAST PERMANENT ADDRESS COUNTY', 1305),
 ('LAST PERMANENT ADDRESS POPULATION DENSITY', 1306),
 ('LAST PERMANENT ADDRESS STATE', 1307),
 ('MIDDLE INITIAL', ''),
 ('MILITARY AND NAVAL SERVICE, PUBLIC ASSISTANCE AND PENSIONS, PHYSICAL DEFECTS',
  4063),
 ('NUMBER OF TIMES IN JAPAN', 241),
 ('POTENTIAL OCCUPATION 1', 251),
 ('POTENTIAL OCCUPATION 2', 251),
 ('PRIMARY OCCUPATION', 251),
 ('RACE OF INDIVIDUAL AND SPOUSE', 249),
 ('RELIGION', 4143),
 ('RELOCATION PROJECT', 234),
 ('SECONDARY OCCUPATION', 251),
 ('SEX AND MARITAL STATUS', 244),
 ('TERTIARY OCCUPATION', 251),
 ('TOTAL LENGTH OF TIME IN JAPAN', 240),
 ('TOTAL YEARS OF SCHOOLING IN JAPAN', 237),
 ('YEAR OF BIRTH', ''),
 ('YEAR OF FIRST ARRIVAL IN TERRITORIAL U.S.', ''),
 ('YEARS OF SCHOOLING IN JAPAN', 239)]




def generate_data_dictionary(directory):
    values_dict = {}
    for col_name, file_id in NAMES_CODES2:
        if file_id:
            file_loc = directory + 'cl_' + str(file_id) + '.csv'
            file_df = pd.read_csv(file_loc, index_col=0, usecols=[0,1])
            file_dict = file_df.to_dict()['Meaning']
            values_dict[col_name] = file_dict
        else:
            values_dict[col_name] = None
    return values_dict

def map_value(entry):
    for col, row in entry.iteritems():   
        code_dict = values_dict[col]
        if code_dict:
            code = code_dict[row]
        else:                  
            code = ''      
    print(col, '| ', row, '| ', code)


def process(file_name):
    col_names = []
    for item, _ in NAMES_CODES2:
        col_names.append(item)
    df = pd.read_csv(file_name, names=col_names, dtype=str)
    return df
