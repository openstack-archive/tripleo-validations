Undercloud-heat-purge-deleted
=============================

An Ansible role to check if `heat-manage purge_deleted` is enabled in the
crontab

Requirements
------------

This role requires an installed and working Undercloud.

Role Variables
--------------

- cron_check: <'heat-manage purge_deleted'> -- String to check in the crontab

Dependencies
------------

No dependencies.

Example Playbook
----------------


    - hosts: undercloud
      roles:
         - { role: undercloud-heat-purge-deleted }

License
-------

Apache

Author Information
------------------

Red Hat TripleO Validations Team
