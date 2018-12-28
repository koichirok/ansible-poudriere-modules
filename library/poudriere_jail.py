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
module: poudriere_jail
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

class PoudriereJail(Poudriere):

    def __init__(self, module):
        super(PoudriereJail, self).__init__(module)
        self.cmd.append('jail')
        self.state = module.params['state']
        # for state=present
        self.jobs = module.params['jobs']
        self.name = module.params['name']
        self.version = module.params['version']
        self.arch = module.params['arch']
        self.method = module.params['method']
        self.url = module.params['url']
        self.path = module.params['path']
        self.filesystem = module.params['filesystem']
        self.kernel = module.params['kernel']
        self.mountpoint = module.params['mountpoint']
        self.patch = module.params['patch']
        self.src_path = module.params['src_path']
        self.build_native_xtools = module.params['build_native_xtools']
        self.full_git_clone = module.params['full_git_clone']
        # for state=absent
        self.clean = module.params['clean']
        # for state=started/stopped
        self.ports = module.params['ports']
        self.set = module.params['set']


    def run_command(self, args, err_msg=None, allow_fail=False):
        msg = err_msg or "failed to execute `poudriere jail' command"
        return super(PoudriereJail, self).run_command(args, msg, allow_fail=allow_fail)


    def get_info(self):
        '''
        '''
        (rc, out, err) = self.run_command(['-i', '-j', self.name], allow_fail=True)

        if rc != 0:
            return None

        result = {}

        for l in out.splitlines():
            n, v = l.split(':',1)
            result[n] = v.strip()
            
        return result


    def run_module(self):
        '''
        Do `poudriere jail' operation.
        '''
        
        # Get all available ports trees' name
        info = self.get_info()

        if self.state == 'absent':
            # delete jail
            if info is None:
                self.module.exit_json(changed=False, msg="jail `{}' not exists.".format(self.name))

            result = dict(changed=True, jail=info)

            if self.module.check_mode:
                result['msg'] = "jail `{}' will be removed.".format(self.name)
                self.module.exit_json(**result)

            # build arguments
            args = ['-d', '-j', self.name]
            if self.clean:
                args += ['-C', self.clean]

            (rc, out, err) = self.run_command(args, err_msg="failed to delete jail: " + self.name)
            result.update(dict(rc=rc,stdout=out,stderr=err,
                               msg="ports `{}' successfully removed.".format(self.name)))
            self.module.exit_json(**result)

        elif self.state == 'present':
            # create jail
            args = ['-c', '-j', self.name, '-v', self.version, '-m', self.method]

            if self.method == 'url':
                args[-1] += '=' + self.url
            elif self.method == 'tar':
                args[-1] += '=' + self.path
            elif self.method == 'src':
                args[-1] += '=' + self.path
                args.append('-b')

            if self.jobs is not None:
                args += ['-J', str(self.jobs)]
            if self.filesystem:
                args += ['-f', self.filesystem]
            if self.kernel:
                args += ['-K', self.kernel]
            if self.arch:
                args += ['-a', self.arch]
            if self.mountpoint:
                args += ['-M', self.mountpoint]
            if self.patch:
                args += ['-P', self.patch]
            if self.src_path:
                args += ['-S', self.src_path]
            if self.build_native_xtools:
                args.append('-x')
            if self.full_git_clone:
                args.append('-D')

            if info:
                self.module.exit_json(changed=False, jail=info,
                                      msg="jail `{}' already exists.".format(self.name))
            if self.module.check_mode:
                self.module.exit_json(changed=True,
                                      msg="jail `{}' will be created.".format(self.name))
            (rc, out, err) = self.run_command(args, err_msg="failed to create ports: " + self.name)
            self.module.exit_json(changed=True, rc=rc, stdout=out, stderr=err,
                                  jail=self.get_info(),
                                  msg="ports `{}' successfully created.".format(self.name))
        elif self.state in ['started','stopped']:
            args = ['-s' if self.state == 'started' else '-k', '-j', self.name]
            if self.ports:
                args += ['-p', self.ports]
            if self.set:
                args += ['-z', self.set]
        else:
            # for Parameters `-u' (update)  and/or `-r' (rename)
            # -t version    -- Version of FreeBSD to upgrade the jail to.
            pass

        self.module.fail_json(msg='Unsupported state: ' + self.state)


def main():
    module = PoudriereModule(
        dict(
            state=dict(default='present',choices=['present','absent','started','stopped']), # 'latest', 'renamed']),
            jobs=dict(type='int',default=None),
            name=dict(required=True),
            version=dict(type='str'),
            arch=dict(type='str',default=None),
            method=dict(default='http',choices=['allbsd','ftp-archive','ftp','git','http','null',
                                                 'src','svn','svn+file','svn+http','svn+https',
                                                 'svn+ssh','tar','ur']), 
            url=dict(type='str',default=None),
            path=dict(type='path',default=None),
            filesystem=dict(type='str',default=None),
            kernel=dict(type='str',default=None),
            mountpoint=dict(type='path',default=None),
            patch=dict(type='str',default=None), # type='path'?
            src_path=dict(type='path',default=None),
            build_native_xtools=dict(default=False),
            full_git_clone=dict(default=False),
            # for state=absent (or should create 'cleaned' for this operation???)
            clean=dict(default=None,choices=['all','cache','logs','packages','wrkdirs']),
            # for state=started/stopped
            ports=dict(type='str',default=None),
            set=dict(type='str',default=None),
        ),
        required_if=[
            ('state', 'present', ['version']),
            ('method', 'tar', ['path']),
            ('method', 'src', ['path']), # can merge above???
            ('method', 'url', 'url'),
        ],
        supports_check_mode=True,
    )
    PoudriereJail(module).run_module()


if __name__ == '__main__':
    main()
