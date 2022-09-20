======================
check_ntp_reachability
======================

--------------
About The Role
--------------

An Ansible role that will check if the time is synchronised with the NTP servers.
The role fails, if the time is not NTP synchronised and prints NTP servers which
chrony is trying to synchronise with. This role is recommended to run, if the
``Undercloud`` deployment fails on NTP synchronisation task.

Requirements
============

This role runs on ``Undercloud``.

License
=======

Apache

Author Information
==================

Red Hat TripleO Validations Team

.. ansibleautoplugin::
   :role: roles/check_ntp_reachability
