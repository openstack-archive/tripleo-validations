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

Prerequisites
-------------

The TripleO validations require Ansible 2.0 or above::

    $ sudo pip install 'ansible>=2'

Existing validations
--------------------

Here are all the validations that currently exist. They're grouped by
the deployment stage they're should be run on.

Validations can belong to multiple groups.

Prep
~~~~

Validations that are run on a fresh machine *before* the undercloud is
installed.

.. include:: validations-prep.rst

Pre Introspection
~~~~~~~~~~~~~~~~~

Validations that are run when the undercloud is ready to perform hardware
introspection.

.. include:: validations-pre-introspection.rst

Pre Deployment
~~~~~~~~~~~~~~

Validation that are run right before deploying the overcloud.

.. include:: validations-pre-deployment.rst

Post Deployment
~~~~~~~~~~~~~~~

Validations that are run after the overcloud deployment finished.

.. include:: validations-post-deployment.rst


Writing Validations
-------------------

All validations are written in standard Ansible with a couple of extra
meta-data to provide information to the Mistral validation framework.

For people not familiar with Ansible, get started with their `excellent
documentation <http://docs.ansible.com/ansible/>`_.

After the generic explanation on writing validations is a couple of concrete
examples.

Directory Structure
~~~~~~~~~~~~~~~~~~~

All validations are located in the ``validations`` directory. It
contains a couple of subdirectories:

- the ``files`` directory contains scripts that are directly executable;
- the ``library`` one is for custom Ansible modules available to the
  validations;
- ``tasks`` is for common steps that can be shared between the validations.

Here is what the tree looks like::

    validations
    ├── first_validation.yaml
    ├── second_validation.yaml
    ├── files
    │   └── some_script.sh
    ├── library
    │   ├── another_module.py
    │   └── some_module.py
    └── tasks
        └── some_task.yaml

Sample Validation
~~~~~~~~~~~~~~~~~

Each validation is an Ansible playbook with a known location and some
meta-data. Here is what a minimal validation would look like::

    ---
    - hosts: overcloud
      vars:
        metadata:
          name: Hello World
          description: This validation prints Hello World!
      tasks:
      - name: Run an echo command
        command: echo Hello World!

It should be saved as ``validations/hello_world.yaml``.

As shown here, the validation playbook requires three top-level directives:
``hosts``, ``vars -> metadata`` and ``tasks``.

``hosts`` specify which nodes to run the validation on. Based on the
``hosts.sample`` structure, the options can be ``all`` (run on all nodes),
``undercloud``, ``overcloud`` (all overcloud nodes), ``controller`` and
``compute``.

The ``vars`` section serves for storing variables that are going to be
available to the Ansible playbook. The validations API uses the ``metadata``
section to read each validation's name and description. These values are then
reported by the API and shown in the UI.

The validations can be grouped together by specifying a ``groups`` metadata.
Groups function similar to tags and a validation can thus be part of many
groups.  Here is, for example, how to have a validation be part of the
`pre-deployment` and `hardware` groups::

    metadata:
      groups:
        - pre-deployment
        - hardware

``tasks`` contain a list of Ansible tasks to run. Each task is a YAML
dictionary that must at minimum contain a name and a module to use.
Module can be any module that ships with Ansible or any of the custom
ones in the ``library`` subdirectory.

The `Ansible documentation on playbooks
<http://docs.ansible.com/ansible/playbooks.html>`__ provides more detailed
information.

Ansible Inventory
~~~~~~~~~~~~~~~~~

Dynamic inventory
+++++++++++++++++

Tripleo-validations ships with a `dynamic inventory
<http://docs.ansible.com/ansible/intro_dynamic_inventory.html>`__, which
contacts the various OpenStack services to provide the addresses of the
deployed nodes as well as the undercloud.

Just pass ``-i tripleo-ansible-inventory`` to ``ansible-playbook`` command::

    ansible-playbook -i tripleo-ansible-inventory validations/hello_world.yaml

Hosts file
++++++++++

