from unittest.test import test_break
def parseArgs():
    parser = argparse.ArgumentParser(description='Get runlist tests')
    parser.add_argument('-r','--runlist', type=str, default='5GC-End-to-End.vrl', help='Name of the runlist in Velocity (always ends in .vrl)')
    parser.add_argument('-u','--url', type=str, default='https://localhost:8443', help='Velocity URL')
    parser.add_argument('-p','--output_path', type=str, default='/temp', help='Output directory')
    return(vars(parser.parse_args()))

import argparse
import json
import re
import time
import logging
import requests
import datetime
from dateutil import tz
import pprint
import pandas as pd

from requests.auth import HTTPBasicAuth
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# do arguments
args = parseArgs()
print("Reading Velocity Runlist "+args['runlist'])
pprint.pprint(args)

# login to Velocity get token
token_resp = requests.get(args['url']+'/velocity/api/auth/v2/token', auth=HTTPBasicAuth('aws_velocity','Spirent01'), verify=False)
token = json.loads(token_resp.text)['token']

# set headers
headers = {"Content-Type": "application/json; charset=utf-8", "X-Auth-Token": token}

# get current time
time_resp = requests.get(args['url']+'/velocity/api/util/v3/time', headers=headers, verify=False)
curr_time = json.loads(time_resp.text)['time']

# get runlist json
url = args['url']+'/ito/repository/v2/repository/main/_runlists/'+args['runlist']
runlist_resp = requests.get(url, headers=headers, verify=False)
runlist_dict = json.loads(runlist_resp.text)
#pprint.pprint(runlist_dict)

# open output file
f = open(args['output_path']+'/'+args['runlist'].split('.')[0]+'.csv', "w")
f.write('Full,File,Path'+'\n')

# output loop
for item_dict in runlist_dict['main']['items']:
    f.write(','.join([item_dict['path'],item_dict['path'].split('/')[-1],'/'.join(item_dict['path'].split('/')[0:-1])])+'\n')

f.close

