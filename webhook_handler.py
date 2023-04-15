#!/usr/bin/env python3
import io
import json
import subprocess
import re
import logging
import uwsgi
def application(env, start_response):
    ## Initialising logger
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    group_mapping = {
        "Carrier-Support (CS)" : "01 CRS-CS-PortalAccess",
        "Direct-Support (CS)" : "02 EDEC-CS-PortalAccess",
        "NEC-Support (CS)" : "03 NEC-CS-PortalAccess",
        "SwitchRay Support (CS)" : "04 SRS-CS-PortalAccess",
        "T-Mobile Insource (CS)" : "05 TMI-CS-PortalAccess",
        "T-Mobile Support (CS)" : "06 TMOB-CS-PortalAccess",
    }
    try:
        content_length = int(env.get('CONTENT_LENGTH', 0))
        webhook_data = env['wsgi.input'].read(content_length)
        webhook_dict = json.loads(webhook_data)
        
        ##extracting email and group from payload
        emailAddress =  webhook_dict["issue"]["fields"]["summary"]
        if not is_valid_email(emailAddress):
            # Return a 400 Bad Request response
            status = '400 Bad Request'
            message = 'Invalid request data'
            response_headers = [('Content-type', 'text/plain')]
            start_response(status, response_headers)
            return [message.encode()]
        projectName = webhook_dict["issue"]["fields"]["customfield_10133"]["value"]
        groupToAdd = str(group_mapping.get(projectName))
        uwsgi.log("Creating user with email: {}".format(str(emailAddress)))
        logging.info("Creating User with email: {}".format(str(emailAddress)))

        #passing parameters to execute script for adding user in Jira
        subprocess.run(["python3","./main.py",emailAddress,groupToAdd])
        start_response('200 OK', [('Content-Type','text/html')])
        message = "Successfully executed the script"
        return [message.encode()]
    except Exception as e:
        logging.error("Error: {}".format(str(e)))
        uwsgi.log("Error: {}".format(str(e)))
        start_response("500 Internal Server Error", [('Content-Type', 'text/plain')])
        return ["Internal Server Error".encode('utf-8')]

def is_valid_email(email):
    """
    Check if email is a valid email address
    """
    # Regular expression for validating an email address
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    # Use re.match() to check if email matches the pattern
    if re.match(pattern, email):
        return True
    else:
        return False
