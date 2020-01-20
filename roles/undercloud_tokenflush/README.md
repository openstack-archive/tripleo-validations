Undercloud-tokenflush
=====================

An Ansible role to check if `keystone-manage token_flush` is enabled for the keystone user.

Requirements
------------

This role requires an installed and working Undercloud.

Role Variables
--------------

- cron_check: <'keystone-manage token_flush'> -- the string to check in the crontab


Dependencies
------------

No dependencies.

Example Playbook
----------------

    - hosts: undercloud
      roles:
         - { role: undercloud-tokenflush }

License
-------

Apache

Author Information
------------------

Red Hat TripleO Validations Team
