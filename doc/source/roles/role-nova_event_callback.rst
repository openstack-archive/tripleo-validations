===================
nova_event_callback
===================

--------------
About the role
--------------

An Ansible role to check if the **Nova** ``auth_url`` in **Neutron** is
configured correctly on the **Overcloud Controller(s)**.

Requirements
============

None.

Dependencies
============

None.

Example Playbook
================

.. code-block:: yaml

   - hosts: Controller
     vars:
       neutron_config_file: /path/to/neutron.conf
     roles:
       - nova_event_callback

License
=======

Apache

Author Information
==================

**Red Hat TripleO DFG:Compute Deployment Squad**

----------------
Full Description
----------------

.. ansibleautoplugin::
   :role: roles/nova_event_callback

