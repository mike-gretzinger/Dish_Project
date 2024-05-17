def parseArgs():
    parser = argparse.ArgumentParser(description='Create a Velocity CSV Report on tests with Callback URLS (run from AWS)')
    parser.add_argument('-hr','--hours', type=int, default=24, help='Number of hours back from NOW to get results')
    parser.add_argument('-u','--url', type=str, default='https://localhost:8443', help='Velocity URL')
    parser.add_argument('-0','--output', type=str, default='c:/temp/Results.csv', help='File to write')
    return(vars(parser.parse_args()))

import argparse
import json
import re
import time
import logging
import requests
import csv
import datetime
from dateutil import tz

from requests.auth import HTTPBasicAuth
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# do arguments
args = parseArgs()
args['url'] = 'https://localhost:8443'

# login to Velocity get token
token_resp = requests.get(args['url']+'/velocity/api/auth/v2/token', auth=HTTPBasicAuth('aws_velocity','Spirent01'), verify=False)
token = json.loads(token_resp.text)['token']

# set headers
headers = {"Content-Type": "application/json; charset=utf-8", "X-Auth-Token": token}

# get current time
time_resp = requests.get(args['url']+'/velocity/api/util/v3/time', headers=headers, verify=False)
curr_time = json.loads(time_resp.text)['time']

# get timestamp for range
prev_time = curr_time - (args['hours']*60*60*1000)

# hard code topos and runlist to monitor for now
topos = ['D-E1-IN-001_TS6','D-E1-IN-001_TS3']
runlist = 'main/_runlists/5GC-End-to-End.vrl'

# prep for loop
result_list = []

# loop on each topo
print('Working')
    
# itialize looping vars
remaining = 1
start = 0
    
#loop on remaining tests
while remaining > 0:
    url = args['url']+'/ito/executions/v1/executions?limit=200&offset='+str(start)+'&filter=endTime:gt:'+str(prev_time)
    #url = args['url']+'/ito/executions/v1/executions?limit=200&offset='+str(start)+'&filter=endTime:gt:'+str(prev_time)+'&runlistPath::'+runlist+'&topologyName::'+topo+'&executionState::COMPLETED&filter=result:!:CANCEL'
    info_resp = requests.get(url, headers=headers, verify=False)
    info = json.loads(info_resp.text)
    start = start + info['count']
    remaining = info['total'] - start
    print('remaining = '+str(remaining)+', start = '+str(start)+', total = '+str(info['total']))
    for i in range(0, info['count']):
        # only post results if there is a callback (that means AWS triggered it)
        if 'callbackURL' in info['content'][i] and info['content'][i]['runlistPath'] == 'main/_runlists/5GC-End-to-End.vrl' and 'td_postTestResultsS3Demo' not in info['content'][i]['testPath']:
            result_list.append([datetime.datetime.fromtimestamp(info['content'][i]['startTime']/1000).strftime('%Y-%m-%d %H:%M:%S'),re.split('/|\.',info['content'][i]['testPath'])[-2],info['content'][i]['topologyName'],info['content'][i]['result']])
 
rows = sorted(result_list, key=lambda d: d[0])
print('Sending info to file: '+args['output'])
fields = ['UTC', 'Test Case','Topology','Result']
with open(args['output'], 'w', newline="") as csvfile: 
    # creating a csv writer object 
    csvwriter = csv.writer(csvfile) 
    # writing the fields 
    csvwriter.writerow(fields)         
    # writing the data rows 
    csvwriter.writerows(rows)
