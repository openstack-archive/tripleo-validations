========================
overcloud_service_status
========================

--------------
About The Role
--------------

An Ansible role to verify the ``Overcloud`` services states after a deployment
or an update. It checks the ``API /os-services`` and looks for deprecated
services (``nova-consoleauth``) or any down services.

Requirements
============

This role needs to be run on an ``Undercloud`` with a deployed ``Overcloud``.

Dependencies
============

No dependencies.

Example Playbook
================

.. code-block:: yaml

   - hosts: undercloud
     roles:
       - { role: overcloud_service_status }

License
=======

Apache

Author Information
==================

**Red Hat TripleO DFG:Compute Squad:Deployment**

----------------
Full Description
----------------

.. ansibleautoplugin::
   :role: roles/overcloud_service_status

