#!/usr/bin/python

import commands
import re

from string import *
from ansible.module_utils.basic import *

def checkSp(user,password,spa,spb):
    naviseccli_path = "/opt/Navisphere/bin/naviseccli"
    (rc, out, err) = module.run_command('%s -user %s -password %s -address %s -scope 0 getarrayuid' % (naviseccli_path, user, password, spa))
    if rc == 0:
        return spa
    else:
        return spb

def createSg(gname):
    (rc, out, err) = module.run_command('%s storagegroup -list -gname %s' % (naviseccli, gname))
    if rc != 0:
        (rc, out, err) = module.run_command('%s storagegroup -create -gname %s' % (naviseccli, gname), check_rc=True)
        return 1
    else:
        return 0

def main():
    ### Parse Arguments
    global module
    module = AnsibleModule(
        argument_spec = dict(
            user = dict(required=True),
            password = dict(required=True),
            spa = dict(required=True),
            spb = dict(required=True),
            gname = dict(required=True),
        ),
    )
    user = module.params['user']
    password = module.params['password']
    spa = module.params['spa']
    spb = module.params['spb']
    gname = module.params['gname']

    ### Check SP
    address = checkSp(user,password,spa,spb) 

    ### Set Global Variable naviseccli
    global naviseccli
    naviseccli = "/opt/Navisphere/bin/naviseccli -user " + user + " -password " + password + " -address " + address + " -scope 0"

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
