Check-for-dangling-images
=========================

Add Ansible role to check for dangling images

Requirements
------------

This role will be executed pre Update.


Role Variables
--------------

* `check_for_dangling_images_debug`: <'false'> -- debugging mode.

Dependencies
------------

No Dependencies

Example Playbook
----------------

    - hosts: servers
      roles:
      - { role: check_for_dangling_images, check_for_dangling_images_debug: true }

License
-------

Apache

Author Information
------------------

Red Hat TripleO DFG:Upgrades
