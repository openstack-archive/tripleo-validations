============
fips_enabled
============

--------------
About The Role
--------------

This role will check if system has turned on FIPS.
This validation can be enabled or disabled within the variable:
`enforce_fips_validation`, setting it to `true` will
enable the validation, setting to `false` will disable it.

Requirements
============

Turned on FIPS.

Dependencies
============

No dependencies.

Example Playbook
================

.. code-block:: yaml

    - hosts: localhost
      gather_facts: false
      roles:
        - { role: fips_enabled }

Licence
=======

Apache

Author Information
==================

**Red Hat TripleO DFG:Security Squad:OG**

----------------
Full Description
----------------

.. ansibleautoplugin::
  :role: roles/fips_enabled
