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
	print(next_link)
	return d, next_link

def crawl(starting_url, number_to_crawl):
	coded_ls = []
	
	soup = url_to_soup(starting_url)
	coded, next_link = process_soup(soup)
	coded_ls.append(coded)

	i = 1
	while i <= number_to_crawl:
		soup = url_to_soup(next_link)
		coded, next_link = process_soup(soup)
		coded_ls.append(coded)
		i = i + 1
		print(i)

	df = pd.DataFrame(coded_ls)


	return df


