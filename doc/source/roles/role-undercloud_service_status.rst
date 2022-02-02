=========================
undercloud_service_status
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

.. code-block:: yaml

    - hosts: undercloud
      roles:
         - { role: undercloud-service-status }

License
-------

Apache

Author Information
------------------

Red Hat TripleO Validations Team.

----------------
Full Description
----------------

.. ansibleautoplugin::
   :role: roles/undercloud_service_status
