===========
node_health
===========

Role is used by the :ref:`pre-upgrade_node-health` validation to verify state of the overcloud
compute services and baremetal nodes they are running on.

As the clients contacted require Keystone authentication, the role requires
relevant values, such as Keystone endpoint and username, for correct operation.
Otherwise it will produce authentication error.

.. ansibleautoplugin::
   :role: roles/node_health
