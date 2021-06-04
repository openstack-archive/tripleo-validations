=====================
oslo_config_validator
=====================

--------------
About the role
--------------

An Ansible role that will loop through all the containers on selected host, find the Openstack service configuration file
and leverage the [oslo-config-validator](https://docs.openstack.org/oslo.config/latest/cli/validator.html) utility to validate the current running configuration.

It's also possible to generate a report that contains all differences between the sample or default values with current running configuration.

Finally, it will also verify that the current running configuration doesn't contain any known invalid settings that might have been deprecated and removed in previous versions.

Exceptions
==========

Some services like ``cinder`` can have dynamic configuration sections. In ``cinder``'s case, this is for the storage backends. To perform validation on these dynamic sections, we need to generate a yaml formatted config sample with ``oslo-config-generator`` beforehand, append a new sample configuration for each storage backends, and validate against that newly generated configuration file by passing ``--opt-data`` to the ``oslo-config-validator`` command instead of using ``--namespaces``. Since generating a sample config adds some delay to the validation, this is not the default way of validating, we prefer to validate directly using ``--namespaces``.

NOTE: At the time of writing this role, ``oslo-config-generator`` has a bug [1] when generating yaml config files, most notably with ``cinder``. Since the inclusion of oslo.config patch can't be garanteed, the role will inject this patch [2] to the oslo.config code, inside the validation container. This code change is ephemeral for the time of the configuration file generation. The reason why we want to inject this patch is because it's possible that we run the validation on containers that were created before it was merged. This ensures a smooth validation across the board.

[1] https://bugs.launchpad.net/oslo.config/+bug/1928582
[2] https://review.opendev.org/c/openstack/oslo.config/+/790883


Requirements
============

This role needs to be run on an Undercloud with a deployed Overcloud.

Role Variables
==============

- oslo_config_validator_validation: Wether or not to run assertions on produced outputs. That also means that the role will fail if anything is output post-filtering. If this is enabled with the reporting, this will most likely trigger a failure unless executed against default configuration
- oslo_config_validator_report: Wether or not we compare the configuration files found with the default config
- oslo_config_validator_invalid_settings:  When running validation, wether or not we should check for invalid settings. This adds to the time it takes to complete validation because of the way the validations_read_ini module works. This won't work without ``oslo_config_validator_validation`` enabled.
- oslo_config_validator_report_path: The folder used when generating the reports.
- oslo_config_validator_global_ignored_messages: List of regular expressions that will filter out messages globally, across all namespaces
- oslo_config_validator_namespaces_config: Specific namespace configurations. It contains namespace-specific ignored patterns as well as invalid settings configuration.
- oslo_config_validator_service_configs: Mapping of known Openstack services with their namespace configuration.
- oslo_config_validator_checked_services: List of services being validated.

Dependencies
============

- podman_container
- podman_container_info
- validations_read_ini
- https://review.opendev.org/c/openstack/oslo.config/+/790883



Example Reporting Playbook
==========================

.. code-block:: yaml

    - hosts: all
      vars:
      - oslo_config_validator_report: true
      - oslo_config_validator_validation: false
      roles:
      - { role: oslo_config_validator}

Example playbook to validate only one service
=============================================

.. code-block:: yaml

    - hosts: all
      vars:
      - oslo_config_validator_checked_services:
      - nova
      roles:
      - { role: oslo_config_validator}

License
=======

Apache

Author Information
==================

**Red Hat TripleO DFG:Compute Deployment Squad**

----------------
Full Description
----------------

.. ansibleautoplugin::
  :role: roles/oslo_config_validator
