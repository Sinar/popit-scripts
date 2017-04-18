#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests, hug
from dateutil import parser
from geopy.geocoders import GoogleV3
api_key = "AIzaSyDo0FrdUg0ZTQm1M-I2C1onbfYxCG6mRJE" 
geocoder = GoogleV3(api_key=api_key)


def addressToPAR(address):
    '''
    Returns corresponding Parliamentary Constituency code for an address
    '''
    constituency_code= False
    geocode = geocoder.geocode(address)
    reversed_geocode = geocode[1][::-1]
    PARs = requests.get('http://mapit.sinarproject.org/areas/PAR')
    if PARs.ok:
        PARs_json = PARs.json()
    else:
        print(r.content)

    loc = '{},{}'.format(reversed_geocode[0],reversed_geocode[1])
    areas = requests.get('http://mapit.sinarproject.org/point/4326/' + loc)
    areas_json = areas.json()
    PAR_set = set(areas_json).intersection(set(PARs_json))
    if PAR_set:
        PAR = PAR_set.pop()
        constituency_code = PARs_json[PAR]['codes']['code']
    return constituency_code
    
def dateRangeMP_raw(members, start_date, end_date):
    '''
    Returns raw member JSON for MPs between start and end date
    '''
    MP_dateRange = []
    start_datetime = parser.parse(start_date)
    end_datetime = parser.parse(end_date)
    
    for member in members:
        
        if member['start_date']:
            if member['end_date']: #has end date, ex member
                memStart = parser.parse(member['start_date'])
                memEnd = parser.parse(member['end_date'])   
                if memStart >= start_datetime and memEnd <= end_datetime:
                    MP_dateRange.append(member)
            else: 
                memStart = parser.parse(member['start_date'])
                if memStart >= start_datetime and memStart<= end_datetime:
                    MP_dateRange.append(member)
    
    return MP_dateRange
     
def currentMP_raw(members, start_date):
    '''
    Returns raw member JSON for current MP
    '''
    for member in members:
        if member['start_date']:
            start_datetime = parser.parse(member['start_date'])
            if not member['end_date'] and start_datetime >= start_datetime:
                return member
        
@hug.get(examples='base_url=http://api.popit.sinarproject.org/&constituency_code=P104&start_date=2013-04-03&end_date=2017')
@hug.local()           
def MP_const(base_url: hug.types.text, constituency_code: hug.types.text, start_date: hug.types.text, end_date: hug.types.text):
    '''
    Returns raw JSON of MP details for a constituency code
    '''    
    posts = requests.get(base_url+'/en/search/posts?q=area.identifier:"' + constituency_code + '"')
    members = posts.json()['results'][0]['memberships']
    
    MP = dateRangeMP_raw(members, start_date, end_date)
                
    return MP

@hug.get(examples='base_url=http://api.popit.sinarproject.org/&constituency_code=P104&start_date=2013-04-03')
@hug.local()           
def currentMP_const(base_url: hug.types.text, constituency_code: hug.types.text, start_date: hug.types.text):
    '''
    Return current MP details by parliamentary constituency area code
    '''    
    posts = requests.get(base_url+'/en/search/posts?q=area.identifier:"' + constituency_code + '"')
    members = posts.json()['results'][0]['memberships']
   
    currentMP = currentMP_raw(members, start_date)        
    return currentMP

#RFC 3986, no comma in text field; treated as delimiter.
@hug.get(examples='base_url=http://api.popit.sinarproject.org/&address=Jalan SS15/4G Subang Jaya Selangor&start_date=2013-04-03&end_date=2017')
@hug.local()           
def MP_geoloc(base_url: hug.types.text, address: hug.types.text, start_date: hug.types.text, end_date: hug.types.text):
    '''
    Return MP details by geolocation between start and end dates
    '''    
    MP = None
    constituency_code = addressToPAR(address) 
    if constituency_code:
        MP = MP_const(base_url, constituency_code, start_date, end_date)
    
    return MP
    
@hug.get(examples='base_url=http://api.popit.sinarproject.org/&address=Jalan SS15/4G Subang Jaya Selangor&start_date=2013-04-03') 
@hug.local()           
def currentMP_geoloc(base_url:hug.types.text, address: hug.types.text, start_date: hug.types.text):
    '''
    Return current MP person ID by geolocation
    '''    
    currentMP = None
    constituency_code = addressToPAR(address)
    if constituency_code:
        currentMP = currentMP_const(base_url, constituency_code, start_date)
    
    return currentMP

