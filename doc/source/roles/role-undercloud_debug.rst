================
undercloud_debug
================

--------------
About the role
--------------

An Ansible role to check if debug is enabled on Undercloud services.

Requirements
============

This role needs to be run against an installed Undercloud.
The tested services must use one of the specified configuration files
to set their debug status.

Role Variables
==============

- debug_check: <True>
- services_conf_files: List of paths for configuration files of services
  you want to check

Dependencies
============

- 'validations_read_ini' custom plugin

Example Playbook
================

.. code-block:: yaml

  - hosts: undercloud
    roles:
      - { role: undercloud-debug }

License
=======

Apache

Author Information
==================

Red Hat TripleO Validations Team

----------------
Full Description
----------------

.. ansibleautoplugin::
   :role: roles/undercloud_debug
