Repos
==============

An Ansible role to check the correctness of nova-libvirt version.

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
         - role: nova_libvirt

    - hosts: overcloud
      roles:
         - role: nova_libvirt

License
-------

Apache

Author Information
------------------

Red Hat TripleO Validations Team
