========================
Team and repository tags
========================

.. image:: https://governance.openstack.org/tc/badges/tripleo-validations.svg
    :target: https://governance.openstack.org/tc/reference/tags/index.html

.. Change things from this point on

TripleO Validations
===================

A collection of Ansible roles and playbooks to detect and report potential
issues during TripleO deployments.

The validations will help detect issues early in the deployment process and
prevent field engineers from wasting time on misconfiguration or hardware
issues in their environments.

All validations are written in Ansible and are written in a way that's
consumable by the `Mistral validation framework
<https://review.opendev.org/#/c/255792/>`_ or by Ansible directly. They are
available independently from the UI or the command line client.

* Free software: Apache license
* Documentation: https://docs.openstack.org/tripleo-validations/latest/
* Release notes: https://docs.openstack.org/releasenotes/tripleo-validations/
* Source: https://opendev.org/openstack/tripleo-validations
* Bugs: https://storyboard.openstack.org/#!/project/openstack/tripleo-validations

Prerequisites
-------------

The TripleO validations require Ansible 2.7 or above::

    $ sudo pip install 'ansible>=2.7'

Existing validations
--------------------

Here are all the validations that currently exist. They're grouped by
the deployment stage they're should be run on.

Validations can belong to multiple groups.

.. include:: validations-groups.rst

To add a new group, you will need to edit the ``groups.yaml`` file located in
the root of the TripleO Validations directory::

    $ [vim|emacs] groups.yaml
    ...
    pre-update:
      - description: >-
          Validations which try to validate your OpenStack deployment before you
          update it.
    ...

Writing Validations
-------------------

All validations are written in standard Ansible with a couple of extra
meta-data to provide information to the Mistral validation framework.

For people not familiar with Ansible, get started with their `excellent
documentation <https://docs.ansible.com/ansible/>`_.

After the generic explanation on writing validations is a couple of concrete
examples.

Directory Structure
~~~~~~~~~~~~~~~~~~~

All validations consist of an Ansible role located in the ``roles`` directory
and a playbook located in the ``playbooks`` directory.

- the ``playbooks`` one contains all the validations playbooks you can run;
- the ``lookup_plugins`` one is for custom Ansible look up plugins available
  to the validations;
- the ``library`` one is for custom Ansible modules available to the
  validations;
- the ``roles`` one contains all the necessary Ansible roles to validate your
  TripleO deployment;

Here is what the tree looks like::

    playbooks/
      ├── first_validation.yaml
      ├── second_validation.yaml
      ├── third_validation.yaml
      └── etc...
    library/
      ├── another_module.py
      ├── some_module.py
      └── etc...
    lookup_plugins/
      ├── one_lookup_plugin.py
      ├── another_lookup_plugin.py
      └── etc...
    roles
      ├── first_role
      ├── second_role
      └── etc...


Sample Validation
~~~~~~~~~~~~~~~~~

Each validation is an Ansible playbook located in the ``playbooks`` directory
calling his own Ansible role located in the ``roles`` directory. Each playbook
have some metadata. Here is what a minimal validation would look like::

    ---
    - hosts: undercloud
      vars:
        metadata:
          name: Hello World
          description: This validation prints Hello World!
      roles:
      - hello-world

It should be saved as ``playbooks/hello_world.yaml``.

As shown here, the validation playbook requires three top-level directives:
``hosts``, ``vars -> metadata`` and ``roles``.

``hosts`` specify which nodes to run the validation on. Based on the
``hosts.sample`` structure, the options can be ``all`` (run on all nodes),
``undercloud``, ``allovercloud`` (all overcloud nodes), ``controller`` and
``compute``.

The ``vars`` section serves for storing variables that are going to be
available to the Ansible playbook. The validations API uses the ``metadata``
section to read each validation's name and description. These values are then
reported by the API.

The validations can be grouped together by specifying a ``groups`` metadata.
Groups function similar to tags and a validation can thus be part of many
groups.  Here is, for example, how to have a validation be part of the
`pre-deployment` and `hardware` groups::

    metadata:
      groups:
        - pre-deployment
        - hardware

``roles`` include the Ansible role, which contains all the tasks to run,
associated to this validation. Each task is a YAML dictionary that must at
minimum contain a name and a module to use.  Module can be any module that ships
with Ansible or any of the custom ones in the ``library`` directory.

The `Ansible documentation on playbooks
<https://docs.ansible.com/ansible/playbooks.html>`__ provides more detailed
information.

Ansible Inventory
~~~~~~~~~~~~~~~~~

Dynamic inventory
+++++++++++++++++

Tripleo-validations ships with a `dynamic inventory
<https://docs.ansible.com/ansible/intro_dynamic_inventory.html>`__, which
contacts the various OpenStack services to provide the addresses of the
deployed nodes as well as the undercloud.

Just pass ``-i /usr/bin/tripleo-ansible-inventory`` to ``ansible-playbook``
command.