When more flexibility than what the current dynamic inventory provides is
needed or when running validations against a host that hasn't been deployed via
heat (such as the ``prep`` validations), it is possible to write a custom hosts
inventory file. It should look something like this::

    [undercloud]
    undercloud.example.com

    [overcloud:children]
    controller
    compute

    [controller]
    controller.example.com

    [compute]
    compute-1.example.com
    compute-2.example.com

    [all:vars]
    ansible_ssh_user=stack
    ansible_sudo=true

It will have a ``[group]`` section for each role (``undercloud``,
``controller``, ``compute``) listing all the nodes belonging to that group. It
is also possible to create a group from other groups as done with
``[overcloud:children]`` in the above example. If a validation specifies
``hosts: overcloud``, it will be run on any node that belongs to the
``compute`` or ``controller`` groups. If a node happens to belong to both, the
validation will only be run once.

Lastly, there is an ``[all:vars]`` section where to configure certain
Ansible-specific options.

``ansible_ssh_user`` will specify the user Ansible should SSH as. If that user
does not have root privileges, it is possible to instruct it to use ``sudo`` by
setting ``ansible_sudo`` to ``true``.

Learn more at the `Ansible documentation page for the Inventory
<http://docs.ansible.com/ansible/intro_inventory.html>`__

Custom Modules
~~~~~~~~~~~~~~

In case the `available Ansible modules
<http://docs.ansible.com/ansible/modules_by_category.html>`__ don't cover your
needs, it is possible to write your own. Modules belong to the
``validations/library`` directory.

Here is a sample module that will always fail::

    #!/usr/bin/env python

    from ansible.module_utils.basic import *

    if __name__ == '__main__':
        module = AnsibleModule(argument_spec={})
        module.fail_json(msg="This module always fails.")

Save it as ``validations/library/my_module.py`` and use it in a validation like
so::

    tasks:
    ...  # some tasks
    - name: Running my custom module
      my_module:
    ...  # some other tasks

The name of the module in the validation ``my_module`` must match the file name
(without extension): ``my_module.py``.

The custom modules can accept parameters and do more complex reporting.  Please
refer to the guide on writing modules in the Ansible documentation.

Learn more at the `Ansible documentation page about writing custom modules
<http://docs.ansible.com/ansible/developing_modules.html>`__.

Running a validation
~~~~~~~~~~~~~~~~~~~~

Running the validations require ansible and a set of nodes to run them against.
These nodes need to be reachable from the operator's machine and need to have
an account it can ssh to and perform passwordless sudo.

The nodes need to be present in the static inventory file or available from the
dynamic inventory script depending on which one the operator choses to use.
Check which nodes are available with::

    $ source stackrc
    $ tripleo-ansible-inventory --list

In general, Ansible and the validations will be located on the *undercloud*,
because it should have connectivity to all the *overcloud* nodes is already set
up to SSH to them.

::

    $ source ~/stackrc
    $ ansible-playbook -i tripleo-ansible-inventory path/to/validation.yaml

Example: Verify Undercloud RAM requirements
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The Undercloud has a requirement of 16GB RAM. Let's write a validation
that verifies this is indeed the case before deploying anything.

Let's create ``validations/undercloud-ram.yaml`` and put some metadata
in there::

    ---
    - hosts: undercloud
      vars:
        metadata:
          name: Minimum RAM required on the undercloud
          description: >
            Make sure the undercloud has enough RAM.
          groups:
            - prep
            - pre-introspection

The ``hosts`` key will tell which server should the validation run on. The
common values are ``undercloud``, ``overcloud`` (i.e. all overcloud nodes),
``controller`` and ``compute`` (i.e. just the controller or the compute nodes).

The ``name`` and ``description`` metadata will show up in the API and the
TripleO UI so make sure to put something meaningful there. The ``groups``
metadata applies a tag to the validation and allows to group them together in
order to perform group operations, such are running them all in one call.

Now let's add an Ansible task to test that it's all set up properly. Add
this under the same indentation as ``hosts`` and ``vars``::

      tasks:
      - name: Test Output
        debug: msg="Hello World!"

