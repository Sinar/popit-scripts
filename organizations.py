# Initial script to import, update popit organization csv template
# input 
# TODO
# CLI options 
# --import/--update <filename>
# --export
# --verbose
# --dry-run
# token
# api url

import pandas
import requests

#store key in token.txt Don't commit this file
key = open('token.txt')
token = 'Token '+key.read().rstrip()

headers = {'Authorization': token }

df = pandas.read_csv('organizations.csv', header=0, index_col=False)
df = df.where((pandas.notnull(df)),None)

organizations = df.to_dict(orient='records')

def import_orgs():
    for org in organizations:
       
        if org['identifier']:
            org['identifiers'] = [
                {'identifier':org['identifier'],'scheme':org['scheme'],}
                ]
        del org['identifier']
        del org['scheme']

        contact_details = []

        if org['contact_voice']:
            contact_details.append(
                [
                {'type':'voice','value':org['contact_voice']},
                ])

        if org['contact_address']:
            contact_details.append(
                [
                {'type':'address','value':org['contact_address']},
                ])

        if org['contact_email']:
            contact_details.append(
                [
                {'type':'email','value':org['contact_email']},
                ])


        del org['contact_voice']
        del org['contact_address']
        del org['contact_email']

        if org['link_url']:
            org['links'] = [{'url':org['link_url']},]
            if org['link_note']:
                org['links'].append({'note':org['link_note']})

        del org['link_url']
        del org['link_note']

        print org

import_orgs()
