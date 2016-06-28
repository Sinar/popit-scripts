import requests
import pandas
from fuzzywuzzy import fuzz

base_url = 'http://api.popit.sinarproject.org'
lang = 'en'

def search_person(name):
    #returns first match result if any
    search_url = base_url + '/' + lang + "/" + "search/persons?q=" + name 
    print search_url
    r = requests.get(search_url)
    print 
    persons = r.json()['results']
  
    if persons:
        
       scores = [[ fuzz.token_set_ratio(name,person['name']), person] \
                for person in persons ]
    else:
        return None

    return scores



