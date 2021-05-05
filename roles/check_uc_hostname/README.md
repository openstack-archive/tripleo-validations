Check-uc-hostname
=================

Add Ansible role to check DockerInsecureRegistryAddress matches the UC hostname.

Requirements
------------

This role will be executed pre Overcloud Update, and post Update


Role Variables
--------------

* `check_uc_hostname_debug`: <'false'> -- debugging mode.
* `check_uc_hostname_containers`: <'{{ansible_env.HOME}}/containers-prepare-parameter.yaml'> -- Sets the default path to the `containers-prepare-parameters.yaml` file on the Undercloud.
* `check_uc_hostname_undercloud`: <'{{ ansible_env.HOME }}/undercloud.conf'> -- Sets the default path to the `undercloud.conf` file on the Undercloud.

Dependencies
------------

No Dependencies

Example Playbook
----------------

    - hosts: servers
      roles:
      - { role: check_uc_hostname, check_uc_hostname_debug: true }

License
-------

Apache

Author Information
------------------

Red Hat TripleO DFG:Upgrades
