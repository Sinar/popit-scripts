#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 15 16:33:35 2017

@author: kay-wong
"""


import csv, requests, re, sys
import pandas as pd
import utils
import argparse
import search_CLI

base_url = "http://api.popit.sinarproject.org"
token = open('../token.txt')
headers = {'Authorization': token.read().rstrip()}


def personImport(orgID, csvName):
    '''
    Generate CSV of person details for all members of an org
    '''
    personIDs = utils.genCurrentPersonIDs(base_url, orgID)
    
    headerRow = ['name','birth_date', 'death_date', 'gender','summary', 'biography', 'national_identity', 'image', 'family_name', 'given_name','additional_name','honorific_prefix','honorific_suffix','patronymic_name','sort_name']    
    contactKeys  = ['twitter','email', 'cell', 'voice', 'fax', 'address']
    linkKeys  = ['facebook','wikipedia', 'officialWebsite']
    
    idCols = ['id']
    idCols.extend(['contact_'+ k + '_id' for k in contactKeys])
    idCols.extend(['link_'+ k + '_id' for k in linkKeys])
    
    headerRow.extend(['contact_'+ k for k in contactKeys])
    headerRow.extend(['link_'+ k for k in linkKeys])
    headerRow.extend(idCols)
    
    mp_csv = csv.writer(open("../"+csvName+".csv", "w"))
    mp_csv.writerow(headerRow)
    
    for person_id in personIDs:
        url = base_url+ "/en/persons/"+ person_id
        person = requests.get(url).json()['result']
        
        if person['contact_details']:
             contacts = person.pop('contact_details')
             for c in contacts:
                person['contact_'+ c['type']] = c['value']
                person['contact_'+ c['type']+ '_id'] = c['id']
        
        if person['links']:
            links = person.pop('links')
            for l in links:
                for linkType in ['facebook', 'wikipedia', 'official website']:    
                    if linkType in utils.cleanText(l['note']):
                        person['link_'+ linkType] =   l['url']
                        person['link_'+ linkType + '_id'] =   l['id']
                        break
        
        row = [person[k] if k in person else None for k in headerRow]
        mp_csv.writerow(row)
        


                
def personUpdate(df):
    '''
    Imports data from df of person details to PopitReturns:
    '''
    #addPersons
    newPersons = df[df['person_id']== ""]
    
    for i in newPersons.index:
        person=  newPersons.loc[i]
        person_id = search_CLI.searchCLI(base_url, person['name'], 'persons', 'name', 'othernames')
        if person_id:
            newPersons.is_copy = False
            #set id of person as id found
            newPersons.loc[i, 'person_id'] = person_id
            newPersons.drop(i, axis=0, inplace= True)
    
    #Add persons        
    if not newPersons.empty:
        newPersons = newPersons.drop('person_id', axis=1)
        payloads = generatePayloads(newPersons)
        
        url = base_url + "/en/persons/"
        for payload in payloads:
            r = requests.post(url, headers=headers, json= payload)
        
    #updatePersons
    df = df.drop(df[df['person_id']== ""].index)
    payloads = generatePayloads(df)
    #Post all payloads
    payloads = pd.Series(payloads)
    payloads.apply(putPayloads)
    

def generatePayloads(df):
    '''
    Generate complete payloads
    Returns:
        payloads for entire df
    '''
    contacts = df.filter(regex=r'^contact_', axis=1)
    links = df.filter(regex=r'^link_', axis=1)
    rest = df.filter(regex=r'^(?!link_|contact_)', axis=1)

    #Get contacts and links payloads
    contactP = contacts.apply(getContactPayload, axis=1)
    linkP = links.apply(getContactPayload, axis=1)
    
    #Merge all
    concat = pd.concat([contactP, linkP], axis=1)
    concat.columns= ['contact_details', 'links']
    
    concat = pd.concat([rest, concat], axis=1)
    payloads=  concat.to_dict(orient= 'records') #Payloads for each entry
    
    return payloads

def generatePayload_row(row):
    '''
    Generate complete payloads for a single row
    Inputs:
        row: pd.Series object, row containing person details
    Returns:
        payload for a single row
    '''
    contacts = row.filter(regex=r'^contact_')
    links = row.filter(regex=r'^link_')
    rest = row.filter(regex=r'^(?!link_|contact_)')
    payload = rest.to_dict()
    #Get contacts and links payloads
    
    contactP = getContactPayload(contacts)
    linkP = getContactPayload(links)
    
    #Merge all
    payload['contact_details'] = contactP
    payload['links'] = linkP
    
    return payload
    


def putPayloads(payload):
    '''
    Puts complete payloads for a payload entry for a single person to Popit DB
    Inputs:
        payload: payload entry for a single person
    
    '''
    personID = payload['person_id']
    url = base_url+ "/en/persons/"+ personID
    payload  = dict((k,v) for k,v in payload.items() if v)
    #print(payloads)
    r = requests.put(url, headers=headers, json= payload)
    if not r.ok:
        print(r.content)
        
def getContactPayload(contact):
    '''
    Generate complete payloads for a contacts dictionary
    Inputs:
        contact: dictionary with 'contact_details' prefixes, including id and value columns
    Returns:
        payload: contact payload for a single row's contact_details
    '''
    cd = {}
    #groupby type of contact
    for key, value in sorted(contact.items()):
        cd.setdefault(extractType(key), []).append(contact[key])
    #create payload only if value is not null
    payload = [{'type': k, 'value': cd[k][0], 'id': cd[k][1]}  for k in cd.keys() if cd[k][0]]
    return payload

def getLinkPayload(link):
    '''
    Generate complete payloads for a links dictionary
    Inputs:
        link: dictionary with 'link' prefixes, including id and value columns
    Returns:
        payload: link payload for a single row's links
    '''
    linko =  {}
    #groupby type of link
    for key, value in sorted(link.items()):
        linko.setdefault(extractType(key), []).append(link[key])
    
    linkNoteMap = {'facebook':'Official Facebook account' , 'wikipedia': 'Wikipedia', 'officialWebsite': 'Official Website'}
    #create payload only if url is not null
    payload = [{'note': linkNoteMap[k], 'url': linko[k][0], 'id': linko[k][1]}  for k in linko.keys() if linko[k][0]]
    return payload

def extractType(k):
    '''
    Extracts contact_details/link types
    Inputs:
        k: contact_detail/link key 
        eg. link_facebook, link_wikipedia_id
    Returns:
        match: extracted contact_detail/link type
        eg. facebook, wikipedia
    '''
    match =re.search(r'(?<=\_).*?(?=(?:\_|$))', k).group()  #match between '_' or till end of str
    return match

