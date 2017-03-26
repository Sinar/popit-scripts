#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import sys, argparse 
import pandas as pd
import numpy as np


parser = argparse.ArgumentParser(description='Update Popit DB with changes from spreadsheet')
parser.add_argument('function',  help='Function to run')
parser.add_argument('className', help= 'Name of class in sheet to sort by')
   
parser.add_argument('orgID', help='Org ID, required arg to import')
parser.add_argument('spreadsheetId', help='ID of Google spreadhseet')
parser.add_argument('latestSheet', help= 'Name of latest sheet in Google spreadsheet to update')
parser.add_argument('controlSheet', help= 'Name of sheet in Google spreadsheet to update')


if __name__ == '__main__':
    
    base_url = "http://api.popit.sinarproject.org"
    token = open('../token.txt')
    headers = {'Authorization': token.read().rstrip()}

    args, rest = parser.parse_known_args()
    
    
    if args.function=='update_changes':
        '''
            Updates Popit DB with only changed rows from the current GoogleSheet
        '''
        
        sys.argv = ['importSheet.py']
        import importSheet
        df = importSheet.sheetChanges(args.spreadsheetId, args.latestSheet, args.controlSheet, args.className+'_id')
        
        if args.className == 'membership':
            sys.argv = ['membershipsUpdate.py']
            import membershipsUpdate
            df.apply(lambda row: membershipsUpdate.genPayloads(base_url, row, args.orgID), axis=1)
        elif args.className == 'person':
            sys.argv = ['persons.py']
            import persons
            persons.personUpdate(df)
        else:
            print("Invalid class")
           
        
        
    elif args.function=='update_batch':
        '''
            Updates Popit DB with all rows of GoogleSheet
        '''
        sys.argv = ['importSheet.py']
        import importSheet
        df = importSheet.importGSheetAsDF(args.spreadsheetId, args.latestSheet)
        
         if args.className == 'membership':
            sys.argv = ['membershipsUpdate.py']
            import membershipsUpdate
            df.apply(lambda row: membershipsUpdate.genPayloads(base_url, row, args.orgID), axis=1)
        
        elif args.className == 'person':
            sys.argv = ['persons.py']
            import persons
            persons.personUpdate(df)
        else:
            print("Invalid class")
           
        
        
    else:
        print("Invalid argument")
    