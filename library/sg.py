#!/usr/bin/python

import re

from string import *
from ansible.module_utils.basic import *

def runCommand(cmd,isCheck=False):
    (rc, out, err) = module.run_command(cmd)
    if not rc:
        module.log("OK " + cmd)
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

def createSg(gname):
    (rc, out, err) = runCommand('%s storagegroup -list -gname %s' % (naviseccli, gname),True)
    if rc != 0:
        (rc, out, err) = runCommand('%s storagegroup -create -gname %s' % (naviseccli, gname))
        return 1
    else:
        return 0

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
            gname = dict(required=True),
        ),
    )
    nscli = module.params['nscli']
    user = module.params['user']
    password = module.params['password']
    spa = module.params['spa']
    spb = module.params['spb']
    gname = module.params['gname']

    ### Set Global Variable naviseccli
    global naviseccli
    naviseccli = getNaviseccliCommand(nscli,user,password,spa,spb)

    ### Create Storage Group
    rc = createSg(gname)
    if rc:
        res_args = dict(
            changed = True
        )
        module.exit_json(**res_args)
    else:
        res_args = dict(
            changed = False
        )
        module.exit_json(**res_args)

if __name__ == '__main__':
    main()