As the playbooks are located in their own directory and not at the same level as
the ``roles``, ``callback_plugins``, ``library`` and ``lookup_plugins``
directories, you will have to export some Ansible variables first::

    $ cd tripleo-validations/
    $ export ANSIBLE_CALLBACK_PLUGINS="${PWD}/callback_plugins"
    $ export ANSIBLE_ROLES_PATH="${PWD}/roles"
    $ export ANSIBLE_LOOKUP_PLUGINS="${PWD}/lookup_plugins"
    $ export ANSIBLE_LIBRARY="${PWD}/library"

    $ ansible-playbook -i /usr/bin/tripleo-ansible-inventory playbooks/hello_world.yaml

Hosts file
++++++++++

When more flexibility than what the current dynamic inventory provides is
needed or when running validations against a host that hasn't been deployed via
heat (such as the ``prep`` validations), it is possible to write a custom hosts
inventory file. It should look something like this::

    [undercloud]
    undercloud.example.com

    [allovercloud:children]
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
``[allovercloud:children]`` in the above example. If a validation specifies
``hosts: overcloud``, it will be run on any node that belongs to the
``compute`` or ``controller`` groups. If a node happens to belong to both, the
validation will only be run once.

Lastly, there is an ``[all:vars]`` section where to configure certain
Ansible-specific options.

``ansible_ssh_user`` will specify the user Ansible should SSH as. If that user
does not have root privileges, it is possible to instruct it to use ``sudo`` by
setting ``ansible_sudo`` to ``true``.

Learn more at the `Ansible documentation page for the Inventory
<https://docs.ansible.com/ansible/intro_inventory.html>`__

Custom Modules
~~~~~~~~~~~~~~

In case the `available Ansible modules
<https://docs.ansible.com/ansible/modules_by_category.html>`__ don't cover your
needs, it is possible to write your own. Modules belong to the
``library`` directory.

Here is a sample module that will always fail::

    #!/usr/bin/env python

    from ansible.module_utils.basic import AnsibleModule

    if __name__ == '__main__':
        module = AnsibleModule(argument_spec={})
        module.fail_json(msg="This module always fails.")

Save it as ``library/my_module.py`` and use it in a validation like
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
<https://docs.ansible.com/ansible/developing_modules.html>`__.

Running a validation
~~~~~~~~~~~~~~~~~~~~

Running the validations require ansible and a set of nodes to run them against.
These nodes need to be reachable from the operator's machine and need to have
an account it can ssh to and perform passwordless sudo.

The nodes need to be present in the static inventory file or available from the
dynamic inventory script depending on which one the operator chooses to use.
Check which nodes are available with::

    $ source stackrc
    $ tripleo-ansible-inventory --list

In general, Ansible and the validations will be located on the *undercloud*,
because it should have connectivity to all the *overcloud* nodes is already set
up to SSH to them.

::

    $ source ~/stackrc
    $ /bin/run-validations.sh --help
    Usage:
        run-validations.sh [--help]
                           [--debug]
                           [--ansible-default-callback]
                           [--plan <overcloud>]
                           --validation-name <validation_name>

    --debug:                      Enable ansible verbose mode (-vvvv connection debugging)
    --ansible-default-callback:   Use the 'default' Ansible callback plugin instead of the
                                  tripleo-validations custom callback 'validation_output'
    --plan:                       Stack name to use for generating the inventory data
    --validation-name:            The name of the validation

    $ /bin/run-validations.sh --validation-name validation

Example: Verify Undercloud RAM requirements
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The Undercloud has a requirement of 16GB RAM. Let's write a validation
that verifies this is indeed the case before deploying anything.

Let's create ``playbooks/undercloud-ram.yaml`` and put some metadata
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

Now let's include the Ansible role associated to this validation. Add this under
the same indentation as ``hosts`` and ``vars``::

    roles:
    - undercloud-ram

Now let's create the ``undercloud-ram`` Ansible role which will contain the
necessary task(s) for checking if the Undercloud has the mininum amount of RAM
required.::

    $ cd tripleo-validations
    $ ansible-galaxy init --init-path=roles/ undercloud-ram
    - undercloud-ram was created successfully

The tree of the new created role should look like::

    undercloud-ram/
      ├── defaults
      │   └── main.yml
      ├── meta
      │   └── main.yml
      ├── tasks
      │   └── main.yml
      └── vars
          └── main.yml

Now let's add an Ansible task to test that it's all set up properly::

    $ cd roles
    $ cat <<EOF >> undercloud-ram/tasks/main.yml
    - name: Test Output
      debug:
        msg: "Hello World!"
    EOF

When running it, it should output something like this::

    $ /bin/run-validations.sh --validation-name undercloud-ram.yaml --ansible-default-callback

    PLAY [undercloud] *********************************************************

    TASK [Gathering Facts] ****************************************************
    ok: [undercloud]

    TASK [undercloud-ram : Test Output] ***************************************
    ok: [undercloud] => {
        "msg": "Hello World!"
    }

    PLAY RECAP ****************************************************************
    undercloud                 : ok=2    changed=0    unreachable=0    failed=0


If you run into an issue where the validation isn't found, it may be because the
run-validations.sh script is searching for it in the path where the packaging
installs validations.  For development, export an environment variable named
VALIDATIONS_BASEDIR with the value of base bath of your git repo.::

    cd /path/to/git/repo
    export VALIDATIONS_BASEDIR=$(pwd)


