============
policy_file
============

--------------
About The Role
--------------

This role will check if there is a file named Policy.yaml in the controlers.
The file should be located at the manila's configuration folder in the container.

Requirements
============

No Requirements.

Dependencies
============

No dependencies.

Example Playbook
================

.. code-block:: yaml

 - hosts: "{{ controller_rolename | default('Controller') }}"
   vars:
   metadata:
     name: Verify that keystone admin token is disabled
       description: |
         This validation checks that policy file of manilas configuration folder inside of the container,exists.
       groups:
         - post-deployment
       categories:
         - controller
       products:
         - tripleo
    manilas_policy_file: "/var/lib/config-data/puppet-generated/manila/etc/manila/policy.yaml"
   roles:
     - check_manila_policy_file

Author Information
==================

**Red Hat Manila**

----------------
Full Description
----------------

.. ansibleautoplugin::
  :role: roles/check_manila_policy_file
