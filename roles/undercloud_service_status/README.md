Undercloud-service-status
=========================

An Ansible role to verify the Undercloud services states before running an
Update or Upgrade.

Requirements
------------

This role needs to be run against an installed Undercloud.

Role Variables
--------------

- undercloud_service_list: A list of services actually coming from the tripleo-ansible-inventory

Dependencies
------------

No dependencies.

Example Playbook
----------------


    - hosts: undercloud
      roles:
         - { role: undercloud-service-status }

License
-------

Apache

Author Information
------------------

Red Hat TripleO Validations Team.
