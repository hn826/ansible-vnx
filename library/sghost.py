#!/usr/bin/python

import re

from string import *
from ansible.module_utils.basic import *

def runCommand(cmd):
    (rc, out, err) = module.run_command(cmd)
    if not rc:
        module.log("OK " + cmd)
        return (rc, out, err)
    else:
        module.log("FAILED " + cmd + " " + out)
        module.fail_json(msg="FAILED " + cmd + " " + out)

def checkSp(nscli,user,password,spa,spb):
    (rc, out, err) = runCommand('%s -user %s -password %s -address %s -scope 0 getarrayuid' % (nscli, user, password, spa))
    if rc == 0:
        return spa
    else:
        return spb

def getNaviseccliCommand(nscli,user,password,spa,spb):
    return ('%s -user %s -password %s -address %s -scope 0' % (nscli, user, password, checkSp(nscli,user,password,spa,spb)))

def getHosts(gname):
    (rc, out, err) = runCommand('%s storagegroup -list -gname %s -host' % (naviseccli, gname))
    retlist = []
    for l in re.split(r'\n', out):
        if re.search(r'^Host name.*', l):
            x=re.search(r'^Host name.*', l).group().split(" ")
            retlist.append(x[-1])
    return list(set(retlist))

def getMaintainHosts(query,gname):
    pairs = getHosts(gname)
    maintainlist = []
    for i in query:
        for j in pairs:
            if i == j:
                maintainlist.append(j)
    return maintainlist

def parseQuery(query):
    return re.split(r':', query)

def removeHosts(query,gname):
    removelist = list(set(getHosts(gname)) - set(getMaintainHosts(query,gname)))
    if not removelist:
        return 0

    for i in removelist:
        (rc, out, err) = runCommand('%s storagegroup -disconnecthost -gname %s -hosts %s -o' % (naviseccli, gname, i))

    return 1

def addHosts(query,gname):
    addlist = filter(lambda s:s != '', list(set(query) - set(getMaintainHosts(query,gname))))
    if not addlist:
        return 0

    for i in addlist:
        if i != "":
            (rc, out, err) = runCommand('%s storagegroup -connecthost -gname %s -hosts %s -o' % (naviseccli, gname, i))
    return 1

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
            query = dict(required=True),
            gname = dict(required=True),
            noremove = dict(default=False, required=False, type='bool')
        ),
    )
    nscli = module.params['nscli']
    user = module.params['user']
    password = module.params['password']
    spa = module.params['spa']
    spb = module.params['spb']
    query = module.params['query']
    gname = module.params['gname']
    noremove = module.params['noremove']

    ### Set Global Variable naviseccli
    global naviseccli
    naviseccli = getNaviseccliCommand(nscli,user,password,spa,spb)

    rc = 0

    ### Remove Phase
    if not noremove:
        rc += removeHosts(parseQuery(query),gname)

    ### Add Phase
    rc += addHosts(parseQuery(query),gname)

    if rc:
        res_args = dict(
            changed = True, pair = getHosts(gname)
        )
        module.exit_json(**res_args)
    else:
        res_args = dict(
            changed = False, pair = getHosts(gname)
        )
        module.exit_json(**res_args)

if __name__ == '__main__':
    main()
