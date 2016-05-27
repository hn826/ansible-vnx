#!/usr/bin/python

from ansible.module_utils.basic import *


def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(required=False),
        )
    )
    args = module.params

    name = args.get('name') or 'World'
    message = 'Hello, {name}'.format(name=name)

    module.exit_json(message=message, changed=False)


if __name__ == '__main__':
    main()
