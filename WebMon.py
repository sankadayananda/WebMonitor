
#############################################################
# Author : Sanka Dayananda
# Version : 1.0.0
# Purpose : Monitor Website health and invoke another Lambda
#############################################################

import os
import boto3
import requests

def trigger_handler(event, context):
    keydir = os.environ['keydir']
    keyfile = os.environ['keyfile']
    luser = os.environ['luser']
    url = os.environ['url']
    server_ip =  os.environ['server_ip']
    worker_lambda = os.environ['worker_lambda']
    server_reigon = os.environ['server_reigon']

    client = boto3.client('lambda', region_name=server_reigon)
    try:
        r = requests.get(url, timeout=5)
        status_code = int(r.status_code)
    except requests.RequestException as e:
        print e
        status_code = 111

    if (status_code != 200 ):
        SendPayload = '{"ip":"'+server_ip+'", "keydir":"'+keydir+'", "keyfile":"'+keyfile+'", "luser":"'+luser+'"}'

        print "{url} is Down".format(url=url)
        print "Invoking worker : %s lambda on : %s " %(worker_lambda, server_ip)
        invokeResponse=client.invoke(
            FunctionName=''+worker_lambda+'',
            InvocationType='Event',
            LogType='Tail',
            Payload=SendPayload
        )
        print invokeResponse

    else:
        print "{url} is Up".format(url=url)

    return{
        'message' : "Trigger function finished"
    }
