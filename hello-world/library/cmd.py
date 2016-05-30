#!/usr/bin/python

import datetime
import commands
import re

from string import *
from ansible.module_utils.basic import *

def getrgluns(user,password,address):
    getlun = commands.getoutput("/opt/Navisphere/bin/naviseccli -user " + user + " -password " + password + " -address " + address + " -scope 0 getlun -name")
    getunusedluns = commands.getoutput("/opt/Navisphere/bin/naviseccli -user " + user + " -password " + password + " -address " + address + " -scope 0 getunusedluns | sed '/^$/d' | grep -v \"RAID GROUP:\"")

    ret = ""

    for name in re.split(r'\n', getunusedluns):
        if re.search('.*\n.*' + name, getlun): 
            ret = ret + re.search('^LOGICAL.*$', re.search('.*\n.*' + name, getlun).group(), re.M).group() + '\n'

    return re.split(r'\n', re.sub('LOGICAL UNIT NUMBER ' , '', ret.rstrip('\n')))

def getspluns(user,password,address):
    lunlist = commands.getoutput("/opt/Navisphere/bin/naviseccli -user " + user + " -password " + password + " -address " + address + " -scope 0 lun -list -featureData | grep -B 2 N/A | grep \"LOGICAL UNIT NUMBER\"")

    return re.split(r'\n', re.sub('LOGICAL UNIT NUMBER ' , '', lunlist.rstrip('\n')))

def main():
    module = AnsibleModule(
        argument_spec = dict(
            user = dict(required=True),
            password = dict(required=True),
            address = dict(required=True),
        ),
    )
    user = module.params['user']
    password = module.params['password']
    address = module.params['address']

    stdout = ""

    for i in getrgluns(user,password,address):
        stdout = stdout + i + '\n'
    for i in getspluns(user,password,address):
        stdout = stdout + i + '\n'

    res_args = dict(
        user = user, password = password, changed = True, stdout = stdout
    )
    module.exit_json(**res_args)

if __name__ == '__main__':
    main()