When running it, it should output something like this::

    $ ansible-playbook -i tripleo-ansible-inventory validations/undercloud-ram.yaml

    PLAY [undercloud] *************************************************************

    GATHERING FACTS ***************************************************************
    ok: [localhost]

    TASK: [Test Output] ***********************************************************
    ok: [localhost] => {
        "msg": "Hello World!"
    }

    PLAY RECAP ********************************************************************
    localhost                  : ok=2    changed=0    unreachable=0    failed=0

Writing the full validation code is quite easy in this case because Ansible has
done all the hard work for us already. We can use the ``ansible_memtotal_mb``
fact to get the amount of RAM (in megabytes) the tested server currently has.
For other useful values, run ``ansible -i tripleo-ansible-inventory
undercloud -m setup``.

So, let's replace the hello world task with a real one::

      tasks:
      - name: Verify the RAM requirements
        fail: msg="The RAM on the undercloud node is {{ ansible_memtotal_mb }} MB, the minimal recommended value is 16 GB."
        failed_when: "({{ ansible_memtotal_mb }}) < 16000"

Running this, we see::

    TASK: [Verify the RAM requirements] *******************************************
    failed: [localhost] => {"failed": true, "failed_when_result": true}
    msg: The RAM on the undercloud node is 8778 MB, the minimal recommended value is 16 GB.

Because our Undercloud node really does not have enough RAM. Your mileage may
vary.

Either way, the validation works and reports the lack of RAM properly!

``failed_when`` is the real hero here: it evaluates an Ansible expression (e.g.
does the node have more than 16 GB of RAM) and fails when it's evaluated as
true.

The ``fail`` line right above it lets us print a custom error in case of
a failure. If the task succeeds (because we do have enough RAM), nothing will
be printed out.

Now, we're almost done, but there are a few things we can do to make this nicer
on everybody.

First, let's hoist the minimum RAM requirement into a variable. That way we'll
have one place where to change it if we need to and we'll be able to test the
validation better as well!

So, let's call the variable ``minimum_ram_gb`` and set it to ``16``. Do this in
the ``vars`` section::

      vars:
        metadata:
          name: ...
          description: ...
          groups: ...
        minimum_ram_gb: 16

Make sure it's on the same indentation level as ``metadata``.

Then, update ``failed_when`` like this::

    failed_when: "({{ ansible_memtotal_mb }}) < {{ minimum_ram_gb|int * 1024 }}"

And ``fail`` like so::

    fail: msg="The RAM on the undercloud node is {{ ansible_memtotal_mb }} MB, the minimal recommended value is {{ minimum_ram_gb|int * 1024 }} MB."

And re-run it again to be sure it's still working.

One benefit of using a variable instead of a hardcoded value is that we can now
change the value without editing the yaml file!

Let's do that to test both success and failure cases.

This should succeed but saying the RAM requirement is 1 GB::

    ansible-playbook -i tripleo-ansible-inventory validations/undercloud-ram.yaml -e minimum_ram_gb=1

And this should fail by requiring much more RAM than is necessary::

    ansible-playbook -i tripleo-ansible-inventory validations/undercloud-ram.yaml -e minimum_ram_gb=128

(the actual values may be different in your configuration -- just make sure one
is low enough and the other too high)

And that's it! The validation is now finished and you can start using it in
earnest.

For reference, here's the full validation::

    ---
    - hosts: undercloud
      vars:
        metadata:
          name: Minimum RAM required on the undercloud
          description: Make sure the undercloud has enough RAM.
          groups:
            - prep
            - pre-introspection
        minimum_ram_gb: 16
      tasks:
      - name: Verify the RAM requirements
        fail: msg="The RAM on the undercloud node is {{ ansible_memtotal_mb }} MB, the minimal recommended value is {{ minimum_ram_gb|int * 1024 }} MB."
        failed_when: "({{ ansible_memtotal_mb }}) < {{ minimum_ram_gb|int * 1024 }}"
