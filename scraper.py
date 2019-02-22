"""
scraping-japanese-american-data

Eric Langowski
"""

import json
import sys
import csv
import re
import bs4
import urllib.parse
import os
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

starting_url = 'https://aad.archives.gov/aad/record-detail.jsp?dt=2003&mtch=6919&cat=all&tf=F&sc=24943,24947,24948,24949,24942,24938,24928,24940&bc=sl,fd&cl_24949=8&op_24949=null&nfo_24949=V,1,1900&rpp=10&pg=1&rid=82&rlst=82,98,99,100,101,102,103,104,105,107'
absolute_fragment = 'https://aad.archives.gov/aad/'

def url_to_soup(url):

    try:
        r = requests.get(url)
        if r.status_code == 404 or r.status_code == 403:
            r = None
    except Exception:
        r = None
    
    return bs4.BeautifulSoup(r.text.encode('iso-8859-1'), 'html5lib')


def process_soup(soup):
	d = {}
	for row in soup.find('table').find_all('tr')[1:]:
		cells = row.find_all('td')
		field_name = cells[0].text.strip()
		coded_value = cells[1].text.strip()
		#mapped_value = cells[2].text.strip()
		if field_name in COLUMN_NAMES:
			d[field_name] = coded_value
	next_link = absolute_fragment + soup.find_all('a')[-11]['href']
	return d, next_link

def crawl(starting_url, number_to_crawl):
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

	df = pd.DataFrame(coded_ls)


	return df

birth_url = 'https://aad.archives.gov/aad/display-partial-records.jsp?dt=2003&sc=24943%2C24947%2C24948%2C24949%2C24942%2C24938%2C24928%2C24940&cat=all&tf=F&bc=sl%2Cfd&q=&as_alq=&as_anq=&as_epq=&as_woq=&nfo_24943=V%2C10%2C1900&op_24943=0&txt_24943=&nfo_24947=V%2C8%2C1900&op_24947=0&txt_24947=&nfo_24948=V%2C1%2C1900&op_24948=0&txt_24948=&nfo_24949=V%2C1%2C1900&cl_24949=&nfo_24942=V%2C1%2C1900&cl_24942=&nfo_24938=V%2C5%2C1900&cl_24938=&nfo_24928=V%2C6%2C1900&op_24928=0&txt_24928=&nfo_24940=V%2C2%2C1900&op_24940=0&txt_24940='

def process_search(soup):
	records = soup.find_all('p')[2].text
	r_str = re.findall('[0-9,]*', records)[10]
	num_records = int(r_str.replace(',',''))
	if num_records == 0:
		return 0, None

	first_record = soup.find_all('table')[1].find_all('a')[8]['href']
	return num_records, absolute_fragment + first_record

def scrape(year_of_birth):
	starting_url = birth_url + str(year_of_birth)
	driver = webdriver.Firefox()
	driver.get(starting_url)
	driver.implicitly_wait(10)
	time.sleep(10)
	html = driver.page_source
	driver.close()
	soup = bs4.BeautifulSoup(html, 'html5lib')
	num_records, first_link = process_search(soup)
	if num_records == 0:
		return pd.DataFrame()
	df = crawl(first_link, num_records)

	return df

def get_years(first_year, output_filename):
	
	current_year = first_year
	counter = 0
	with open(output_filename, 'a') as file: 
		while counter < 100:
			current_df = scrape(current_year % 100)
			if not current_df.empty:
				current_df.to_csv(file, header=False, index=False)
			current_year = current_year + 1
			counter = counter + 1
			print(current_year % 100 - 1, current_df.shape[0])