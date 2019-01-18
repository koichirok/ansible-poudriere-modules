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

class PoudrierePorts(Poudriere):

    def __init__(self, module):
        super(PoudrierePorts, self).__init__(module)
        self.command = 'ports'
        self.state = self.module.params['state']
        self.name = self.module.params['name']
        self.method = self.module.params['method']
        self.url = self.module.params['url']
        self.branch = self.module.params['branch']
        self.path = self.module.params['path']
        self.unregister_only = self.module.params['unregister_only']

    def get_info(self):
        (rc, out, err) = self.run_command('-l', allow_fail=True)

        # rc == 70 when no ports is exist
        if rc not in [0, 70]:
            self.module.fail_json(rc=rc,stdout=out,stderr=err,msg="Error occurred while executing module")

        info = self.extract_list_output(out,(0, self.name))

        if info:
            return dict(name=info[0], method=info[1], timestamp=info[2], path=info[3])

        return None

    def run_module(self):
        '''
        Do `poudriere ports' operation.
        currently "update ports tree (-u)" operation is not supported
        '''
        
        info = self.get_info()
        result = dict(changed=True)

        if self.state == 'absent':
            # delete ports tree
            if info is None:
                self.module.exit_json(changed=False, msg="ports `{}' not exists.".format(self.name))

            result = dict(changed=True, ports_tree=info)

            if self.module.check_mode:
                result['msg'] = "ports `{}' will be removed.".format(self.name)
                self.module.exit_json(**result)

            # build arguments
            args = ['-d', self.name]

            if self.unregister_only:
                args.append('-k')
                
            (rc, out, err) = self.run_command(args, err_msg="failed to delete ports: " + self.name)
            result.update(dict(rc=rc,stdout=out,stderr=err,
                               msg="ports `{}' successfully removed.".format(self.name)))
            self.module.exit_json(**result)

        elif self.state == 'present':
            # create ports
            '''
            currently unsupported options for creating/updating ports tree:

                -F            -- When used with -c, only create the needed filesystems
                                 (for ZFS) and directories, but do not populate them.
                -f filesystem -- The name of the filesystem to create for the ports tree.
                                 If 'none' then do not create the filesystem.  The default
                                 is: 'poudriere/ports/default'.
            '''
            if info:
                self.module.exit_json(changed=False, ports_tree=info,
                                      msg="ports `{}' already exists.".format(self.name))

            if self.module.check_mode:
                self.module.exit_json(changed=True, msg="ports `{}' will be created.".format(self.name))

            # build arguments
            args = ['-c', self.name, '-m', self.method]
            if self.url:
                args += ['-U', self.url]
            if self.path:
                args += ['-M', self.path]
            if self.branch: # and (self.method == 'git' or self.method.startswith('svn')):
                args += ['-B', self.branch]

            (rc, out, err) = self.run_command(args, err_msg="failed to create ports: " + self.name)

            self.module.exit_json(changed=True,rc=rc,stdout=out,stderr=err,ports_tree=self.get_info(),
                                  msg="ports `{}' successfully created.".format(self.name))
        else: 
            # update ports (state=latest), not implemented
            self.module.fail_json(msg='unreached here')


def main():
    module = PoudriereModule(
        dict(
            state=dict(default='present',choices=['present','absent']), # 'latest']),
            branch=dict(type='str',default=None),
            name=dict(default='default'),
            method=dict(default='portsnap',choices=['git','null','portsnap','svn','svn+http',
                                                     'svn+https','svn+file','svn+ssh']),
            url=dict(type='str',default=None),
            path=dict(type='path',default=None),
            unregister_only=dict(default=False),
        ),
        supports_check_mode=True
    )
    PoudrierePorts(module).run_module()


if __name__ == '__main__':
    main()
