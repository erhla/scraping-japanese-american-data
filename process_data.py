import pandas as pd
import csv
import collections

NAMES_CODES = [('AGE AT TIME IN JAPAN', 242),
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
    for col_name, file_id in NAMES_CODES:
        if file_id:
            file_loc = directory + 'cl_' + str(file_id) + '.csv'
            file_df = pd.read_csv(file_loc, index_col=0, usecols=[0,1], dtype=str)
            file_dict = file_df.to_dict()['Meaning']
            if file_id == 251:
                new = {}
                for key, val in file_dict.items():
                    
            if col_name == 'RELOCATION PROJECT':
                new = {}
                for key, val in file_dict.items():
                    new[str(key)] = val
                file_dict = new
            values_dict[col_name] = file_dict
        else:
            values_dict[col_name] = None
    return values_dict

def map_value(entry, values_dict):
    for col, row in entry.iteritems():   
        code_dict = values_dict[col]
        if code_dict:
            if row == row:
                code = code_dict[row]
            else:
                code = ''
        else:                  
            code = ''      
        print(col, '| ', row, '| ', code)


def process(file_name):
    col_names = []
    to_correct = ['POTENTIAL OCCUPATION 1',
                  'POTENTIAL OCCUPATION 2']
    for item, _ in NAMES_CODES:
        col_names.append(item)
    df = pd.read_csv(file_name, skiprows=[0], names=col_names, dtype=str)
    for col in to_correct:
        df[col] = df[col].apply(lambda x: str(x).replace(".0", "") if x == x else x)
    return df
