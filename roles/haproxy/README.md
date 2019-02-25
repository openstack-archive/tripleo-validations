haproxy
=======

An Ansible role to check if the HAProxy configuration has recommended values.

Requirements
------------

This role requires an Up and Running Overcloud

Role Variables
--------------

- config_file: '/var/lib/config-data/puppet-generated/haproxy/etc/haproxy/haproxy.cfg'
- global_maxconn_min: 20480
- defaults_maxconn_min: 4096
- defaults_timeout_queue: '2m'
- defaults_timeout_client: '2m'
- defaults_timeout_server: '2m'
- defaults_timeout_check: '10s'

Dependencies
------------

No dependencies

Example Playbook
----------------

    - hosts: undercloud
      roles:
         - { role: haproxy }

License
-------

Apache

Author Information
------------------

Red Hat TripleO Validations Team.
