import pyeapi
import paramiko
import getpass
import sys
import os
import scp
import select
import re
import ssl
import pexpect
import time
import argparse
ssl._create_default_https_context = ssl._create_unverified_context

parser = argparse.ArgumentParser()
parser.add_argument("-i", help="Enter input file path")
args=parser.parse_args()

file_switches = args.i

list_root_configured = []
list_root_notconfigured=[]

i=1
switches = []

with open(file_switches) as readfile:
    for line in readfile:
        switches.append(line.strip())
# Get the username and password to connect to switches

username = raw_input("Enter your username: ")
password = getpass.getpass("Enter your password: ")

rootpassword = getpass.getpass("Enter Root password: ")

for switch in switches:
    result = ""
    while True:
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(switch,22,username,password,look_for_keys=False, allow_agent=False)
            print "Connected to %s" % switch
            break
        except paramiko.AuthenticationException:
            print "Authentication failed when connecting to %s" % switch
            sys.exit(1)
        except:
            print "Could not SSH to %s, waiting for it to start" % switch
            i += 1
            time.sleep(2)
        if i == 5:
            print "Could not connect to %s." % switch
            sys.exit(1)

    stdin, stdout, stderr = ssh.exec_command("enable \n show run sec aaa root secret")

# Wait for the command to terminate
    while not stdout.channel.exit_status_ready():
    # Only print data if there is data to read in the channel
        if stdout.channel.recv_ready():
            rl, wl, xl = select.select([stdout.channel], [], [], 0.0)
            if len(rl) > 0:
                result = stdout.channel.recv(1024)


    searchRoot = re.search(r'xxx command',result,re.I)
    if(searchRoot):
        list_root_configured.append(switch)
    else:
        list_root_notconfigured.append(switch)

if(list_root_configured):
    print "Root Configured for following switches"
    for sw in list_root_configured:
        print sw
    userInput1 = raw_input("Do you want to change root password for these switches y or n: ")
    if(userInput1 == "y"):
        for switch in list_root_configured:
            while True:
                try:
                    ssh = paramiko.SSHClient()
                    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    ssh.connect(switch,22,username,password,look_for_keys=False, allow_agent=False)
                    print "Connected to %s" % switch
                    break
                except paramiko.AuthenticationException:
                    print "Authentication failed when connecting to %s" % switch
                    sys.exit(1)
                except:
                    print "Could not SSH to %s, waiting for it to start" % switch
                    i += 1
                    time.sleep(2)
                if i == 5:
                    print "Could not connect to %s." % switch
                    sys.exit(1)

            stdin, stdout, stderr = ssh.exec_command("enable \n configure terminal \n aaa root secret "+rootpassword)

            while not stdout.channel.exit_status_ready():
                time.sleep(1)
            print "Root password changed for switch "+switch
            ssh.close()



if(list_root_notconfigured):
    print "Root Not Configured for following switches"
    for sw in list_root_notconfigured:
        print sw
    userInput2 = raw_input("Do you want to configure root for these switches y or n: ")
    if(userInput2 == "y"):
        for switch in list_root_notconfigured:
            while True:
                try:
                    ssh = paramiko.SSHClient()
                    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    ssh.connect(switch,22,username,password,look_for_keys=False, allow_agent=False)
                    print "Connected to %s" % switch
                    break
                except paramiko.AuthenticationException:
                    print "Authentication failed when connecting to %s" % switch
                    sys.exit(1)
                except:
                    print "Could not SSH to %s, waiting for it to start" % switch
                    i += 1
                    time.sleep(2)
                if i == 5:
                    print "Could not connect to %s." % switch
                    sys.exit(1)
        
            stdin, stdout, stderr = ssh.exec_command("enable \n configure terminal \n aaa root secret "+rootpassword)
            
            while not stdout.channel.exit_status_ready():
                time.sleep(1)
            print "Root password configured for switch "+switch
        ssh.close()





