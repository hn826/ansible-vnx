#!/usr/bin/python

import commands
import re

from string import *
from ansible.module_utils.basic import *

def getPairs(gname):
    (rc, out, err) = module.run_command('%s storagegroup -list -gname %s' % (naviseccli, gname), check_rc=True)
    retlist = []
    for l in re.split(r'\n', out):
        if re.search(r'^    .*', l):
            retlist.append(re.sub(r' +', ',', re.sub(r'    ', '', re.search(r'^    .*', l).group())))
    return retlist

def parseQuery(query):
    return re.split(r':', query)

def removeHlus(query,gname):
    for i in query:
        pairs = getPairs(gname)
        for j in pairs:
            if i != j:
                hlu = (re.split(r',' , j))[0]
                (rc, out, err) = module.run_command('%s storagegroup -removehlu -gname %s -hlu %s -o' % (naviseccli, gname, hlu), check_rc=True)

def addHlus(query,gname):
    for i in query:
        hlu = (re.split(r',' , i))[0]
        alu = (re.split(r',' , i))[1]
        (rc, out, err) = module.run_command('%s storagegroup -addhlu -gname %s -hlu %s -alu %s' % (naviseccli, gname, hlu, alu), check_rc=True)

def main():
    ### Parse Arguments
    global module
    module = AnsibleModule(
        argument_spec = dict(
            user = dict(required=True),
            password = dict(required=True),
            address = dict(required=True),
            query = dict(required=True),
            gname = dict(required=True),
            noremove = dict(default=False, required=False, type='bool')
        ),
    )
    user = module.params['user']
    password = module.params['password']
    address = module.params['address']
    query = module.params['query']
    gname = module.params['gname']
    noremove = module.params['noremove']

    ### Set Global Variable naviseccli
    global naviseccli
    naviseccli = "/opt/Navisphere/bin/naviseccli -user " + user + " -password " + password + " -address " + address + " -scope 0"

    ### Remove Phase
    if not noremove:
        removeHlus(parseQuery(query),gname)

    ### Add Phase
    addHlus(parseQuery(query),gname)

    res_args = dict(
        changed = True, pair = getPairs(gname)
    )
    module.exit_json(**res_args)

if __name__ == '__main__':
    main()
