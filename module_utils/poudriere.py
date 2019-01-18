# -*- coding: utf-8 -*-

# Copyright: (c) 2018, KIKUCHI Koichiro <koichiro@hataki.jp>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


import re

from ansible.module_utils.basic import AnsibleModule

class Poudriere():
    def __init__(self, module):
        '''
        '''
        self.module = module
        self.executable = module.params['executable']
        self.global_opts = '-N'
        self.headers = []
        self.command = None
        # TODO: check existence of executable here

        etcdir = module.params['etcdir']

        if etcdir:
            # TODO: check existence of etcdir here
            self.global_opts += '-e ' + etcdir


    def run_command(self, args, err_msg=None, allow_fail=False):
        '''
        wrapper of AnsibleModule#run_command
        '''
        (rc, out, err) = self.module.run_command(self.make_command_line(args))
        if not allow_fail and rc != 0:
            if err_msg is None:
                err_msg = 'failed to execute poudriere'
                if self.command is not None:
                    err_msg += ' ' + self.command
            self.module.fail_json(rc=rc,stdout=out,stderr=err,msg=msg,command=cmd)
        return (rc, out, err)

    def make_command_line(self, args):
        '''
        :args: string or list of string
        '''
        if type(args) is list:
            args = ' '.join(args)
        return "{} {} {} {}".format(self.executable,self.global_opts,self.command,args)

    def extract_list_output(self, output, matcher=None):
        '''
        1st line is treated as header and used to determine length of each field. 
        matcher is a list or tuple  [field_number, expected_str]
        '''
        lines = output.splitlines()

        if len(lines) < 2:
            return None

        begs = [ x.start() for x in re.finditer(r'[^ ]+', lines[0]) ]

        result = []

        for l in lines[1:]:
            fields = [ l[b:e].strip() for b,e in zip(begs,begs[1:] + [len(l)]) ]
            if matcher and fields[matcher[0]] == matcher[1]:
                return fields
            result.append(fields)

        return None if matcher else result


class PoudriereModule(AnsibleModule):
    def __init__(self, argument_spec, **kwargs):
        common_args_spec = dict(
            executable=dict(type='path',default='/usr/local/bin/poudriere'),
            etcdir=dict(type='path',default=None),
        )
        common_args_spec.update(argument_spec)

        super(PoudriereModule, self).__init__(argument_spec=common_args_spec, **kwargs)
