import requests
import pandas

import utils

#store key in token.txt Don't commit this file
key = open('token.txt')
token = 'Token '+key.read().rstrip()

headers = {'Authorization': token }
