Repos
==============

An Ansible role to check the correctness of current repositories.

Requirements
------------

This role could be used before/after an Undercloud or an Overcloud has been
deployed.

Role Variables
--------------

- None

Dependencies
------------

No dependencies.

Example Playbook
----------------

    - hosts: undercloud
      roles:
         - role: repos

    - hosts: overcloud
      roles:
         - role: repos

License
-------

Apache

Author Information
------------------

Red Hat TripleO Validations Team
