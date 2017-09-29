#!/usr/bin/python

import re

from string import *
from ansible.module_utils.basic import *

def runCommand(cmd,isCheck=False):
    module.log("Starting " + cmd)
    (rc, out, err) = module.run_command(cmd)
    if not rc:
        module.log("Succeeded " + cmd)
        return (rc, out, err)
    else:
        module.log("FAILED " + cmd + " " + out)
        if not isCheck:
            module.fail_json(msg="FAILED " + cmd + " " + out)
        else:
            return (rc,out,err)

def checkSp(nscli,user,password,spa,spb):
    (rc, out, err) = runCommand('%s -user %s -password %s -address %s -scope 0 getarrayuid' % (nscli, user, password, spa))
    if rc == 0:
        return spa
    else:
        return spb

def getNaviseccliCommand(nscli,user,password,spa,spb):
    return ('%s -user %s -password %s -address %s -scope 0' % (nscli, user, password, checkSp(nscli,user,password,spa,spb)))

def checkFaultslist():
    cmd='%s faults -list' % (naviseccli)
    (rc, out, err) = runCommand(cmd)
    if not re.search('The array is operating normally.', out):
        module.fail_json(msg='FAILED Faults List Check ' + cmd + ' ' + out)

def main():
    ### Parse Arguments
    global module
    module = AnsibleModule(
        argument_spec = dict(
            nscli = dict(default="/opt/Navisphere/bin/naviseccli", required=False),
            user = dict(required=True),
            password = dict(required=True),
            spa = dict(required=True),
            spb = dict(required=True),
        ),
    )
    nscli = module.params['nscli']
    user = module.params['user']
    password = module.params['password']
    spa = module.params['spa']
    spb = module.params['spb']

    ### Set Global Variable naviseccli
    global naviseccli
    naviseccli = getNaviseccliCommand(nscli,user,password,spa,spb)

    ### Check Faults List
    checkFaultslist()

    res_args = dict(
        changed = False
    )
    module.exit_json(**res_args)

if __name__ == '__main__':
    main()
