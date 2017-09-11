#!/usr/bin/env python

# AUTHOR: Created by John Singer, 2.6.15 for AirCarrier/ApplePie Airlines.
# Any usage must include give credit to the above.
#
import sys
import requests
from argparse import ArgumentParser
from time import strftime
import xml.etree.ElementTree as Et

usage = """createIEMComputerGroup.py <group name> <group filename> [options]

Create an automatic group within IBM Endpoint Manager master-actionsite for
       use in targetting fixlets

The first parameter, the desired name of the group-to-be-created
    must not currently exist within IEM

The second parameter, the name of a text file containing a
    one-computername-per-line list of IEM-managed computers to include

Options:
  --user USERNAME             IEM console-login USERNAME
                               (no default)
  --password PASSWORD         IEM console-login PASSWORD for above user
                               (no default)
  -h, --help                   Print this help message and exit

Note that without the -user USERNAME and --password PASSWORD arguments, the
IEM 'create-group' XML is generated and output to the console, but never 
invoked.

Examples:
  Create a group named PatchTuesday-2 from names in a file named 
  fromFile.txt, using the console login adminMO/adminmo.

    createIEMComputerGroup PatchTuesday-2 fromFile.txt -u adminMO -p adminmo

"""

def editTargetString(sourceStr, lookingFor, replaceStr):
    '''Replaces the lookingFor part of the sourceStr, with replaceStr'''
    newStr = sourceStr.replace(lookingFor, replaceStr)
    return newStr

# When invoked as the main program, figure out the cmdline parms, assign them to variables, handle usage & help, and go get the
#      prototype XML & names of the group-members from the cmdline filename.
if __name__ == '__main__':
    try:
        parser = ArgumentParser(add_help=False, usage=usage)
        parser.add_argument('groupname')
        parser.add_argument('filename')
        parser.add_argument('-u', '--user')
        parser.add_argument('-p', '--password')
        
        if '-h' in sys.argv or '--help' in sys.argv:
          print(usage)
          exit()
        
        args = parser.parse_args()

        if args.groupname == None or args.filename == None:
            exit(status=0)
        groupname = args.groupname
        filename = args.filename

        if args.user: user = args.user
        if args.password: password = args.password

# Using the endpoint names from the cmdline filename, substitute them into multiple copies of the
# following 'stanza', leaving result in el
        stanza = '<SearchComponentPropertyReference PropertyName="Computer Name" Comparison="Contains"><SearchText>%%computer</SearchText><Relevance>exists (computer name) whose (it as string as lowercase contains "%%computer" as lowercase)</Relevance></SearchComponentPropertyReference>'

        el = ''
        lines = [line.rstrip('\n\r').lower() for line in open(filename, 'rb')]
        for computerName in lines:
            el = el + editTargetString(stanza, '%%computer', computerName)

# With the prototype XML from the indicated file, substitute the groupname, and multiple 'stanzas', from above into the new-XML string
        with open('protoComputerGroup.xml', 'r') as f:
            basexml = f.read()
            f.close()
        newXml = editTargetString(basexml.replace('%%groupname', groupname), '%%miracle_happens_here', el)

# If there are no cmdline arguments for username/password, just output the generated XML to the console, otherwise 'push' group into IEM.
        if not args.user or not args.password:
            print( "\n", newXml )
#            outFn = 'final' + strftime("%H-%M-%S") + '.xml'
#            with open(outFn, 'w') as f:
#                f.write(newXml)
#                f.close()
            exit()

        s1a = 'adhaytem0a.'
        s1b = 'ad.'
        s2a = 'csueast'
        s2b = 'bay'
        s3 = '.edu'
        server = s1a + s1b + s2a + s2b + s3

        port = '52311'
        baseurl = 'https://' + server + ':' + port + '/api'

        r = requests.get(baseurl+'/login',verify=False,auth=(user,password))
        if r.status_code != 200:
            print( r.status_code )
            exit()

        # After logging in, issue request to create IEM computer group with indicated name/members, printing returned XML
        r = requests.post(baseurl+'/computergroups/master',verify=False,auth=(user, password), data=newXml)
        if r.status_code != 200:
            print( r.status_code )
            exit()
        else:
            print( '\nHeres the response XML about the action that I invoked: \n', r.text )

# Handle any exceptions, printing out error code
    except SystemExit:
        pass
    except:
        print("Unexpected error:", sys.exc_info()[0])
        raise
    finally:
        print("\n")
