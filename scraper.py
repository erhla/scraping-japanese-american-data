"""
scraping-japanese-american-data

scraper.py scrapes webpages from the National
Archives to a designated csv file

Call get_years(starting year, ending year) to
scrape records

For example, to scrape 1900 to 1910 call get_years('00', '10')

Eric Langowski
"""

import re
import bs4
import requests
import pandas as pd
from selenium import webdriver
import time

COLUMN_NAMES = set(['LAST NAME',
                    'FIRST NAME',
                    'MIDDLE INITIAL',
                    'RELOCATION PROJECT',
                    'ASSEMBLY CENTER',
                    'LAST PERMANENT ADDRESS',
                    'LAST PERMANENT ADDRESS STATE',
                    'LAST PERMANENT ADDRESS COUNTY',
                    'LAST PERMANENT ADDRESS POPULATION DENSITY',
                    'BIRTH PLACE OF PARENTS',
                    'FATHERS OCCUPATION IN U.S.',
                    'FATHERS OCCUPATION ABROAD',
                    'TOTAL YEARS OF SCHOOLING IN JAPAN',
                    'YEARS OF SCHOOLING IN JAPAN',
                    'EDUCATIONAL DEGREES',
                    'YEAR OF FIRST ARRIVAL IN TERRITORIAL U.S.',
                    'TOTAL LENGTH OF TIME IN JAPAN',
                    'NUMBER OF TIMES IN JAPAN',
                    'AGE AT TIME IN JAPAN',
                    'MILITARY AND NAVAL SERVICE, PUBLIC ASSISTANCE AND PENSIONS, PHYSICAL DEFECTS',
                    'INDIVIDUAL NUMBER',
                    'SEX AND MARITAL STATUS',
                    'RACE OF INDIVIDUAL AND SPOUSE',
                    'YEAR OF BIRTH',
                    'BIRTH PLACE',
                    'ALIEN REGISTRATION NUMBER, SOCIAL SECURITY NUMBER AND JAPANESE LANGUAGE SCHOOL',
                    'HIGHEST GRADE COMPLETED OR GRADE ATTENDING',
                    'LANGUAGE',
                    'RELIGION',
                    'PRIMARY OCCUPATION',
                    'SECONDARY OCCUPATION',
                    'TERTIARY OCCUPATION',
                    'POTENTIAL OCCUPATION 1',
                    'POTENTIAL OCCUPATION 2',
                    'FILE NUMBER',
                    'BLANK 1'])

MAIN_URL = 'https://aad.archives.gov/aad/record-detail.jsp?dt=2003&mtch=6919&cat=all&tf=F&sc=24943,24947,24948,24949,24942,24938,24928,24940&bc=sl,fd&cl_24949=8&op_24949=null&nfo_24949=V,1,1900&rpp=10&pg=1&rid=82&rlst=82,98,99,100,101,102,103,104,105,107'
ABSOLUTE_URL = 'https://aad.archives.gov/aad/'

def url_to_soup(url):
    '''
    helper function which takes a url and returns a bs4 object
    '''
    try:
        r = requests.get(url)
        if r.status_code == 404 or r.status_code == 403:
            r = None
    except Exception:
        r = None

    return bs4.BeautifulSoup(r.text.encode('iso-8859-1'), 'html5lib')


def process_soup(soup):
    '''
    helper function which takes a bs4 object of an individual NARA
    records page from the target data set and returns its table stored
    as a dictionary and the link to the next record
    '''
    d = {}
    for row in soup.find('table').find_all('tr')[1:]:
        cells = row.find_all('td')
        field_name = cells[0].text.strip()
        coded_value = cells[1].text.strip()
        if field_name in COLUMN_NAMES:
            d[field_name] = coded_value
    next_link = ABSOLUTE_URL + soup.find_all('a')[-11]['href']
    return d, next_link

def crawl(starting_url, number_to_crawl):
    '''
    helper function which takes a starting url and a number of pages
    to crawl. After reaching the designated number of pages, the data
    is converted into a dataframe and returned
    '''
    coded_ls = []

    soup = url_to_soup(starting_url)
    coded, next_link = process_soup(soup)
    coded_ls.append(coded)

    i = 1
    while i < number_to_crawl:
        soup = url_to_soup(next_link)
        coded, next_link = process_soup(soup)
        coded_ls.append(coded)
        i = i + 1

    return pd.DataFrame(coded_ls)

BIRTH_URL = 'https://aad.archives.gov/aad/display-partial-records.jsp?dt=2003&sc=24943%2C24947%2C24948%2C24949%2C24942%2C24938%2C24928%2C24940&cat=all&tf=F&bc=sl%2Cfd&q=&as_alq=&as_anq=&as_epq=&as_woq=&nfo_24943=V%2C10%2C1900&op_24943=0&txt_24943=&nfo_24947=V%2C8%2C1900&op_24947=0&txt_24947=&nfo_24948=V%2C1%2C1900&op_24948=0&txt_24948=&nfo_24949=V%2C1%2C1900&cl_24949=&nfo_24942=V%2C1%2C1900&cl_24942=&nfo_24938=V%2C5%2C1900&cl_24938=&nfo_24928=V%2C6%2C1900&op_24928=0&txt_24928=&nfo_24940=V%2C2%2C1900&op_24940=0&txt_24940='

def process_search(soup):
    '''
    process_search takes a soup representing a page of
    NARA search results and determines the number of total records
    returned from that search. The number of records, and the URL for
    the first record are returned.
    '''
    records = soup.find_all('p')[2].text
    r_str = re.findall('[0-9,]*', records)[10]
    num_records = int(r_str.replace(',', ''))
    if num_records == 0:
        return 0, None

    first_record = soup.find_all('table')[1].find_all('a')[8]['href']
    return num_records, ABSOLUTE_URL + first_record

def process_driver(driver):
    '''
    process_driver takes a driver and extracts a soup from its html
    '''
    html = driver.page_source
    soup = bs4.BeautifulSoup(html, 'html5lib')
    return process_search(soup)

def write_records(records_df, output_filename):
    '''
    write_records takes a dataframe and output file name and
    appends the dataframe to the output file
    '''
    with open(output_filename, 'a') as file:
        records_df.to_csv(file, header=False, index=False)


def scrape(year_of_birth, output_filename):
    '''
    scrape takes a individual year of birth and an output filename
    and writes the years records to the file
    '''
    starting_url = BIRTH_URL + year_of_birth

    driver = webdriver.Firefox()
    driver.get(starting_url)
    time.sleep(10)
    records, current_link = process_driver(driver)

    if records != 0:
        while records > 0:
            write_records(crawl(current_link, min(records, 10)), output_filename)
            if records > 10:
                next_page_link = driver.find_element_by_link_text('Next >')
                next_page_link.click()
                time.sleep(10)
                _, current_link = process_driver(driver)
            records = records - 10

    driver.close()

def get_years(first_year_str, last_year_str):
    '''
    get_years is the main function for scraper.py. get_years takes
    two strings in the form 'XX' where allowed values are between '00'
    and '99' and creates an output file of the form 
    first_year_str_to_last_year_str.csv in the current directory.

    For example, to scrape 1900 to 1910 call get_years('00', '10')
    '''

    current_year = int(first_year_str)

    output_filename = first_year_str + '_to_' + last_year_str + '.csv'

    while current_year <= int(last_year_str):
        if current_year < 10:
            current_year_str = '0' + str(current_year)
        else:
            current_year_str = str(current_year)

        scrape(current_year_str, output_filename)
        print("Year completed:", current_year % 100)
        current_year = current_year + 1
