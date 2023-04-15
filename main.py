#!/usr/bin/env python3
import requests
from requests.auth import HTTPBasicAuth
import json
import logging
import time
import sys

## Initialising logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

## Jira API token and username
api_username = "" #"<user name of admin>" # pending implementation of vault
api_token = "" #"<api_token>" # pending implementation of vault

##receiving fields from subprocess
emailAddress = sys.argv[1]
groupName = sys.argv[2]

## Adding authentication
auth = HTTPBasicAuth(api_username,api_token)
accountId = ''

## Adding basic URLs
baseurl = "" #"base url https"  #update base url of you jira project here
USER_URL =  ''.join([baseurl,'rest/api/2/user'])
GROUP_URL = ''.join([baseurl,'rest/api/2/group/user'])




## creating user header
USER_HEADER = {
    "Accept": "application/json",
   "Content-Type": "application/json"
}

USER_PAYLOAD = json.dumps( {
  "emailAddress": emailAddress
} )

#Adding user in Atlassian
try:
   response = requests.request(
    "POST",
    USER_URL,
    data=USER_PAYLOAD,
    headers=USER_HEADER,
    auth=auth
    )
   logger.info(response)
   response = response.text.replace("\"active\": true", "\"active\": \"true\"")
   accountId = json.loads(response).get("accountId")
   logger.info("User created with email address " + json.loads(USER_PAYLOAD).get('emailAddress') + " and accountId " + str(accountId))
   
except Exception as err:
   logger.error(err) 





## Removing Default Groups for user
delete_group_queries =[{
    'groupname' : 'jira-workmanagement-users-46labs',
    'accountId' : accountId
    },
    {
    'groupname' : 'confluence-users-46labs',
    'accountId' : accountId
    },
    {
    'groupname' : 'jira-servicemanagement-users-46labs',
    'accountId' : accountId
    },
    {
    'groupname' : 'opsgenie-users',
    'accountId' : accountId
    }
    ]



time.sleep(15)
#loop to delete groups
for query in delete_group_queries:
    try:
       if(accountId is not None):
          response = requests.request(
             "DELETE",
             GROUP_URL,
             params=query,
             auth=auth
             )
          logger.info(response)
          logger.info("User with accountId " + accountId + " deleted from group  " + str(query.get('groupname')))
    except Exception as err:
      logger.error(err) 
    

## add group for user
add_group_queries ={
    "groupname" : groupName
}
    

add_group_payload = json.dumps({
   "accountId": accountId
})

try:
    
    response = requests.post(
    GROUP_URL,
    data=add_group_payload,
    headers=USER_HEADER,
    params=add_group_queries,
    auth=auth
    )
    logger.info(response)
    logger.info("User with accountId " + accountId + " added to group  " + str(add_group_queries.get('groupname'))) # type: ignore
except Exception as err:
   logger.error(err)
