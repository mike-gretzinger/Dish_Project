from unittest.test import test_break
def parseArgs():
    parser = argparse.ArgumentParser(description='Execute a Test Case')
    parser.add_argument('-p','--phone', type=str, default='+15059539970', help='Phone number or public/private username')
    parser.add_argument('-s','--supi', type=str, default='313340999978850', help='SUPI (15 digits)')
    parser.add_argument('-i','--imei', type=str, default='35829866031900', help='IMEI (14 digits)')
    parser.add_argument('-t','--testcase', type=str, default='5GC/ai_Dish_Production/DISH_5G/test_cases_BSS/Data_BSS_OSS.fftc', help='Full name with path of test case')
    parser.add_argument('-pa','--parameterFile', type=str, default='5GC/ai_Dish_Production/DISH_5G/test_cases_BSS/Data_BSS_OSS.ffpt', help='Full name with path of parameter file')
    parser.add_argument('-to','--topology', type=str, default='D-W2-IN-001_TS1', help='Topology name in Velocity')
    parser.add_argument('-u','--url', type=str, default='https://localhost:8443', help='Velocity URL')
    parser.add_argument('-ti','--timeout', type=int, default=3, help='Timeout in minutes')
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
import pprint

from requests.auth import HTTPBasicAuth
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# do arguments
args = parseArgs()
print("Triggering Velocity Test Case "+args['testcase']+" on topology "+args['topology'])

#pprint.pprint(args)

# login to Velocity get token
token_resp = requests.get(args['url']+'/velocity/api/auth/v2/token', auth=HTTPBasicAuth('bss-oss','Spirent01'), verify=False)
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
#pprint.pprint(topo_dict)

# create execution dict te
exec_dict = {'testPath':args['testcase'],'topologyId':topo_dict['topologies'][0]['id'],'parameterFilePath':args['parameterFile']}

# add phone numer and supi to parameters
exec_dict['parametersList'] = [{"name": "supi","value": args['supi'],"type": "text"},{"name": "phone","value": args['phone'],"type": "text"},{"name": "imei","value": args['imei'],"type": "text"}]
#pprint.pprint(exec_dict)

# trigger execution
url = args['url']+'/ito/executions/v1/executions'
exec_json = json.dumps(exec_dict)
exec_resp = requests.post(url, headers=headers, verify=False, data=exec_json)
exec_resp_dict = json.loads(exec_resp.text)
#print('________ RUN RESPONSE ________')
#pprint.pprint(exec_resp_dict)

# wait some time
time.sleep(5)

 
# check execution for status
url = args['url']+'/ito/executions/v1/executions/'+exec_resp_dict['executionID']
exec_resp = requests.get(url, headers=headers, verify=False)
exec_dict = json.loads(exec_resp.text)
#print('________ EXEC RESPONSE ________')
#pprint.pprint(exec_dict)

# check execution for status in loop
timeout = args['timeout']*60
start_time = time.time()
url = args['url']+'/ito/executions/v1/executions/'+exec_resp_dict['executionID']
while True:
    # if timeout, abort test
    if time.time() - start_time >= timeout:
        print('Timeout failure, canceling execution')
        url = args['url']+'/ito/executions/v1/executions/'+exec_resp_dict['executionID']
        exec_resp = requests.delete(url, headers=headers, verify=False)
        pprint.pprint(json.loads(exec_resp.text))
        break

    # wait 5 sec
    time.sleep(5)
    
    #get info about execution, check if complete
    exec_resp = requests.get(url, headers=headers, verify=False)
    exec_dict = json.loads(exec_resp.text)
    print("                            ", end = '\r')
    print('Test State: '+exec_dict['executionState'], end = '\r')
    if exec_dict['endTime'] != 0:
        print()
        print('Tests Result: '+exec_dict['result'])
        url = args['url']+'/ito/reporting/v1/reports/'+exec_resp_dict['executionID']
        print('Gathering Sample Test results')
        print('Basic Report Data: '+url)
        print('---------------------------------------------------------------------------------------------------------')
        rep_resp = requests.get(url, headers=headers, verify=False)
        pprint.pprint(json.loads(rep_resp.text))
        url = args['url']+'/ito/reporting/v1/reports/'+exec_resp_dict['executionID']+'/extdata'
        print()
        print('Extracted Data: '+url)
        print('---------------------------------------------------------------------------------------------------------')
        rep_resp = requests.get(url, headers=headers, verify=False)
        pprint.pprint(json.loads(rep_resp.text))
        break

