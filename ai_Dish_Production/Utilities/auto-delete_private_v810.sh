#!/bin/bash
TARGETDATE=$1
HOSTNAME=$2
USERNAME=$3
PASSWORD=$4
DATE=`date  --date="$TARGETDATE days ago" +%s%N | cut -b1-13`

TOKEN=`curl -k -s -u "$USERNAME:$PASSWORD" https:/$HOSTNAME/velocity/api/auth/v2/token | grep -o '"token":"[^"]*' | cut -d'"' -f4`

echo "curl -k -s -X PUT -H \"X-Auth-Token:$TOKEN\" \"https://$HOSTNAME/ito/reporting/v1/autodelete?olderThan=$DATE\""
curl -k -s -X PUT -H "X-Auth-Token:$TOKEN" "https:/$HOSTNAME/ito/reporting/v1/autodelete?olderThan=$DATE"
