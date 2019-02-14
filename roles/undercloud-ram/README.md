Undercloud-ram
==============

An Ansible role to check if the Undercloud fits the RAM requirements

Requirements
------------

This role could be used before or/and after the Undercloud installation

Role Variables
--------------

- min_undercloud_ram_gb: <24> -- Minimal amount of RAM in GB

Dependencies
------------

No dependencies.

Example Playbook
----------------

    - hosts: undercloud
      roles:
         - { role: undercloud-ram, min_undercloud_ram_gb: 24 }

License
-------

Apache

Author Information
------------------

Red Hat TripleO Validations Team
