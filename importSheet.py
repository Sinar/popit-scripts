#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 23 01:58:36 2017

@author: kay-wong
"""

from __future__ import print_function
import httplib2, os, sys, argparse
import pandas as pd 

from apiclient import discovery
import gSheet_credentials


def importGSheetAsDF(spreadsheetId, sheetName):
    '''
    Imports Google sheet as a dataframe
    Returns:
        df: dataframe of GSheet
        
    '''
    credentials = gSheet_credentials.get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discoveryUrl)

    #Get header row
    rangeName = sheetName+'!1:1'
    colNames = service.spreadsheets().values().get(
        spreadsheetId=spreadsheetId, range=rangeName, majorDimension= "ROWS").execute()
    colNames = colNames.get('values', [])[0]
    
    #Append placeholder end row to mark end of table as SheetsV4 omits empty trailing rows/columns
    placeholderVals = [['-']*len(colNames)]
    valInput_body={"majorDimension": "ROWS",
     "values": placeholderVals}
    rangeName = sheetName
    writeResult = service.spreadsheets().values().append(spreadsheetId=spreadsheetId, range=rangeName, 
            valueInputOption='RAW', body = valInput_body).execute()   
    
    #Store range of placeholder row to be removed later
    updatedRange = writeResult['updates']['updatedRange']
    
    #Get col data
    tableRange = sheetName+'!A2:AG'
    result = service.spreadsheets().values().get(
         spreadsheetId=spreadsheetId, range=tableRange, majorDimension= "COLUMNS").execute()
    colVals = result['values']

    #Remove placeholder end row
    emptyRow = [['']*len(colNames)]
    valInput_body['values'] = emptyRow
    writeResult = service.spreadsheets().values().update(spreadsheetId=spreadsheetId, range=updatedRange, 
            valueInputOption='RAW', body = valInput_body).execute() 
    
    #Create df out of colNames and colVals
    dic = dict((kvPair[0], kvPair[1]) for kvPair in zip(colNames, colVals))
    df = pd.DataFrame.from_dict(dic, orient = 'columns')
    df = df[:-1]
    
    return df



def sheetChanges(spreadsheetId, latestSheet, controlSheet, classID):
    '''
    Get rows with difference between 2 sheets
    Returns:
        df_changes: dataframe of changed rows
        
    '''
    df_latest = importGSheetAsDF(spreadsheetId, latestSheet)
    df_control = importGSheetAsDF(spreadsheetId, controlSheet)
    
     #Sort by memID so all new entries are at the top
    df_latest = df_latest.sort_values(by=classID, axis=0)
    df_control = df_control.sort_values(by=classID, axis=0)
    #Get new entries
    nDiff = len(df_latest)- len(df_control)
    df_added = df_latest[:nDiff]
    #Get updated entries
    df_latest = df_latest[nDiff:]
    df_updated=  df_latest[(df_control != df_latest).sum(axis = 1) >0]
    
    df_changes = df_updated.append(df_added, ignore_index= True)
    return df_changes

    
    


'''   
if __name__ == '__main__':
    #Example
    spreadsheetId = '1D5U8O9QXpMlteMIzqRpzIH45Ac0zabCmSmaH5uRII98'
    #df = importGSheetAsDF(spreadsheetId, sheetName)
    latestSheet = 'Sheet2'
    controlSheet = 'Sheet1'
    df = sheetChanges(spreadsheetId, latestSheet, controlSheet, 'membership_id')
    
'''