Writing the full validation code is quite easy in this case because Ansible has
done all the hard work for us already. We can use the ``ansible_memtotal_mb``
fact to get the amount of RAM (in megabytes) the tested server currently has.
For other useful values, run ``ansible -i /usr/bin/tripleo-ansible-inventory
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

    ansible-playbook -i /usr/bin/tripleo-ansible-inventory playbooks/undercloud-ram.yaml -e minimum_ram_gb=1

And this should fail by requiring much more RAM than is necessary::

    ansible-playbook -i /usr/bin/tripleo-ansible-inventory playbooks/undercloud-ram.yaml -e minimum_ram_gb=128

(the actual values may be different in your configuration -- just make sure one
is low enough and the other too high)

And that's it! The validation is now finished and you can start using it in
earnest.

Create a new role with automation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The role addition process is also automated using ansible. If ansible is
available on the development workstation change directory to the root of
the `tripleo-validations` repository and run the the following command which
will perform the basic tasks noted above.

.. code-block:: console

    $ cd tripleo-validations/
    $ ansible-playbook -i localhost, role-addition.yml -e role_name=${NEWROLENAME}

When the role is ready for CI, add a **job** entry into the
`zuul.d/molecule.yaml`.

.. code-block:: yaml

    - job:
        files:
        - ^roles/${NEWROLENAME}/.*
        name: tripleo-validations-centos-7-molecule-${NEWROLENAME}
        parent: tripleo-validations-centos-7-base
        vars:
          tripleo_validations_role_name: ${NEWROLENAME}


Make sure to add the **job** name into the check and gate section at the top
of the `molecule.yaml` file.

.. code-block:: yaml

    - project:
        check:
          jobs:
            - tripleo-validations-centos-7-molecule-${NEWROLENAME}
        gate:
          jobs:
            - tripleo-validations-centos-7-molecule-${NEWROLENAME}


Finally add a role documentation file at
`doc/source/roles/role-${NEWROLENAME}.rst`. This file will need to contain
a title, a literal include of the defaults yaml and a literal include of
the molecule playbook, or playbooks, used to test the role, which is noted
as an "example" playbook.

Local testing of new roles
~~~~~~~~~~~~~~~~~~~~~~~~~~

Local testing of new roles can be done in any number of ways, however,
the easiest way is via the script `run-local-test` on a *CentOS 8* machaine.
This script will setup the local work environment to execute tests mimicking
what Zuul does.

.. warning::

    This script makes the assumption the executing user has the
    ability to escalate privileges and will modify the local system.

To use this script execute the following command.

.. code-block:: console

    $ ./scripts/run-local-test ${NEWROLENAME}

When using the `run-local-test` script, the TRIPLEO_JOB_ANSIBLE_ARGS
environment variable can be used to pass arbitrary Ansible arguments.
For example, the following shows how to use `--skip-tags` when testing
a role with tags.

.. code-block:: console

    $ export TRIPLEO_JOB_ANSIBLE_ARGS="--skip-tags tag_one,tag_two"
    $ ./scripts/run-local-test ${ROLENAME}

Role based testing with molecule can be executed directly from within
the role directory.

.. note::

    All tests require Podman for container based testing. If Podman
    is not available on the local workstation it will need to be
    installed prior to executing most molecule based tests.


.. note::

    The script `bindep-install`, in the **scripts** path, is
    available and will install all system dependencies.


.. note::

    Some roles depend on some packages which are available only through the EPEL
    repositories. So, please ensure you have installed them on your CentOS 8 host
    before running molecule tests.


Before running basic molecule tests, it is recommended to install all
of the python dependencies in a virtual environment.

.. code-block:: console

    $ python -m virtualenv --system-site-packages "${HOME}/test-python"
    $ ${HOME}/test-python/bin/pip install -r requirements.txt \
                                          -r test-requirements.txt \
                                          -r molecule-requirements.txt
    $ source ${HOME}/test-python/bin/activate


Now, it is important to install validations-common and tripleo-ansible as
dependencies.

.. code-block:: console

    $ cd tripleo-validations/
    $ for REPO in validations-common tripleo-ansible; do
        git clone https://opendev.org/openstack/${REPO} roles/roles.galaxy/${REPO}
      done


To run a basic molecule test, simply source the `ansible-test-env.rc`
file from the project root, and then execute the following commands.

.. code-block:: console

    (test-python) $ cd roles/${NEWROLENAME}/
    (test-python) $ molecule test --all


If a role has more than one scenario, a specific scenario can be
specified on the command line. Running specific scenarios will
help provide developer feedback faster. To pass-in a scenario use
the `--scenario-name` flag with the name of the desired scenario.

.. code-block:: console

    (test-python) $ cd tripleo-validations/roles/${NEWROLENAME}/
    (test-python) $ molecule test --scenario-name ${EXTRA_SCENARIO_NAME}


When debugging molecule tests its sometimes useful to use the
`--debug` flag. This flag will provide extra verbose output about
test being executed and running the environment.

.. code-block:: console

    (test-python) $ molecule --debug test
