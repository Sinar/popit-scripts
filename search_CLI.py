#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 26 09:49:45 2017

@author: kay-wong
"""

import requests
base_url = "http://api.popit.sinarproject.org"
token = open('../token.txt')
headers = {'Authorization': token.read().rstrip()}



def searchCLI_naive(base_url, searchTerm, class_, featureName):
    '''
       Naively searches Popit DB for a feature within a class,
       selecting the first entry
    '''
    
    '{}/en/search/{}/?q={}:{}'.format(base_url, class_, featureName, searchTerm )
    searchURL = base_url+ '/en/search/areas/?q=name:'+ areaName
    r = requests.get(searchURL)
    if r.ok:
        if r.json()['results']:
            return r.json()['results'][0]['id']
    else:
        return None

def searchCLI(base_url, name, class_, feature, otherfeature):
    '''
   Interactive CLI that searches Popit DB for a feature within a class,
   selecting match based on user input

    Inputs: 
        eg. 
        class_: organization, person, post
        feature: names, labels
        otherfeature: othernames, other_labels
    Returns:
        matchID: ID of matched class entry
    '''
    
    searchURL = '{}/en/search/{}?q={}:"{}"'.format(base_url, class_, feature, name)
    matchID = searchMatchCLI(searchURL, name, feature)
    if not matchID:
        searchOtherURL = '{}/en/search/{}?q=other_{}s.{}:"{}"'.format(base_url, class_, feature, feature, name)
        
        matchID = searchMatchCLI(searchOtherURL, name, feature)
        if matchID:
             while True:
                store = input('Store "{0}" as an alternate {1} under the matched {1}? (y/n): '.format(name, feature))
                if store.lower() == 'y':
                    storeURL = '{}/en/{}/{}/{}'.format(base_url, class_, matchID, otherfeature)                               
                    storePayload = {feature: name}
                    
                    print(storeURL)
                    print(storePayload)
                    #r = requests.post(storeURL, headers=headers, json = storePayload)
                    break
            
                elif store.lower() == 'n':
                    break
                else:
                    print("Invalid input\nDo any of these results match your person? (y/n)")
        else:
            print("No matches found. A new entry will be made for this..")
            
    return matchID


def searchMatchCLI(searchURL, name, feature):
   '''
   Interactive CLI that searches Popit DB for a feature within a class,
   selecting match based on user input

    Inputs: 
        eg. 
        name: searchTerm
        feature: names, labels
    Returns:
        matchID: ID of matched class entry
    '''
    r = requests.get(searchURL)
    
    if r.json()['results']:
        results = r.json()['results']
        resultsDic = {}
        for j in range(len(results)):
            p = results[j]
            resultsDic[p['id']] = p[str(feature)]
        
        print("%d closest matches found for %s: " %(len(resultsDic), name))
        ids = list(resultsDic.keys())
        for j in range(len(ids)):
            print("%d.\n  %s: %s \n  ID: %s"%(j, feature.upper(), resultsDic[ids[j]], ids[j]))
    
    
        while True:
            match = input("Do any of these results match? (y/n): ")
            if match.lower() == 'y':
                while True:
                    try:
                        matchIndex = int(input("Please select the matching index: "))
                        if matchIndex>=0 and matchIndex< len(ids):
                            matchID = ids[matchIndex]
                            break
                    except:
                        pass
                    
                break
            elif match.lower() == 'n':
                matchID = None 
                break
            else:
                print("Invalid input\nDo any of these results match your person? (y/n)")
            
    else:
        matchID = None
    
    return matchID
                    
