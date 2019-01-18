#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2018, KIKUCHI Koichiro <koichiro@hataki.jp>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: poudriere_ports
short_description: TBD
description:
    - TBD
version_added: "2.7"
author:
    - KIKUCHI Koichiro (@koichirok)
'''

EXAMPLES = '''
TBD
'''

RETURN = '''
---
TBD
'''

from ansible.module_utils.poudriere import Poudriere
from ansible.module_utils.poudriere import PoudriereModule
from ansible.module_utils.six import iteritems

BOOL_PARAM_ARG_MAP = dict(
    allow_failures='-k',
    leave_jail='-I',
    build_repository='-N',
    custom_prefix='-P',
    skip_recursive_rebuild='-S',
    save_wrkdir='-w',
    verbose='-v',
    debug='-v -v',
)

class PoudriereTestport(Poudriere):
    """
    Class corresponding to poudriere's testport command.
    """
 
    def __init__(self, module):
        super(PoudriereTestport, self).__init__(module)
        self.command = 'testport'

    def run_module(self):
        '''
        Do `poudriere testport' operation.
        '''
        params = self.module.params
        args = ['-j', params['jail']]
        if params['build_name']:
            args += ['-B', params['build_name']]
        if params['jobs']:
            args += ['-J', params['jobs']]
        if params['ports']:
            args += ['-p', params['ports']]
        if params['set']:
            args += ['-z', params['set']]
        for param,arg in iteritems(BOOL_PARAM_ARG_MAP):
            if params[param] != self.module.argument_spec[param]['default']:
                args.append(arg)
        # dry-run for check_mode
        if self.module.check_mode:
            args.append('-n')

        args.append(params['origin'])

        rc, out, err = self.run_command(args, err_msg="failed to execute poudriere testport for " + params['origin'])

        self.module.exit_json(changed=True,rc=rc,stdout=out,stderr=err)

def main():
    module = PoudriereModule(
        dict(
            jail=dict(type='str',required=True),
            origin=dict(type='str',required=True,aliases=['name']),
            build_name=dict(type='str',default=None), 
            jobs=dict(type='str',default=None), 
            allow_failures=dict(type='bool',default=False),
            leave_jail=dict(type='bool',default=False),
            build_repository=dict(type='bool',default=True), 
            ports=dict(type='str',default=None), # or 'default'
            custom_prefix=dict(type='bool',default=False),
            skip_recursive_rebuild=dict(type='bool',default=False),
            save_wrkdir=dict(type='bool',default=False),
            set=dict(type='str',default=None),
            verbose=dict(type='bool',default=False),
            debug=dict(type='bool',default=False),
        ),
        supports_check_mode=True # use dry-run for check
    )
    PoudriereTestport(module).run_module()


if __name__ == '__main__':
    main()
