Ansible Modules for poudriere
=========

Ansible modules for [poudriere](https://github.com/freebsd/poudriere)

Requirements
------------

* Ansible >= TBD
* poudriere

Installation and use
----------------

```
$ ansible-galaxy install koichirok.poudriere_modules
```

Once installed, use the modules in playbook or role:

```yaml
- name: Load modules
  roles:
     - koichirok.poudriere_modules
  tasks:
    ...
```

Modules
-------

see python scripts under the [library](/library) directory.

License
-------

GPLv3
