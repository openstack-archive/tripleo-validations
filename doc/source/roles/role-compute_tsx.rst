===========
compute_tsx
===========

--------------
About The Role
--------------

An Ansible role to verify that the compute nodes have the appropriate TSX flags
before proceeding with an upgrade.

``RHEL-8.3`` kernel disabled the **Intel TSX** (Transactional Synchronization
Extensions) feature by default as a preemptive security measure, but it breaks
live migration from ``RHEL-7.9`` (or even ``RHEL-8.1`` or ``RHEL-8.2``) to
``RHEL-8.3``.

Operators are expected to explicitly define the TSX flag in their KernelArgs for
the compute role to prevent live-migration issues during the upgrade process.

This role is intended to be called by tripleo via the kernel deployment
templates.

It's also possible to call the role as a standalone.

This also impacts upstream CentOS systems

Requirements
============

This role needs to be run on an ``Undercloud`` with a deployed ``Overcloud``.

Dependencies
============

No dependencies.

Example Playbook
================

Standard playbook:

.. code-block:: yaml

   - hosts: nova_libvirt
     roles:
       - { role: compute_tsx}

Reporting playbook with no failure:

.. code-block:: yaml

  - hosts: nova_libvirt
    vars:
      - compute_tsx_warning: true
    roles:
      - { role: compute_tsx }

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
   :role: roles/compute_tsx
