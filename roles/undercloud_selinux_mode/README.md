Undercloud-selinux-mode
=======================

An Ansible role to check the Undercloud SELinux Enforcing mode


Requirements
------------

This role could be used before or/and after the Undercloud installation

Role Variables
--------------

None

Dependencies
------------

No dependencies.

Example Playbook
----------------

    - hosts: undercloud
      roles:
         - { role: undercloud-selinux-mode }

License
-------

Apache

Author Information
------------------

Red Hat TripleO Validations Team
