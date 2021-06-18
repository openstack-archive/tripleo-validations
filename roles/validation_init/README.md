Validation_init
===============

The purpose of this `validation_init` role is to create new validation from a skeleton.

Requirements
------------

None.

Role Variables
--------------

* `validation_init_debug`: <'false'> -- Debugging mode.
* `validation_init_role_name`: <'Undefined'> -- New role name, undefined by default!
* `validation_init_prefix`: <'tripleo'> -- New role prefix
* `validation_init_skeleton_role_dir`: <'/tmp'> -- Absolute path of the directory where the skeleton will be deployed
* `validation_init_roles_dir`: <'roles'> -- Absolute/Relative path to the roles directory where the new roles will be created
* `validation_init_zuuld_molecule`: <'zuul.d/molecule.yaml'> -- Relative path to the CI molecule yaml file
* `validation_init_playbooks_dir`: <'playbooks'> -- Relative path to the playbooks directory where the new playbook will be created
* `validation_init_roles_doc_dir`: <'doc/source/roles'> -- Relative path to documentation roles directory
* `validation_init_enabling_ci`: <'true'> -- If 'true', documentation and CI configuration will be done, otherwise not

Dependencies
------------

None.

Example Playbook
----------------

    - name: Create my new role
      hosts: localhost
      connection: local
      gather_facts: false
      roles:
      - { role: validation_init, validation_init_role_name: "mynewrolename"}

License
-------

Apache

Author Information
------------------

Red hat TripleO DFG:DF Squad:VF
