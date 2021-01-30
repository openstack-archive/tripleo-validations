Overcloud-service-status
=========================

An Ansible role to verify the Overcloud services states after a deployment or an update.
It checks the API /os-services and looks for deprecated services (nova-consoleauth) or
any down services.

Requirements
------------

This role needs to be run on an Undercloud with a deployed Overcloud.

Role Variables
--------------

- overcloud_service_status_debug: Wether or not to log the token request
- overcloud_deprecated_services: A list of services that shouldn't be registered any more
- overcloud_service_api: overcloud API to validate against

These variables are normally set as host variables for the undercloud when generating
the inventory with tripleo-ansible-inventory:
- overcloud_keystone_url
- overcloud_admin_password


Dependencies
------------

No dependencies.

Example Playbook
----------------


    - hosts: undercloud
      roles:
         - { role: overcloud_service_status }

License
-------

Apache

Author Information
------------------

Red Hat Nova Deployment Squad Team.
