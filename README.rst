========================
Team and repository tags
========================

.. image:: http://governance.openstack.org/badges/tripleo-validations.svg
    :target: http://governance.openstack.org/reference/tags/index.html

.. Change things from this point on

TripleO Validations
===================

A collection of Ansible playbooks to detect and report potential issues during TripleO deployments

The validations will help detect issues early in the deployment process and
prevent field engineers from wasting time on misconfiguration or hardware
issues in their environments.

All validations are written in Ansible and are written in a way that's
consumable by the `Mistral validation framework
<https://review.openstack.org/#/c/255792/>`_ or by Ansible directly. They are
available independently from the UI or the command line client.

* Free software: Apache license
* Source: http://git.openstack.org/cgit/openstack/tripleo-validations
* Bugs: https://bugs.launchpad.net/tripleo/+bugs?field.tag=validations
