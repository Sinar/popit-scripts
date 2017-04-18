# -*- coding: utf-8 -*-

import hug, requests, datetime
from dateutil import parser

dewanRakyatID = '53633b5a19ee29270d8a9ecf'

@hug.get(examples='base_url=http://api.popit.sinarproject.org/&orgID=53633b5a19ee29270d8a9ecf')
@hug.local()
def genAllMemberIDs(base_url: hug.types.text, orgID:hug.types.text):
    '''
    Generate all member IDs for an organization 
    '''    
    
    url = base_url+ "/en/organizations/" + orgID + "/?minify=True"
    r = requests.get(url).json()['result']
    membershipIDs = r['memberships']
    
    return membershipIDs


@hug.get(examples='base_url=http://api.popit.sinarproject.org/&start_date=2008-04-28&end_date=2013-04-03')
@hug.local()           
def MPmemIDs_date(base_url: hug.types.text, start_date:hug.types.text, end_date:hug.types.text):
    '''
    Generate memberIDs of parliamentarians between start&end date
    '''   

    memberIDs = []
    membershipIDs = genAllMemberIDs(base_url, dewanRakyatID)
    
    start_datetime = parser.parse(start_date)
    end_datetime = parser.parse(end_date)
    
    for membership_id in membershipIDs:
        url = base_url+ "/en/memberships/"+ membership_id
        member = requests.get(url).json()['result']
        
        if member['start_date']:
            if member['end_date']: #has end date, ex member
                memStart = parser.parse(member['start_date'])
                memEnd = parser.parse(member['end_date'])   
                if memStart >= start_datetime and memEnd <= end_datetime:
                    memberIDs.append(membership_id)
            else: 
                memStart = parser.parse(member['start_date'])
                if memStart >= start_datetime and memStart<= end_datetime:
                    memberIDs.append(membership_id)
                    
    return memberIDs


@hug.get(examples='base_url=http://api.popit.sinarproject.org/&start_date=2013-04-03')
@hug.local()           
def currentMPmemIDs(base_url: hug.types.text, start_date:hug.types.text):
    '''
    Generate memberIDs of current parliamentarians 
    '''   
    memberIDs = []
    membershipIDs = genAllMemberIDs(base_url, dewanRakyatID)
    
    start_datetime = parser.parse(start_date)
    
    for membership_id in membershipIDs:
        url = base_url+ "/en/memberships/"+ membership_id
        member = requests.get(url).json()['result']
        if member['start_date']:
            memStart = parser.parse(member['start_date'])
                
            if memStart >= start_datetime and not member['end_date']:
                memberIDs.append(membership_id)
        
    return memberIDs
    
@hug.get(examples='base_url=http://api.popit.sinarproject.org/&start_date=2008-04-28&end_date=2013-04-03')
@hug.local()
def MPMemberships(base_url: hug.types.text, start_date:hug.types.text, end_date:hug.types.text):
    '''
    Returns json of mem details of all parliamentarians between start and end date
    '''    
    memberships = MPmemIDs_date(base_url, start_date, end_date)
    memberships_json = []
    
    for membership_id in memberships:
        url = base_url+ "/en/memberships/"+ membership_id
        r = requests.get(url).json()['result']
            
        memberships_json.append(r)
        
    return memberships_json


@hug.get(examples='base_url=http://api.popit.sinarproject.org/&start_date=2013-04-03')
@hug.local()
def currentMPMemberships(base_url: hug.types.text, orgID:hug.types.text, start_date:hug.types.text, end_date:hug.types.text):
    '''
    Returns json of mem details of all current parliamentarians.
    '''    
    memberships = currentMPmemIDs(base_url, start_date)
    memberships_json = []
    
    for membership_id in memberships:
        url = base_url+ "/en/memberships/"+ membership_id
        r = requests.get(url).json()['result']
            
        memberships_json.append(r)
        
    return memberships_json
