=========================
check_for_dangling_images
=========================

--------------
About the role
--------------

Ansible role to check for dangling images

Requirements
============

This role will be executed pre Update.

Dependencies
============

No Dependencies

Example Playbook
================

.. code-block:: yaml

    - hosts: servers
      roles:
        - { role: check_for_dangling_images, check_for_dangling_images_debug: true }

License
=======

Apache

Author Information
==================

**Red Hat TripleO DFG:Upgrades**

----------------
Full Description
----------------

.. ansibleautoplugin::
  :role: roles/check_for_dangling_images
