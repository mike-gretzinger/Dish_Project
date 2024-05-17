def parseArgs():
    parser = argparse.ArgumentParser(description='Query Velocity for CURRENT Agent Usage and Append Results to File')
    parser.add_argument('-u','--url', type=str, default='https://10.245.0.191', help='Velocity URL')
    parser.add_argument('-0','--output', type=str, default='./Agent_Usage.csv', help='File to write')
    return(vars(parser.parse_args()))

import argparse
import json
import re
import time
import logging
import requests
import csv
import datetime

from requests.auth import HTTPBasicAuth
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# do arguments
args = parseArgs()

#temp
#args = {}
#args['url']= 'https://localhost:8443'

# login to Velocity get token
token_resp = requests.get(args['url']+'/velocity/api/auth/v2/token', auth=HTTPBasicAuth('aws_velocity','Spirent01'), verify=False)
token = json.loads(token_resp.text)['token']

# set headers
headers = {"Content-Type": "application/json; charset=utf-8", "X-Auth-Token": token}

# get current time
time_resp = requests.get(args['url']+'/velocity/api/util/v3/time', headers=headers, verify=False)
curr_time = json.loads(time_resp.text)['time']

# get current agent usage
curr_usage = requests.get(args['url']+'/ito/executions/v1/agents', headers=headers, verify=False)
curr_usage = json.loads(curr_usage.text)

agents_in_use = 0

for i in curr_usage:
    print(i['status']+ " "+ str(i['enabled']))
    if i['enabled'] == True and i['status'] == 'BUSY':
       agents_in_use+=1
print(datetime.datetime.fromtimestamp(curr_time/1000).strftime('%Y-%m-%d %H:%M:%S')+','+str(agents_in_use))
f = open(args['output'], 'a', newline="")
f.write(datetime.datetime.fromtimestamp(curr_time/1000).strftime('%Y-%m-%d %H:%M:%S')+','+str(agents_in_use)+'\n')
f.close


