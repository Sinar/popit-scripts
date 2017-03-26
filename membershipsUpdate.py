#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 23 18:45:45 2017

@author: kay-wong
"""

import pandas as pd
import numpy as np
import requests, sys, argparse
import search_CLI


def genPayloads(base_url, row, orgID):
    '''
    Generates membership payload for row
    
    Inputs:
        row: pd.Series object, row containing membership details
        orgID: orgID used to generate membership sheet
    Returns:
        df_changes: dataframe of changed rows
        
    '''
    
    #================== AREA ==================
    area = row.filter(regex=r'^area_')
    areaP =  getPayload_class(area, 'area')    
    area_id = areaP.pop('id')
    url = base_url+ "/en/areas/"
    
    if not area_id:   #Get ID from area_name or area identifier:
        area_id = search_CLI.searchCLI_naive(base_url, row['area_name'], 'areas', 'name') or search_CLI.searchCLI_naive(base_url, row['area_identifier'], 'areas', 'identifier')
    if area_id: #Update
        pass
    else:   #Add 
        r = requests.post(url, headers=headers, json=areaP)
        area_id = r.json()['result']['id']
        
    #================== ORG ON BEHALF OF  ==================
    on_behalf_of_id = row['on_behalf_of_id']
    url = base_url+ "/en/organizations/"
     
    if not on_behalf_of_id:
        if row['on_behalf_of']:
            on_behalf_of_id = search_CLI.searchCLI(base_url, orgName, 'organizations', 'name', 'othernames')
    
    if on_behalf_of_id: #Update
        pass
    else:   #Add
        OBO_orgP = {'name': row['on_behalf_of']}
        r = requests.post(url, headers=headers, json=OBO_orgP)
        on_behalf_of_id = r.json()['result']['id']
        
    #================== POST ==================
    post = row.filter(regex=r'^post_')
    postP =  getPayload_class(post, 'post')
    post_id = postP.pop('id')
    url = base_url+ "/en/posts/"
    
    if not post_id and postP['label']:
        post_id = search_CLI.searchCLI(base_url, postLabel, 'posts', 'label', 'other_labels')
    
    postP['organization_id'] = orgID
    postP['area_id'] = area_id
    if post_id: #Update
        url = url+ post_id
        postP.pop('label')
        r = requests.put(url, headers=headers, json=postP)
    else:   #Add 
        r = requests.post(url, headers=headers, json=postP)
        post_id = r.json()['result']['id']
        
    #================== PERSONS ==================
    person = row.filter(regex=r'^person_')
    personP =  getPayload_class(person, 'person')
    person_id = personP['id']
    url = base_url+ "/en/persons/"
    
    if not person_id:
        if personP['name']:
            person_id = search_CLI.searchCLI(base_url, personName, 'persons', 'name', 'othernames')
    if person_id: #Update
        pass  
    else:   #Add 
        r = requests.post(url, headers=headers, json=personP)
        area_id = r.json()['result']['id']
         
    #================== MEMBERSHIPS ==================
    memP = {
    'area_id': area_id,
    'on_behalf_of_id': on_behalf_of_id,
    'post_id': post_id,
    'person_id': person_id,   
    'organization_id': orgID
    }
    url = base_url+ "/en/memberships/"
    memP = dict((k,v) for k,v in memP.items() if v) #remove keys with null vals
    if row['membership_id']:    #Update
        url = url+ row['membership_id']
        r = requests.put(url, headers=headers, json= memP)
    else:
        r = requests.post(url, headers=headers, json=memP)
        membership_id = r.json()['result']['id']
    
    
              
def getPayload_class(c, cName):
    d = {}  
    for key, value in sorted(c.items()):
        d[key.split(cName+'_')[1]] =  c[key]       
    return d
