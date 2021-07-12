===============
tripleo_haproxy
===============

--------------
About The Role
--------------

An Ansible role to check if the ``HAProxy`` configuration has recommended
values.

Requirements
============

This role requires and Up and Running Overcloud.

Dependencies
============

None.

Example Playbook
================

.. code-block:: yaml

   - hosts: undercloud
     roles:
       - { role: tripleo_haproxy }

License
=======

Apache

Author Information
==================

**Red Hat Tripleo DFG:PIDONE**

----------------
Full Description
----------------

.. ansibleautoplugin::
   :role: roles/tripleo_haproxy
