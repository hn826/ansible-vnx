#!/usr/bin/python

import datetime

from ansible.module_utils.basic import *


def main():
    module = AnsibleModule(
        argument_spec=dict()
    )

    date = str(datetime.datetime.now())

    module.exit_json(date=date, changed=False)


if __name__ == '__main__':
    main()
