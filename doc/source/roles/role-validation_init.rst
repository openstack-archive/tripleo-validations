===============
validation_init
===============

--------------
About The Role
--------------

The ``validation_init`` role aims to create new validation from a skeleton.

Requirements
============

None.

Dependencies
============

None.

Example Playbook
================

.. code-block:: yaml

    - name: Create my new role
      hosts: localhost
      connection: local
      gather_facts: false
      roles:
        - { role: validation_init, validation_init_role_name: "mynewrolename"}

License
=======

Apache

Author Information
==================

**Red Hat TripleO DFG:DF Squad:VF**

----------------
Full Description
----------------

.. ansibleautoplugin::
   :role: roles/validation_init
