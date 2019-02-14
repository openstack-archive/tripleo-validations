Undercloud-debug
================

An Ansible role to check if debug is enabled on Undercloud services.

Requirements
------------

This role needs to be run against an installed Undercloud.

Role Variables
--------------

- debug_check: <True>
- services_conf_files: List of path for each services configuration files you
  want to check

Dependencies
------------

- 'ini' custom plugin

Example Playbook
----------------

    - hosts: undercloud
      roles:
         - { role: undercloud-debug }

License
-------

Apache

Author Information
------------------

Red Hat TripleO Validations Team
