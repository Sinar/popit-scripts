import requests
import pandas

def end_cabinet(org_id):
    r = \
    requests.get('http://api.popit.sinarproject.org/en/organizations/55b72847916cff2b6d55ab7f')
    members = r.json()['result']['memberships']

    for member in members:
        print member['id']

def import_cabinet(filename):
    df = pandas.DataFrame.from_csv(filename)
    cabinet = df.to_dict(orient='records') 
    
    for minister in cabinet:
        print minister['name']

import_cabinet('data/6th-najib-cabinet.csv')
