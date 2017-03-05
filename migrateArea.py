#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 28 18:35:59 2017

@author: metamatical
"""

from bs4 import BeautifulSoup
from urllib.request import urlopen
import sys

base_url = "http://api.popit.sinarproject.org"
token = open('token.txt')
headers = {'Authorization': token.read().rstrip()}


page = urlopen("https://en.wikipedia.org/wiki/List_of_Malaysian_electoral_districts").read()
soup = BeautifulSoup(page)

#All state tables are of class tag wikitables, exact match             
wikitables = soup.findAll(lambda tag: tag.name== "table" and tag.get("class")== ["wikitable"])


def clean(label):
    label = re.sub(r'-', ' ', label.lower())
    return re.sub(r'[^\w\s]', '', label)

def constructAreaDic():
    '''
        Construct dic mapping parliament and state constituencies to their codes
    '''
    areaDic = {}
    
    for table in wikitables:
        for row in table.findAll("tr"):
            cells = row.findAll("td")
            try:
                #Add Parlimanetary Constituencies
                parlID = clean(cells[0].find(text = True))
                parlName = clean(cells[0].find('a').contents[0])
                areaDic[parlName] = parlID 
                
                #Add State Constituencies 
                stateCon = cells[3].findAll(text= True)
                for SID, Sname in zip(stateCon[0::2], stateCon[1::2]):
                    areaDic[clean(Sname)] = clean(SID.replace('\n', ''))
            except IndexError:
                pass
    
    areaDic['kuala rajang'] = 'n41'

    return areaDic


def fixArea(r, areaDic, dic):
    
    #Alt names
    eqName = {'pj': 'petaling jaya', 'belawai':'kuala rajang', 'ulu': 'hulu', 'bahru': 'bharu', 'tanjung': 'tanjong', 'teluk': 'telok'}

    for person in r['result']:
        if person['memberships']:
            for membership in person['memberships']:
                try:
                    if membership['post_id']: 
                        if membership['area']['name']:
                            try:
                                areaName = clean(membership["area"]['name'])
                                areaDic[areaName]
                                
                            except KeyError:
                                try: 
                                    areaName = " ".join(list(map((lambda x: eqName[x] if x in eqName.keys() else x), areaName.split(' '))))
                                    
                                except:
                                    #if all else fails, try finding closest match
                                    areaNames = list(areaDic.keys())
                                    #Get closest name match, TODO: add threshold >= 0.9
                                    areaMatch = max(areaNames, key = lambda x: difflib.SequenceMatcher(None, x, areaName).ratio())
                                    areaDic[areaMatch]
                                    matchRecord[areaMatch] = areaName
                                               
                            except:
                                e = sys.exc_info()[0]
                                print(e)
                                
                except KeyError:
                    pass

    #map`
def fixAllAreas():
    has_more = True 
    pg = 1
    areaDic = constructAreaDic()
    matchRecord = {}
    
    while has_more:
        
        r = requests.get('https://sinar-malaysia.popit.mysociety.org/api/v0.1/persons/?page='+str(pg)).json()
        fixArea(r, areaDic, areaError)
                
        has_more = r['has_more']
        pg +=1
        
