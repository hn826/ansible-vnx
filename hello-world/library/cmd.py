#!/usr/bin/python

import datetime
import commands
import re
import pexpect

from string import *
from ansible.module_utils.basic import *

def getrgluns():
    getlun = commands.getoutput(naviseccli + " getlun -name")
    getunusedluns = commands.getoutput(naviseccli + " getunusedluns | sed '/^$/d' | grep -v \"RAID GROUP:\"")

    ret = ""

    for name in re.split(r'\n', getunusedluns):
        if re.search('.*\n.*' + name, getlun): 
            ret = ret + re.search('^LOGICAL.*$', re.search('.*\n.*' + name, getlun).group(), re.M).group() + '\n'

    return re.split(r'\n', re.sub('LOGICAL UNIT NUMBER ' , '', ret.rstrip('\n')))

def getspluns():
    lunlist = commands.getoutput(naviseccli + " lun -list -featureData | grep -B 2 N/A | grep \"LOGICAL UNIT NUMBER\"")

    return re.split(r'\n', re.sub('LOGICAL UNIT NUMBER ' , '', lunlist.rstrip('\n')))

def addhlus(num):
    unuseluns = getrgluns() + getspluns()
   
    hlumax = int(commands.getoutput(naviseccli + " storagegroup -list -gname TestMaskingSG | grep '^    ' | awk '{print $1}' | sort | sed -n '$p'") or -1)    

    for i in xrange(hlumax + 1, hlumax + num + 1):
        commands.getoutput(naviseccli + " storagegroup -addhlu -gname TestMaskingSG -alu " + unuseluns[i - (hlumax + 1)] + " -hlu " + str(i) + "")

def removehlus():
    hlulist = re.split(r'\n', commands.getoutput(naviseccli + " storagegroup -list -gname TestMaskingSG | grep '^    ' | awk '{print $1}'").rstrip('\n'))

#    for i in hlulist:
#    rmhlu = pexpect.spawn (naviseccli + " storagegroup -removehlu -gname TestMaskingSG -hlu 0")
#    rmhlu.expect (r"Remove .*")
#    rmhlu.sendline ("y\n")
#    rmhlu.close
#    commands.getoutput(naviseccli + " storagegroup -removehlu -gname TestMaskingSG -hlu " + str(i))

def main():
    module = AnsibleModule(
        argument_spec = dict(
            user = dict(required=True),
            password = dict(required=True),
            address = dict(required=True),
            num = dict(required=False),
        ),
    )
    user = module.params['user']
    password = module.params['password']
    address = module.params['address']
    num = module.params['num']

    global naviseccli
    naviseccli = "/opt/Navisphere/bin/naviseccli -user " + user + " -password " + password + " -address " + address + " -scope 0"

#    if num is None:
#    removehlus()
#    else:
    addhlus(int(num))

    stdout = ""

    for i in getrgluns():
        stdout = stdout + i + '\n'
    for i in getspluns():
        stdout = stdout + i + '\n'

    res_args = dict(
        user = user, password = password, changed = True, stdout = stdout
    )
    module.exit_json(**res_args)

if __name__ == '__main__':
    main()
