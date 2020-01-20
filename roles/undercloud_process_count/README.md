Role Name
=========

An Ansible role to check the number of OpenStack processes on the Undercloud

Requirements
------------

This role requires an installed and working Undercloud


Role Variables
--------------

- max_process_count: <'8'> -- Maximum number of process

Dependencies
------------

No dependencies.

Example Playbook
----------------

    - hosts: servers
      roles:
         - { role: undercloud-process-count }

License
-------

Apache

Author Information
------------------

Red Hat TripleO Validations Team
