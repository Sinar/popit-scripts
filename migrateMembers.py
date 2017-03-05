#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  2 07:11:08 2017

@author: metamatical
"""

import csv, requests, re, sys

base_url = "http://api.popit.sinarproject.org"
token = open('token.txt')
headers = {'Authorization': token.read().rstrip()}

            

def flatten_contacts(contacts):
    dic = {'twitter': '', 'email': '', 'cell': '', 'voice': '', 'fax': '', 'address': ''}
    for i in range(len(contacts)):
     
        c = contacts[i]
        dic[c['type']] = c['value']  

    return dic
        
 
def generateMP_csv():
    '''Generate CSV with all current Dewan Rakyat members'''
    
    errorLog = open("errorLog.txt", 'w+') 
    mp_csv = csv.writer(open("currentMP.csv", "w"))
    mp_csv.writerow(['person_id', 'person_name', 'person_summary', 'image', 'contact_twitter', 'contact_email', 'contact_cell', 'contact_voice', 'contact_fax', 'contact_address'])
    dewanRakyatOrgID = "53633b5a19ee29270d8a9ecf"
    url = base_url+ "/en/organizations/" + dewanRakyatOrgID + "/?minify=True"
    #url = "https://sinar-malaysia.popit.mysociety.org/api/v0.1/organizations/53633b5a19ee29270d8a9ecf"
    r = requests.get(url).json()['result']
    memberships = r['memberships']
    
    for membership_id in memberships:
        #try: 
        url = base_url+ "/en/memberships/"+ membership_id
        r = requests.get(url).json()['result']
        
        try:
            end_date = r['end_date'] or r['post']['end_date'] #take from any which isn't null
        except TypeError:
            end_date = r['end_date']
        
        if end_date: #has end date, ex member
            pass    
        else: #current member

            try:
                personName= r['person']['name']
            except (TypeError, KeyError):
                personName = None
            
            try:
                personSmmry= r['person']['summary']
            except (TypeError, KeyError):
                personDesc = None
                
            try:
                personImage = r['person']['image']
            except (TypeError, KeyError):
                personImage = None
         
            dic = {'twitter': '', 'email': '', 'cell': '', 'voice': '', 'fax': '', 'address': ''}
            if r['person']['contact_details']:
                 contacts = r['person']['contact_details']
                 for i in range(len(contacts)):
                    c = contacts[i]
                    dic[c['type']] = c['value']  
        
            mp_csv.writerow([r['person_id'], personName, personSmmry, personImage, dic['twitter'], dic['email'], dic['cell'], dic['voice'], dic['fax'], dic['address']])    
            
        '''
        except:
            errorLog.write(membership_id)
            print(membership_id)
            e = sys.exc_info()[0]
            print(e)
            errorLog.write(str(e) + "\n")
        '''
            
    
def generate_csv(org_id, org_name, membershipID_list):
    '''
    Generate CSV of members for org
    '''
    
    errorLog = open("errorLog.txt", 'w+') 
    csvName = "members_" + "_".join(org_name.split(" ")) + ".csv"
    org_csv = csv.writer(open('organization_memberships/'+ csvName, "w"))
    #Write header
    org_csv.writerow(['membership_id', 'person_id', 'person_name', 'post_id', 'post,role', 'start_date', 'source url', 'end_date' , 'source_url'])


    errorLog.write("==================\n"+str(org_name))
    for membership_id in membershipID_list:
        try: 
            url = base_url+ "/en/memberships/"+ membership_id
            r = requests.get(url).json()['result']
            
            try:
                postrole = r['role'] or r['post']['role']
            except TypeError:
                postrole = r['role']
            
            try:
                personName= r['person']['name']
            except (TypeError, KeyError):
                personName = None
                
                
            org_csv.writerow([r['id'], r['person_id'], personName, r['post_id'], postrole, r['start_date'], None, r['end_date'], None])

        except:
            errorLog.write(membership_id)
            print(membership_id)
            e = sys.exc_info()[0]
            print(e)
            errorLog.write(str(e) + "\n")
        

def genOrgMembershipCSV():
    
    url = 'http://api.popit.sinarproject.org/en/organizations/?minify=True'
    r = requests.get(url).json()
    
    for org in r['results']:
        generate_csv(org['id'], org['name'], org["memberships"])
        print(str(org['name'])+ " SUCCESSFUL")

def getOrgIDs():
    '''
    Generate CSV of members for all orgs
    '''
    url = 'http://api.popit.sinarproject.org/en/organizations/?minify=True'
    hasNext = True 
    pg = 1
    
    while hasNext:
        r = requests.get(url+"&page=" + str(pg)).json()
        for org in r['results']:
            if org["memberships"]: #if organization is not memberless
                  generate_csv(org['id'], org['name'], org["memberships"])
        
        hasNext = r['next']
        
        pg +=1
        
def genAmyothaCSV():
    errorLog = open("errorLog.txt", 'w+') 
    csvName = "members_amyotha.csv"
    org_csv = csv.writer(open('organization_memberships/'+ csvName, "w"))
    
    hluttaw_base = 'http://api.openhluttaw.org/en/organizations'
    amyotha_ID = '897739b2831e41109713ac9d8a96c845'
    r = requests.get(hluttaw_base+"/"+amyotha_ID).json()
    members = r['result']['memberships']
    
    for member in members:
        try:
            start_date = member['start_date'] or member['post']['start_date'] #take from any which isn't null
        except TypeError:
            start_date = member['start_date']
  
        try:
            end_date = member['end_date'] or member['post']['end_date'] #take from any which isn't null
        except TypeError:
            end_date = member['end_date']
            
        try:
            postrole = member['role'] or member['post']['role']
        except TypeError:
            postrole = member['role']
        
        try:
            personName= member['person']['name']
        except (TypeError, KeyError):
            personName = None
            
        org_csv.writerow([member['id'], member['person_id'], personName, member['post_id'], postrole, start_date, None, end_date, None])

 
def myanmarMP_csv():
    #Generate CSV with all current Dewan Rakyat members
    errorLog = open("errorLog.txt", 'w+') 
    mp_csv = csv.writer(open("myanmarMP.csv", "w"))
    mp_csv.writerow(['person_id', 'person_name', 'person_summary', 'image', 'contact_twitter', 'contact_email', 'contact_cell', 'contact_voice', 'contact_fax', 'contact_address'])
    '''
    dewanRakyatOrgID = "53633b5a19ee29270d8a9ecf"
    url = base_url+ "/en/organizations/" + dewanRakyatOrgID + "/?minify=True"
    #url = "https://sinar-malaysia.popit.mysociety.org/api/v0.1/organizations/53633b5a19ee29270d8a9ecf"
    r = requests.get(url).json()['result']
    memberships = r['memberships']
    '''
    hluttaw_base = 'http://api.openhluttaw.org/en/organizations'
    amyotha_ID = '897739b2831e41109713ac9d8a96c845'
    r = requests.get(hluttaw_base+"/"+amyotha_ID).json()['result']
    members = r['memberships']
    
    for member in members:
        #try: 

        try:
            end_date = member['end_date'] or member['post']['end_date'] #take from any which isn't null
        except TypeError:
            end_date = member['end_date']
        
        if end_date: #has end date, ex member
            pass    
        else: #current member

            try:
                personName= member['person']['name']
            except (TypeError, KeyError):
                personName = None
            
            try:
                personSmmry= member['person']['summary']
            except (TypeError, KeyError):
                personDesc = None
                
            try:
                personImage = member['person']['image']
            except (TypeError, KeyError):
                personImage = None
         
            dic = {'twitter': '', 'email': '', 'cell': '', 'voice': '', 'fax': '', 'address': ''}
            try:
                contacts = member['person']['contact_details']
            except KeyError:
                contacts = member['contact_details']
            
            for i in range(len(contacts)):
                c = contacts[i]
                dic[c['type']] = c['value']  

            mp_csv.writerow([member['person_id'], personName, personSmmry, personImage, dic['twitter'], dic['email'], dic['cell'], dic['voice'], dic['fax'], dic['address']])    
            

'''
def flattenjson( c, delim ):
    val = {}
    for i in c.keys():
        
        if isinstance( c[i], dict ):
            get = flattenjson( c[i], delim )
            for j in get.keys():
                val[ i + delim + j ] = get[j]
        elif isinstance( c[i], list ):
            for n in range(len(c[i])):
                get = flattenjson( c[i][n], "_" )
                for j in get.keys():
                    val[ i + str(n) + delim + j ] = get[j]
        else:
            val[i] = c[i]

    return val


'''