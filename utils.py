import requests
import pandas
from fuzzywuzzy import fuzz

base_url = 'http://api.popit.sinarproject.org'
lang = 'en'

def search_person(name,lang='en'):
    #returns first match result if any
    search_url = base_url + '/' + lang + "/" + "search/persons?q=name:" + name 
    r = requests.get(search_url)
    persons = r.json()['results']
  
    if persons:
        return persons[0]

    else:
        return None

def search_organization(name,lang='en'):
    #return first match result if any
    search_url = base_url + '/' + lang + "/" + "search/organizations?q=name:" + name 

    r = requests.get(search_url)
    organizations = r.json()['results']

    if organizations:
        return organizations[0]

    else:
        return None

def search_party(name,lang='en'):
    #search political party uses acronyms which are more accurate
    #acronym lookup table is a good idea here

    search_url = base_url + '/' + lang + "/" + "search/organizations?q=other_names.name:" + name 

    r = requests.get(search_url)
    party = r.json()['results'][0]

    if party:
        return party
    else:
        return None

def memberships(person_id):
    r = requests.get(base_url + '/en/search/memberships?q=person_id:' + person_id)
    memberships = r.json()['results']

    if memberships:
        return memberships
    else:
        return None

