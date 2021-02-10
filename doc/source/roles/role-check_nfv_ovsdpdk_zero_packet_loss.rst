==================================
check_nfv_ovsdpdk_zero_packet_loss
==================================
--------------
About the role
--------------
This role validates the NFV OvS DPDK zero packet loss rules on OvS DPDK Compute nodes to find out the issues with NFV OvS Dpdk configuration.
Requirements
============
- Validates PMD threads configuration.
- Validates PMD threads included as part of isolcpus.
- Checks any interrupts on Isolated CPU's.
- Validates all the data paths are same on the server if ovs user bridge is used.
- Validates bandwidth of the PCI slots.
- Validates hugepages, CPU pinning, emulatorpin threads and libvirt queue size configuration on NFV instances.
Dependencies
============
- Expects all the configuration files that are passed.
Example Playbook
================
.. code-block:: yaml

    - hosts: servers
      roles:

        - { role: check_nfv_ovsdpdk_zero_packet_loss }

License
=======
Apache
Author Information
=================
**Red Hat TripleO DFG:NFV Integration**
----------------
Full Description
----------------

.. ansibleautoplugin::
   :role: roles/check_nfv_ovsdpdk_zero_packet_loss
