from unittest.test import test_break
def parseArgs():
    parser = argparse.ArgumentParser(description='Execute a runlist')
    parser.add_argument('-p','--phone', type=str, default='+15059539970', help='Phone number or public/private username')
    parser.add_argument('-s','--supi', type=str, default='313340999978850', help='SUPI (15 digits)')
    parser.add_argument('-i','--imei', type=str, default='35829866031900', help='IMEI (14 digits)')
    parser.add_argument('-r','--runlist', type=str, default='BSS-OSS.vrl', help='Name of the runlist in Velocity (always ends in .vrl)')
    parser.add_argument('-to','--topology', type=str, default='D-W2-IN-001_TS1', help='Topology name in Velocity')
    parser.add_argument('-u','--url', type=str, default='https://localhost:8443', help='Velocity URL')
    parser.add_argument('-ti','--timeout', type=int, default=10, help='Timeout in minutes')
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

from requests.auth import HTTPBasicAuth
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# do arguments
args = parseArgs()
print("Triggering Velocity Runlist "+args['runlist']+" on topology "+args['topology'])

# login to Velocity get token
token_resp = requests.get(args['url']+'/velocity/api/auth/v2/token', auth=HTTPBasicAuth('aws_velocity','Spirent01'), verify=False)
token = json.loads(token_resp.text)['token']

# set headers
headers = {"Content-Type": "application/json; charset=utf-8", "X-Auth-Token": token}

# get current time
time_resp = requests.get(args['url']+'/velocity/api/util/v3/time', headers=headers, verify=False)
curr_time = json.loads(time_resp.text)['time']

# get topology ID
url = args['url']+'/velocity/api/topology/v16/topologies?filter=name::'+args['topology']
topo_resp = requests.get(url, headers=headers, verify=False)
topo_dict = json.loads(topo_resp.text)
pprint.pprint(topo_dict)

# get runlist json
url = args['url']+'/ito/repository/v2/repository/main/_runlists/'+args['runlist']
runlist_resp = requests.get(url, headers=headers, verify=False)
runlist_dict = json.loads(runlist_resp.text)

# add phone numer and supi to runlist as parameters
runlist_dict['general']['parameters'] = [{"name": "supi","value": args['supi'],"type": "text"},{"name": "phone","value": args['phone'],"type": "text"},{"name": "imei","value": args['imei'],"type": "text"}]
runlist_dict['general']['topologyId'] = topo_dict['topologies'][0]['id']
pprint.pprint(runlist_dict)

# add callback info
runlist_dict['general']['callbackURL'] = 'https://this_will_fail.com/dummy'

# trigger execution
url = args['url']+'/ito/executions/v1/runlists/main/_runlists/'+args['runlist']
runlist_json = json.dumps(runlist_dict)
runlist_resp = requests.post(url, headers=headers, verify=False, data=runlist_json)
runlist_dict = json.loads(runlist_resp.text)
#print('________ RUN RESPONSE ________')
pprint.pprint(runlist_dict)

# wait some time
time.sleep(5)

 
# check execution for status
url = args['url']+'/ito/executions/v1/executions?filter=runlistGuid::'+runlist_dict['guid']
exec_resp = requests.get(url, headers=headers, verify=False)
exec_dict = json.loads(exec_resp.text)
#print('________ EXEC RESPONSE ________')
#pprint.pprint(exec_dict)
 
# check execution for status in loop
timeout = args['timeout']*60
start_time = time.time()
url = args['url']+'/ito/executions/v1/runlists/summary'
runlist = json.dumps([runlist_dict['guid']])
while True:
    # if timeout, abort test
    if time.time() - start_time >= timeout:
        print('Timeout failure, canceling execution')
        url = args['url']+'/ito/executions/v1/runlists/'+runlist_dict['guid']
        exec_resp = requests.delete(url, headers=headers, verify=False)
        # pprint.pprint(json.loads(exec_resp.text))
        break

    # wait 5 sec
    time.sleep(5)
    
    #get info about runlist, check if complete
    exec_resp = requests.post(url, headers=headers, verify=False, data=runlist)
    exec_dict = json.loads(exec_resp.text)[0]
    print("Working test " + str(len(exec_dict['executions'])) + " of " + str(exec_dict['itemCount']), end = '\r')
    #print("Working test " + str(len(exec_dict['executions'])) + " of " + str(exec_dict['itemCount']))
    #print(exec_dict['executions'])
    if exec_dict['endTime'] != 0:
        print()
        print('Tests Complete')
        for i in range(0,len(exec_dict['executions'])):
            print()
            print('  Test: ' + exec_dict['executions'][i]['testPath'].split('/')[-1])
            print('    Result: ' + exec_dict['executions'][i]['result'])
        break

