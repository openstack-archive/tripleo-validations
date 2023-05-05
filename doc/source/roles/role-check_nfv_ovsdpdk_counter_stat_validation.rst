=========================================
check_nfv_ovsdpdk_counter_stat_validation
=========================================

--------------
About the role
--------------

This role validates the NFV OvS DPDK interface counter statistics.

Requirements
============

- Gathers information about all the existing interfaces.
- Validates ovs_tx_failure_drops, ovs_tx_mtu_exceeded_drops, ovs_rx_qos_drops, ovs_tx_qos_drops, ovs_tx_retries metrics for every interface.
- Checks if any of the listed counters are increasing and outputs its related configuration.

Dependencies
============

Example Playbook
================

.. code-block:: yaml

    - hosts: servers
      roles:

        - { role: check_nfv_ovsdpdk_counter_stat_validation }

License
=======
Apache

Author Information
==================

**Red Hat TripleO DFG:NFV Integration**

----------------
Full Description
----------------

.. ansibleautoplugin::
   :role: roles/check_nfv_ovsdpdk_counter_stat_validation
