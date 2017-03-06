#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import requests
import re

base_url = "http://api.popit.sinarproject.org"
token = open('token.txt')
headers = {'Authorization': token.read().rstrip()}

#  =========   UTILS   =========  #

def clean(label):
    return re.sub(r'[^\w\s]', '', label.lower())


def getUsernameFromLink(linkURL):
    userName = linkURL.split(".com/")[-1]
    return userName

def twitterLinkToContact(linkURL):
    '''
    Posts Twitter link entry as contact entry
    '''
    #Obtain username from URL
    userName = getUsernameFromLink(linkURL)
    newContact = {"type": "twitter", "value": userName, "label": "Twitter"}
    return newContact

def contactToLink(c):
    '''
    Posts contact entry as link entry
    '''
    ctype= c['type']
    #Generate URL from username
    urlPrefixes = {"facebook": "https://www.facebook.com" , "twitter": "https://twitter.com"}
    noteType = {"facebook": "Official Facebook account" , "twitter": "Official Twitter account"}
    

    newURL = urlPrefixes[ctype] + "/" + c['value']
    link_contact = {"url": newURL, "note": noteType[ctype]}
    
    return link_contact


def delLinksandContacts(personID):
    
    base_url = "http://api.popit.sinarproject.org"
    token = "Token 3e6a794d84fc00dc613f40e426cbc4f19b69a68e"
    headers = {'Authorization': token}
    URL = base_url+ "/en/persons/"+ personID
    
    resp = requests.get(URL).json()
    resp= resp['result']
    if resp['links']:
        for link in resp['links']:
            url = URL +"/links/"+link['id']
            requests.delete(url, headers= headers)
    if resp['contact_details']:
        for con in resp['contact_details']:
            url = URL +"/contact_details/"+con['id']
            r = requests.delete(url, headers= headers)


def fixContactType(c):
    ''' Standardise contact type '''
    clabel = clean(c['label'])
    ctype = clean(c['type'])

    if "email" in clabel or "email" in ctype: #change type to email
        c['type'] = 'email'        
    elif "handphone" in clabel or "mobile" in clabel or "handphone" in ctype or "mobile" in ctype: #change type to cell
        c['type'] = 'cell'        
    elif "fax" in clabel or "fax" in ctype:
        c['type'] = 'fax'
    elif "phone" in clabel or "phone" in ctype:
        c['type'] = 'voice'
    elif "address" in clabel or "address" in ctype:
        c['type'] = 'address'     
    else:
        pass
    
    return c   


#  =========   MAIN   =========  #  
def missingContacts_aux(r):
    ''' Migrate missing contacts for a single page '''
    for person in r['result']:
        twitAdded = [] #Keeps track of added accounts to prevent duplication
        fbAdded = []
    
   
        if person['contact_details']:
            for contact in person['contact_details']:
                if contact['type'] == "facebook":
                    link_contact = contactToLink(contact)
                    
                    #Post new link entry for contact
                    postURL = base_url+"/en/persons/"+person['id']+ "/links"
                    r = requests.post(postURL, headers = headers, json = link_contact)
                    fbAdded.append(contact['value'])      
                    
                elif contact['type'] == "twitter":
                    
                    link_contact = contactToLink(contact)
                    #Post new link entry for contact
                    postURL = base_url+"/en/persons/"+person['id']+ "/links"
                    r = requests.post(postURL, headers = headers, json = link_contact)
                    #print(link_contact)
                    
                    #Proceed with posting contact entry
                    url = base_url+"/en/persons/"+person['id']+ "/contact_details"
                    r = requests.post(url, headers = headers, json = contact)        
                    twitAdded.append(contact['value'])
                    #print(contact)
                    
                else:            
                    contact = fixContactType(contact)
                    url = base_url+"/en/persons/"+person['id']+ "/contact_details"
                    r = requests.post(url, headers = headers, json = contact)        
                    #print(contact)
        if person['links']:
            for link in person['links']:
                if "twitter" in clean(link['note']):
                    twitContact = twitterLinkToContact(link['url'])
                    if twitContact['value'] in twitAdded:
                        pass
                    else:
                        url = base_url+"/en/persons/"+person['id']+ "/contact_details"
                        r = requests.post(url, headers = headers, json = twitContact)     
                        #print(twitContact)
                elif "facebook" in clean(link['note']):
                    if getUsernameFromLink(link['url']) in fbAdded:
                        pass
                    else:
                        url = base_url+"/en/persons/"+person['id']+ "/links"
                        r = requests.post(url, headers = headers, json = link)        
                        #print(link)                
                else:
                    url = base_url+"/en/persons/"+person['id']+ "/links"
                    
                    r = requests.post(url, headers = headers, json = link)        
                    #print r.content               


def missingContacts():
    ''' Migrate missing contacts for all pages '''
    has_more = True 
    pg = 1

    while has_more:
        print("Page: "+ str(pg)+ "\n")
        r = requests.get('https://sinar-malaysia.popit.mysociety.org/api/v0.1/persons/?page='+str(pg)).json()
        missingContacts_aux(r)
                
        has_more = r['has_more']
        pg +=1