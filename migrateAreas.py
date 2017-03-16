#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar  6 13:49:27 2017
@author: kay-wong

Script to add new area class.

"""

import re, requests, difflib, csv
import pandas as pd
from bs4 import BeautifulSoup
from urllib.request import urlopen
import sys

base_url = "http://api.popit.sinarproject.org"
token =  open('token.txt')
headers = {'Authorization': token}


def clean(label):
    label = label.strip()
    label = re.sub(r'-', ' ', label.lower())
    return re.sub(r'[^\w\s]', '', label)


def constructAreaDic():
    '''
        Construct dic mapping parliament constituencies to their codes
    '''
    page = urlopen("https://en.wikipedia.org/wiki/List_of_Malaysian_electoral_districts").read()
    soup = BeautifulSoup(page)
    #All state tables are of class tag wikitables, exact match             
    wikitables = soup.findAll(lambda tag: tag.name== "table" and tag.get("class")== ["wikitable"])

    areaDic = {}
    
    for table in wikitables:
        for row in table.findAll("tr"):
            cells = row.findAll("td")
            try:
                #Add Parlimanetary Constituencies
                parlID = clean(cells[0].find(text = True))
                parlName = clean(cells[0].find('a').contents[0])
                areaDic[parlName] = parlID 
                
            except IndexError:
                pass
    

    return areaDic

def deleteAreas():
    '''
        Delete all entries in Area class
    '''
    page = 1
    hasMore = True
    
    while hasMore:
        r = requests.get('http://api.popit.sinarproject.org/en/areas/?page=' + str(page)).json()
        for area in r['results']:
            entryID = area['id']
            delURL = base_url+ "/en/areas/"+ entryID
            requests.delete(delURL, headers =headers )
        
        hasMore = r['has_more']
        page+=1
        
def identifierToID_dic():
    '''
        Construct dic mapping area identifier to entry ID in Areas class
    '''
    has_more = True 
    pg = 1
    
    ID_dic = {}
    while has_more:
    
        r = requests.get('http://api.popit.sinarproject.org/en/areas/?page='+str(pg)).json()
        for area in r['results']:
            entryID = area['id']
            areaID = area['identifier']
            
            ID_dic[areaID] = entryID
                  
        has_more = r['has_more']
        pg +=1
    
    return ID_dic


def IDToIdentifier_dic():
    ID_dic = identifierToID_dic()
    identifierDic = {}
    for areaID, entryID in ID_dic.items():
        identifierDic[entryID] = areaID
    
    return identifierDic

def identifierToArea_dic():
    areaDic = constructAreaDic()
    pidToArea = {}
    for areaName, pid in areaDic.items():
        pidToArea[pid] = areaName
    
    return pidToArea

def postAreas(areaDic):
    '''
        One time script to post all areas to Popit DB
    '''
    url = base_url+ "/en/areas"
    for area, areaID in areaDic.items():
        payload = {'name': area , 'identifier': areaID, 'classification': 'Parliamentary Constituency'}
        r = requests.post(url, headers = headers, json = payload)     
        print(r.text)

def postToAreaID(postLabel, areaDic):
    '''
        String matching to match area from MP postLabel to area identifier
    '''
    eqName = {'pj': 'petaling jaya', 'belawai':'kuala rajang', 'ulu': 'hulu', 'bahru': 'bharu', 'tanjung': 'tanjong', 'teluk': 'telok'}
                   
    try:
        areaName = clean(postLabel.split('MP for')[1])
        areaID = areaDic[areaName]
        
    except KeyError:
        
        try: 
            areaName = " ".join(list(map((lambda x: eqName[x] if x in eqName.keys() else x), areaName.split(' '))))
            areaID = areaDic[areaName]
            
        except (NameError, KeyError):
            #if all else fails, try finding closest match
            areaNames = list(areaDic.keys())
            #Get closest name match, TODO: add threshold >= 0.9
            areaMatch = max(areaNames, key = lambda x: difflib.SequenceMatcher(None, x, areaName).ratio())
            areaID = areaDic[areaMatch]
            
            print("MATCHED " + str(areaName)+ " to "+ str(areaMatch))
        
        except:
            print("PostToAreaID Error")
            print(postLabel)
            e = sys.exc_info()[0]
            print(e)


    
    return areaID

        
def updateMPAreas(areaDic, ID_dic):
    '''
        Match area information to corresponding entry in Area class for all MPs
    '''

    dewanRakyatOrgID = "53633b5a19ee29270d8a9ecf"
    url = base_url+ "/en/organizations/" + dewanRakyatOrgID + "/?minify=True"
    
    r = requests.get(url).json()['result']
    memberships = r['memberships']

    
    for membership_id in memberships:
        try: 
            
            url = base_url+ "/en/memberships/"+ membership_id
            r = requests.get(url).json()['result']
            postID = r['post_id']
            
            try:
                postLabel = r['label'] or r['post']['label']
            except TypeError:
                postLabel = r['label']
              
            if not pd.isnull(postLabel):
                #If postlabel for this MP is not empty
                areaIdentifier = postToAreaID(postLabel, areaDic)
                entryID = ID_dic[areaIdentifier]
                
                payload = {"area_id": entryID} 
                putURL = base_url+"/en/posts/"+ postID
            
                
                r = requests.put(putURL, headers = headers, json = payload)
                
                if r.status_code != requests.codes.ok:
                    print(r.status_code)
                    print(str(membership_id)+ ": "+ str(postLabel))
                    print(entryID)
                    
                else:
                    pass
                
            else:
                pass
            
            
        except:
            print("UpdateMPArea error")
            e = sys.exc_info()[0]
            print(e)
            
            print(str(membership_id + str(postLabel)))

            
  


            
