
#############################################################
# Author : Sanka Dayananda
# Version : 1.0.0
# Purpose : Restart and print status on trigger
#############################################################

import boto3
import paramiko

def rexec_handler(event, context):
    host = event['ip']
    keydir = event['keydir']
    keyfile =  event['keyfile']
    keyfpath = '/tmp/'+keyfile
    luser = event['luser']

    s3_client = boto3.client('s3')
    s3_client.download_file(keydir, keyfile, keyfpath)

    keyf = paramiko.RSAKey.from_private_key_file(keyfpath)
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    print "Connecting to : " + host
    client.connect( hostname = host, username = luser, pkey = keyf )
    print "Connected to : " + host

    commands = [
        "sudo /usr/bin/systemctl stop httpd",
        "touch /tmp/web_stopped",
        "sudo /usr/bin/systemctl start httpd",
        "touch /tmp/web_started",
        "sudo /usr/bin/systemctl status httpd"
        ]
    for command in commands:
        print "Executing {}".format(command)
        stdin , stdout, stderr = client.exec_command(command)
        mstdout = stdout.read()
        mstderr = stderr.read()
        
        if len(mstdout) != 0:
            print mstdout
        if len(mstderr) != 0:
            print mstderr

    client.close()

    return
    {
        'message' : "Script execution completed"
    }



