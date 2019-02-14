Role Name
=========

An Ansible roles to check for potential issues with Neutron's configuration

Requirements
------------

This role needs an installed and working Undercloud

Role Variables
--------------

- configs: A list of Neutron configuration files and directories that will be
  passed to the Neutron services. The order is important here, the values in
  later files take precedence.

Dependencies
------------

No dependencies.

Example Playbook
----------------

    - hosts: undercloud
      roles:
         - { role: undercloud-neutron-sanity-check }

License
-------

Apache

Author Information
------------------

Red Hat TripleO Validations Team
