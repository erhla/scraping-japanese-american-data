'''
process_data cleans and creates descriptive mapped values
from the raw NARA dataset
'''

import pandas as pd
import requests

NAMES_CODES = [('AGE AT TIME IN JAPAN', 242),
               ('ALIEN REGISTRATION NUMBER, SOCIAL SECURITY NUMBER AND JAPANESE LANGUAGE SCHOOL', 245),
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
               ('MILITARY AND NAVAL SERVICE, PUBLIC ASSISTANCE AND PENSIONS, PHYSICAL DEFECTS', 4063),
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

ABSOLUTE_DICT_URL = 'https://aad.archives.gov/aad/Download/cl_'

def download_nara_dictionaries(files_dir):
    '''
    download_nara_dictionaries downloads a list of csvs from
    the NARA website which map coded values to descriptive names the
    provided files_dir is where the files will be stored

    ex) https://aad.archives.gov/aad/Download/cl_235.csv
    '''
    to_download = set()
    for _, file_num in NAMES_CODES:
        if file_num:
            to_download.add(file_num)
    for file_num in to_download:
        file_name = str(file_num) + '.csv'
        r = requests.get(ABSOLUTE_DICT_URL + file_name)
        with open(files_dir + 'cl_' + file_name, 'wb') as f:
            f.write(r.content)
        print(file_name, ' completed')

def generate_data_dictionary(directory, download_files=False):
    '''
    generate_data_dictionary takes a directory where the nara
    dictionaries are stored or takes a directory to store the files
    and download_files=True

    returns a dictionary which maps column names to values to
    descriptive values
    '''
    if download_files:
        download_nara_dictionaries(directory)

    values_dict = {}
    for col_name, file_id in NAMES_CODES:
        if file_id:
            file_loc = directory + 'cl_' + str(file_id) + '.csv'
            file_df = pd.read_csv(file_loc, index_col=0, usecols=[0, 1], dtype=str)
            file_dict = file_df.to_dict()['Meaning']
            if file_id == 251:
                missing_dict = {'039': '39',
                                '030': '30',
                                '071': '71',
                                '043': '43',
                                '024': '24',
                                '072': '72',
                                '008': '8',
                                '045': '45',
                                '098': '98',
                                '048': '48',
                                '4X2': '4-2',
                                '4X6': '4-6',
                                '6X6': '6-6',
                                '6X4': '6-4',
                                '2X1': '2-1'
                                }
                for key, to_add in missing_dict.items():
                    file_dict[to_add] = file_dict[key]
            if file_id == 237:
                graduate_ls = list('HIJKL')
                for item in graduate_ls:
                    file_dict[item] = '16 YEARS, ETC.'
            if col_name == 'RELOCATION PROJECT':
                new = {}
                for key, val in file_dict.items():
                    new[str(key)] = val
                file_dict = new
            values_dict[col_name] = file_dict
        else:
            values_dict[col_name] = None
    return values_dict

def view_record(entry, values_dict):
    '''
    view_record takes an individual entry from a df and
    and values dictionary and prints the mapped values
    or the original value if no mapping exists
    '''
    for col, row in entry.iteritems():
        code_dict = values_dict[col]
        if code_dict:
            if row == row:
                code = code_dict[row]
            else:
                code = ''
        else:
            code = ''
        if code:
            print(col, ':', code)
        else:
            print(col, ':', row)

def bad_values(df, values_dict):
    '''
    bad_values is a helper function which finds values
    that have no mapped value in values_dict

    These errors are original to the data
    '''
    for col in df.columns:
        col_values = df[col].unique()
        valid_values = values_dict[col]
        if valid_values:
            bad_values = set(col_values) - set(valid_values)
        if bad_values:
            print(col, ' has bad values')
            for value in bad_values:
                count = df[df[col] == value].shape[0]
                if count > 5:
                    print(value, 'appears ', count)


def process(file_name, data_dir, download_files=False):
    '''
    process takes a file_name which is a csv of the NARA database and
    returns a dataframe with column names and proper types
    '''
    col_names = []
    to_correct = ['POTENTIAL OCCUPATION 1',
                  'POTENTIAL OCCUPATION 2',
                  'PRIMARY OCCUPATION',
                  'SECONDARY OCCUPATION',
                  'TERTIARY OCCUPATION',
                  'RELOCATION PROJECT',
                  'EDUCATIONAL DEGREES',
                  'LANGUAGE',
                  'LAST PERMANENT ADDRESS POPULATION DENSITY',
                  'LAST PERMANENT ADDRESS STATE',
                  'NUMBER OF TIMES IN JAPAN',
                  'RACE OF INDIVIDUAL AND SPOUSE',
                  'SEX AND MARITAL STATUS',
                  'TOTAL LENGTH OF TIME IN JAPAN',
                  'YEARS OF SCHOOLING IN JAPAN']
    for item, _ in NAMES_CODES:
        col_names.append(item)
    df = pd.read_csv(file_name, skiprows=[0], names=col_names, dtype=str)
    for col in to_correct:
        df[col] = df[col].apply(lambda x: str(x).replace(".0", "") if x == x else x)
    values_dict = generate_data_dictionary(data_dir, download_files)

    for col in col_names:
        print(col)
        if values_dict[col]:
            df[col] = df[col].map(values_dict[col]).astype('category')
    df['YEAR OF BIRTH'] = df['YEAR OF BIRTH'].astype(int)
    df['YEAR OF BIRTH'] = df['YEAR OF BIRTH'].apply(lambda x: 1800 + x if x > 43 else 1900 + x)

    return df
