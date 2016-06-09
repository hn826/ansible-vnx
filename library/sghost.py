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

def getPairs(gname):
    (rc, out, err) = module.run_command('%s storagegroup -list -gname %s -host' % (naviseccli, gname), check_rc=True)
    retlist = []
    for l in re.split(r'\n', out):
        if re.search(r'^Host name.*', l):
            x=re.search(r'^Host name.*', l).group().split(" ")
            retlist.append(x[-1])
    return list(set(retlist))

def getMaintainPairs(query,gname):
    pairs = getPairs(gname)
    maintainlist = []
    for i in query:
        for j in pairs:
            if i == j:
                maintainlist.append(j)
    return maintainlist

def parseQuery(query):
    return re.split(r':', query)

def removeHlus(query,gname):
    removelist = list(set(getPairs(gname)) - set(getMaintainPairs(query,gname)))
    if not removelist:
        return 0

    for i in removelist:
        (rc, out, err) = module.run_command('%s storagegroup -disconnecthost -gname %s -hosts %s -o' % (naviseccli, gname, i), check_rc=True)

    return 1

def addHlus(query,gname):
    addlist = filter(lambda s:s != '', list(set(query) - set(getMaintainPairs(query,gname))))
    if not addlist:
        return 0

    for i in addlist:
        if i != "":
            (rc, out, err) = module.run_command('%s storagegroup -connecthost -gname %s -hosts %s -o' % (naviseccli, gname, i), check_rc=True)
    return 1

def main():
    ### Parse Arguments
    global module
    module = AnsibleModule(
        argument_spec = dict(
            user = dict(required=True),
            password = dict(required=True),
            spa = dict(required=True),
            spb = dict(required=True),
            query = dict(required=True),
            gname = dict(required=True),
            noremove = dict(default=False, required=False, type='bool')
        ),
    )
    user = module.params['user']
    password = module.params['password']
    spa = module.params['spa']
    spb = module.params['spb']
    query = module.params['query']
    gname = module.params['gname']
    noremove = module.params['noremove']

    ### Check SP
    address = checkSp(user,password,spa,spb) 

    ### Set Global Variable naviseccli
    global naviseccli
    naviseccli = "/opt/Navisphere/bin/naviseccli -user " + user + " -password " + password + " -address " + address + " -scope 0"

    rc = 0

    ### Remove Phase
    if not noremove:
        rc += removeHlus(parseQuery(query),gname)

    ### Add Phase
    rc += addHlus(parseQuery(query),gname)

    if rc:
        res_args = dict(
            changed = True, pair = getPairs(gname)
        )
        module.exit_json(**res_args)
    else:
        res_args = dict(
            changed = False, pair = getPairs(gname)
        )
        module.exit_json(**res_args)

if __name__ == '__main__':
    main()
