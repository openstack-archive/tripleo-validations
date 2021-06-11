=================
check_uc_hostname
=================

--------------
About the role
--------------

Ansible role to check ``DockerInsecureRegistryAddress`` matches the UC hostname.

The purpose of this validation is mostly target for the FFWD 13 to 16.X procedure.

Customer is expected to follow the step `9.3. Configuring access to the
undercloud registry
<https://access.redhat.com/documentation/en-us/red_hat_openstack_platform/16.1/html-single/framework_for_upgrades_13_to_16.1/index#configuring-access-to-the-undercloud-registry-composable-services>`_

The customer needs to retrieve the control plane host name on the
undercloud and add it into the ``DockerInsecureRegistryAddress``.

It might happen that the user misses this step or doesn't really add
the right control plan host name and then ``podman`` fails to retrieve the
containers.

To summarize what customer is expected to do:

- Run ``sudo hiera container_image_prepare_node_names`` to get host name(s)
- Edit the containers-prepare-parameter.yaml file and the ``DockerInsecureRegistryAddress`` parameter with
  host name and IP of the undercloud.

This validation will:

- Pull ``DockerInsecureRegistryAddress`` (list) from the Openstack environment
- Run ``sudo hiera container_image_prepare_node_names``
- Verify the container_image_prepare_node_names returned from ``hiera`` is contained in the ``DockerInsecureRegistryAddress`` list.

Requirements
============

This role will be executed pre Overcloud Update.

Dependencies
============

No Dependencies

Example Playbook
================

.. code-block:: yaml

   - hosts: servers
     vars:
       check_uc_hostname_debug: true
     roles:
       - check_uc_hostname

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
  :role: roles/check_uc_hostname
