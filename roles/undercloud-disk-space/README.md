Undercloud-disk-space
=====================

An Ansible role to verify if the Undercloud fits the disk space requirements.

Requirements
------------

This role could be used before or/and after the Undercloud installation.

Role Variables
--------------

- Volumes: a dictionary of mount points and their minimum sizes

Dependencies
------------

No Dependencies

Example Playbook
----------------

    - hosts: servers
      roles:
         - { role: undercloud-disk-space}

License
-------

Apache

Author Information
------------------

Red Hat TripleO Validation Team
