# -*- coding: utf-8 -*-

import hug, requests, datetime
from dateutil import parser
import getMPmemberships

@hug.get(examples='base_url=http://api.popit.sinarproject.org/&start_date=2008-04-28&end_date=2013-04-03')
@hug.local()           
def MPpersonIDs_date(base_url: hug.types.text, start_date:hug.types.text, end_date:hug.types.text):
    '''
    Generate personIDs of all parliamentarians between a start and end date
    '''   
    MPpersonIDs = []
    memberIDs = MPmemIDs_date(base_url, start_date, end_date)
    
    for membership_id in memberIDs:
        url = base_url+ "/en/memberships/"+ membership_id
        member = requests.get(url).json()['result']

        personID = member['person_id']
        MPpersonIDs.append(personID)
        
    return MPpersonIDs

@hug.get(examples='base_url=http://api.popit.sinarproject.org/&start_date=2013-04-03')
@hug.local()           
def currentMPPersonIDs(base_url: hug.types.text, start_date:hug.types.text):
    '''
    Generate personIDs of all current parliamentarians
    '''   
    MPpersonIDs = []
    memberIDs = currentMPmemIDs(base_url, start_date)
    
    for membership_id in memberIDs:
        url = base_url+ "/en/memberships/"+ membership_id
        member = requests.get(url).json()['result']

        personID = member['person_id']
        MPpersonIDs.append(personID)
        
    return MPpersonIDs


@hug.get(examples='base_url=http://api.popit.sinarproject.org/&start_date=2008-04-28&end_date=2013-04-03')
@hug.local()
def MPPersons(base_url: hug.types.text, start_date:hug.types.text, end_date:hug.types.text):
    '''
    Returns JSON of person details for all parliamentarians between start and end dates
    '''
    personIDs = MPpersonIDs_date(base_url, start_date, end_date)
    
    persons_json = []
    for person_id in personIDs:
        json =  {}
        url = base_url+ "/en/persons/"+ person_id
        r = requests.get(url).json()['result']
        
        persons_json.append(r)
    return persons_json
    
@hug.get(examples='base_url=http://api.popit.sinarproject.org/&start_date=2013-04-03')
@hug.local()
def currentMPPersons(base_url: hug.types.text, start_date:hug.types.text):
    '''
    Returns JSON of person details for all current parliamentarians.
    '''
    personIDs = currentMPPersonIDs(base_url, start_date)
    
    persons_json = []
    for person_id in personIDs:
        url = base_url+ "/en/persons/"+ person_id
        r = requests.get(url).json()['result']
        
        persons_json.append(r)
    return persons_json
    
@hug.get(examples='base_url=http://api.popit.sinarproject.org/&start_date=2013-04-03')
@hug.local()
def getCurrentWomenMPs(base_url: hug.types.text, start_date:hug.types.text):
    '''
    Returns JSON of person details for all current female parliamentarians.
    '''
    personIDs = currentMPPersonIDs(base_url, start_date)
    
    womenMPs_json = []
    for person_id in personIDs:
        url = base_url+ "/en/persons/"+ person_id
        r = requests.get(url).json()['result']
        
        if r['gender']== 'Female':
            womenMPs_json.append(r)
            
    return womenMPs_json
    