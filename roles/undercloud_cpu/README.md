Undercloud-cpu
==============

An Ansible role to check if the Undercloud fits the CPU core requirements

Requirements
------------

This role could be used before or/and after the Undercloud installation.

Role Variables
--------------

- min_undercloud_cpu_count: <8> -- Minimal number of CPU core

Dependencies
------------

No dependencies.

Example Playbook
----------------

    - hosts: undercloud
      roles:
         - { role: undercloud-cpu, min_undercloud_cpu_count: 42 }

License
-------

Apache 2.0

Author Information
------------------

Red Hat TripleO Validations Team
