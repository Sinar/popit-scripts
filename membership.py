# generate CSV of membership of organisations

import pandas
import requests

def membership_export():
    org_id = '5362fcc219ee29270d8a9e22'

    r = requests.get('https://api.popit.sinarproject.org/en/search/memberships/' +
            '?q=organization_id:' + org_id)

    pages = r.json()['page']

    memberships = []

    for page in range(1,pages+1):
        r = requests.get(
                'http://api.popit.sinarproject.org/en/search/memberships/' +
                '?q=organization_id:' + org_id+'&page=' + str(page))

        for membership in r.json()['results']:
            memberships.append(membership)


    df_memberships = pandas.DataFrame.from_dict(memberships,orient='columns')
    df_persons = pandas.DataFrame.from_dict(df_memberships['person'].to_dict(),orient='index')
    df_post = pandas.DataFrame.from_dict(df_memberships['post'].to_dict(),orient='index')


    #Drop misc columns
    df_memberships.drop(
            ['created_at', 'updated_at', 'language_code',
             'contact_details',
             'member','member_id','person','organization',
             ], axis=1, inplace= True)
    df_persons.drop(['created_at', 'updated_at', 'language_code', 'id'], axis=1, inplace= True)

    #Only drop columns where all values are NA.
    #df_memberships.dropna(axis = 1, how = 'all', inplace= True)

    df_persons.columns = ['person_'+colName for colName in df_persons.columns] 
    #df_post.columns = ['post_'+colName for colName in df_post.columns] 

    df_memberships = df_memberships.join(df_persons['person_name'], how = 'outer')
    #need to join post_label if it exists

    df_memberships.to_csv('memberships.csv',index=False,encoding='utf-8',columns=[
        'person_name',
        'role',
        'start_date',
        'end_date',
        'person_id',
        'organization_id',
        'post_id',
        'id',
        ])

def membership_update():
    df = pandas.DataFrame.from_csv('memberships.csv')
    df = df.where((pandas.notnull(df)), None)
    memberships = df.to_dict(orient='records')

#membership_export()
