Developer's Guide
=================

Writing Validations
-------------------

All validations are written in standard Ansible with a couple of extra
meta-data to provide information to the validation framework.

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
have some metadata. Here is what a minimal validation would look like:

.. code-block:: yaml

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
`pre-deployment` and `hardware` groups:

.. code-block:: yaml

    metadata:
      groups:
        - pre-deployment
        - hardware

The validations can be categorized by technical domain and can belong to one or
multiple categories. The categorization is depending on what the validation is
checking on the hosts. For example, if a validation checks some networking
related configuration and needs to get configuration items from the
undercloud.conf file, you will have to put `networking` and `undercloud-config` in
the ``categories`` metadata key:

.. code-block:: yaml

    metadata:
      groups:
        - pre-deployment
        - hardware
      categories:
        - networking
        - undercloud-config

.. note::

    The ``categories`` are not restricted to a list as for the ``groups``
    present in the ``groups.yaml`` file, but it could be for example:

    * ``networking``
    * ``compute``
    * ``baremetal``
    * ``provisioning``
    * ``database``
    * ``os``
    * ``system``
    * ``packaging``
    * ``kernel``
    * ``security``
    * ``tls-everywhere``
    * ``dns``
    * ``dhcp``
    * ``dnsmasq``
    * ``webserver``
    * ``storage``
    * ``ha``
    * ``clustering``
    * ``undercloud-config``
    * etc ...

The validations should be linked to a product. Every validations hosted in
``tripleo-validations`` should get at least ``tripleo`` in the ``products``
metadata key:

.. code-block:: yaml

    metadata:
      groups:
        - pre-deployment
        - hardware
      categories:
        - networking
        - undercloud-config
      products:
        - tripleo

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
directories, you will have to export some Ansible variables first:

.. code-block:: console

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
inventory file. It should look something like this:

.. code-block:: INI

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

Here is a sample module that will always fail

.. code-block:: python

    #!/usr/bin/env python

    from ansible.module_utils.basic import AnsibleModule

    if __name__ == '__main__':
        module = AnsibleModule(argument_spec={})
        module.fail_json(msg="This module always fails.")

Save it as ``library/my_module.py`` and use it in a validation like
so:

.. code-block:: yaml

    tasks:
    ...  # some tasks
    - name: Running my custom module
      my_module:
    ...  # some other tasks

The name of the module in the validation ``my_module`` must match the file name
(without extension): ``my_module.py``.

The custom modules can accept parameters and do more complex reporting.  Please
refer to the guide on writing modules in the Ansible documentation.

.. Warning::

   Each custom module must be accompanied by the most complete unit tests
   possible.

Learn more at the `Ansible documentation page about writing custom modules
<https://docs.ansible.com/ansible/developing_modules.html>`__.

Running a validation
--------------------

Running the validations require ansible and a set of nodes to run them against.
These nodes need to be reachable from the operator's machine and need to have
an account it can ssh to and perform passwordless sudo.

The nodes need to be present in the static inventory file or available from the
dynamic inventory script depending on which one the operator chooses to use.
Check which nodes are available with:

.. code-block:: console

    $ source stackrc
    $ tripleo-ansible-inventory --list

In general, Ansible and the validations will be located on the *undercloud*,
because it should have connectivity to all the *overcloud* nodes is already set
up to SSH to them.

.. code-block:: console

    $ source ~/stackrc
    $ tripleo-validation.py
    usage: tripleo-validation.py [-h] [--inventory INVENTORY]
                                [--extra-vars EXTRA_VARS [EXTRA_VARS ...]]
                                [--validation <validation_id>[,<validation_id>,...]]
                                [--group <group>[,<group>,...]] [--quiet]
                                [--validation-dir VALIDATION_DIR]
                                [--ansible-base-dir ANSIBLE_BASE_DIR]
                                [--output-log OUTPUT_LOG]
                                {run,list,show}

    $ tripleo-validation.py run --validation <validation_name>


Example: Verify Undercloud RAM requirements
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The Undercloud has a requirement of 16GB RAM. Let's write a validation
that verifies this is indeed the case before deploying anything.

Let's create ``playbooks/undercloud-ram.yaml`` and put some metadata
in there:

.. code-block:: yaml

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
          categories:
            - os
            - system
            - ram
          products:
            - tripleo


The ``hosts`` key will tell which server should the validation run on. The
common values are ``undercloud``, ``overcloud`` (i.e. all overcloud nodes),
``controller`` and ``compute`` (i.e. just the controller or the compute nodes).

The ``name`` and ``description`` metadata will show up in the API and the
TripleO UI so make sure to put something meaningful there. The ``groups``
metadata applies a tag to the validation and allows to group them together in
order to perform group operations, such are running them all in one call.

Now let's include the Ansible role associated to this validation. Add this under
the same indentation as ``hosts`` and ``vars``:

.. code-block:: yaml

    roles:
      - undercloud-ram

Now let's create the ``undercloud-ram`` Ansible role which will contain the
necessary task(s) for checking if the Undercloud has the mininum amount of RAM
required:

.. code-block:: console

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

Now let's add an Ansible task to test that it's all set up properly:

.. code-block:: yaml

    $ cat <<EOF >> roles/undercloud-ram/tasks/main.yml
    - name: Test Output
      debug:
        msg: "Hello World!"
    EOF

When running it, it should output something like this:

.. code-block:: console

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
VALIDATIONS_BASEDIR with the value of base path of your git repo:

.. code-block:: console

    $ cd /path/to/git/repo
    $ export VALIDATIONS_BASEDIR=$(pwd)

Writing the full validation code is quite easy in this case because Ansible has
done all the hard work for us already. We can use the ``ansible_memtotal_mb``
fact to get the amount of RAM (in megabytes) the tested server currently has.
For other useful values, run ``ansible -i /usr/bin/tripleo-ansible-inventory
undercloud -m setup``.

So, let's replace the hello world task with a real one:

.. code-block:: yaml

      tasks:
      - name: Verify the RAM requirements
        fail: msg="The RAM on the undercloud node is {{ ansible_memtotal_mb }} MB, the minimal recommended value is 16 GB."
        failed_when: "({{ ansible_memtotal_mb }}) < 16000"

Running this, we see:

.. code-block:: console

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
the ``vars`` section:

.. code-block:: yaml

      vars:
        metadata:
          name: ...
          description: ...
          groups: ...
          categories: ...
          products: ...
        minimum_ram_gb: 16

Make sure it's on the same indentation level as ``metadata``.

Then, update ``failed_when`` like this:

.. code-block:: yaml

    failed_when: "({{ ansible_memtotal_mb }}) < {{ minimum_ram_gb|int * 1024 }}"

And ``fail`` like so:

.. code-block:: yaml

    fail: msg="The RAM on the undercloud node is {{ ansible_memtotal_mb }} MB, the minimal recommended value is {{ minimum_ram_gb|int * 1024 }} MB."

And re-run it again to be sure it's still working.

One benefit of using a variable instead of a hardcoded value is that we can now
change the value without editing the yaml file!

Let's do that to test both success and failure cases.

This should succeed but saying the RAM requirement is 1 GB:

.. code-block:: console

    $ ansible-playbook -i /usr/bin/tripleo-ansible-inventory playbooks/undercloud-ram.yaml -e minimum_ram_gb=1

And this should fail by requiring much more RAM than is necessary:

.. code-block:: console

    $ ansible-playbook -i /usr/bin/tripleo-ansible-inventory playbooks/undercloud-ram.yaml -e minimum_ram_gb=128

(the actual values may be different in your configuration -- just make sure one
is low enough and the other too high)

And that's it! The validation is now finished and you can start using it in
earnest.

Create a new role with automation
---------------------------------

The role addition process is also automated using ansible. If ansible is
available on the development workstation change directory to the root of
the `tripleo-validations` repository and run the the following command which
will perform the basic tasks noted above.

.. code-block:: console

    $ cd tripleo-validations/
    $ export ANSIBLE_ROLES_PATH="${PWD}/roles"
    $ ansible-playbook -i localhost, role-addition.yml -e validation_init_role_name=${NEWROLENAME}

The new role will be created in `tripleo-validations/roles/` from a skeleton and one playbook
will be added in `tripleo-validations/playbooks/`.

It will also add a new **job** entry into the `zuul.d/molecule.yaml`.

.. code-block:: yaml

    - job:
        files:
          - ^roles/${NEWROLENAME}/.*
          - ^tests/prepare-test-host.yml
          - ^ci/playbooks/pre.yml
          - ^ci/playbooks/run.yml
          - ^molecule-requirements.txt
        name: tripleo-validations-centos-8-molecule-${NEWROLENAME}
        parent: tripleo-validations-centos-8-base
        vars:
          tripleo_validations_role_name: ${NEWROLENAME}


And the **job** name will be added into the check and gate section at the top
of the `molecule.yaml` file.

.. code-block:: yaml

    - project:
        check:
          jobs:
            - tripleo-validations-centos-8-molecule-${NEWROLENAME}
        gate:
          jobs:
            - tripleo-validations-centos-8-molecule-${NEWROLENAME}

.. note::

    Adding `Molecule` test is highly recommended but remains **optional**. Some
    validations might require a real OpenStack Infrastructure in order to run
    them and this, by definition, will make the `Molecule` test very complex to
    implement.

    If you are in this case when creating a new validation, please
    add `-e validation_init_molecule=false` to the above `ansible-playbook`
    command. No molecule directory and no CI Job will be created.

Finally it will add a role documentation file at
`doc/source/roles/role-${NEWROLENAME}.rst`. This file will need to contain
a title, a literal include of the defaults yaml and a literal include of
the molecule playbook, or playbooks, used to test the role, which is noted
as an "example" playbook.

You will now be able to develop your new validation!

Developing your own molecule test(s)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The role addition process will create a default Molecule scenario from the
skeleton. By using Molecule, you will be able to test it locally and of course
it will be executed during the CI checks.

In your role directory, you will notice a `molecule` folder which contains a
single `Scenario` called `default`. Scenarios are the starting point for a lot
of powerful functionality that Molecule offers. A scenario is a kind of a test
suite for your newly created role.

The Scenario layout
+++++++++++++++++++

Within the `molecule/default` folder, you will find those files:

.. code-block:: console

   $ ls
   molecule.yml  converge.yml  prepare.yml  verify.yml

* ``molecule.yml`` is the central configuration entrypoint for `Molecule`. With this
  file, you can configure each tool that `Molecule` will employ when testing
  your role.

.. note::

    `Tripleo-validations` uses a global configuration file for `Molecule`.
    This file is located at the repository level (``tripleo-validations/.config/molecule/.config.yml``).
    and defines all the default values for all the ``molecule.yml``. By default,
    the role addition process will produce an empty ``molecule.yml`` inheriting
    this ``config.yml`` file. Any key defined in the role ``molecule.yml`` file
    will override values from the ``config.yml`` file.

    But, if you want to override the default values set in the ``config.yml``
    file, you will have to redefine them completely in your ``molecule.yml``
    file. `Molecule` won't merge both configuration files and that's why you
    will have to redefine them completely.

* ``prepare.yml`` is the playbook file that contains everything you need to
  include before your test. It could include packages installation, file
  creation, whatever your need on the instance created by the driver.

* ``converge.yml`` is the playbook file that contains the call for you
  role. `Molecule` will invoke this playbook with ``ansible-playbook`` and run
  it against and instance created by the driver.

* ``verify.yml`` is the Ansible file used for testing as Ansible is the default
  ``Verifier``. This allows you to write specific tests against the state of the
  container after your role has finished executing.

Inspecting the Global Molecule Configuration file
+++++++++++++++++++++++++++++++++++++++++++++++++

As mentioned above, ``tripleo-validations`` uses a global configuration for
Molecule.

.. literalinclude:: ../../../.config/molecule/config.yml
  :language: yaml

* The ``Driver`` provider: ``podman`` is the default. Molecule will use the
  driver to delegate the task of creating instances.
* The ``Platforms`` definitions: Molecule relies on this to know which instances
  to create, name and to which group each instance
  belongs. ``Tripleo-validations`` uses ``CentOS 8 Stream image``.
* The ``Provisioner``: Molecule only provides an Ansible provisioner. Ansible
  manages the life cycle of the instance based on this configuration.
* The ``Scenario`` definition: Molecule relies on this configuration to control
  the scenario sequence order.
* The ``Verifier`` framework. Molecule uses Ansible by default to provide a way
  to write specific stat checking tests (such as deployment smoke tests) on the
  target instance.

Local testing of new roles
--------------------------

Local testing of new roles can be done in two ways:

* Via the script `scripts/run-local-test`,
* or manually by following the procedure described below.

Running molecule tests with the script run-local-test
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This script will setup the local work environment to execute tests mimicking
what Zuul does on a *CentOS 8* machine.

.. warning::

    This script makes the assumption the executing user has the
    ability to escalate privileges and will modify the local system.

To use this script execute the following command.

.. code-block:: console

    $ cd tripleo-validations
    $ ./scripts/run-local-test ${NEWROLENAME}

When using the `run-local-test` script, the TRIPLEO_JOB_ANSIBLE_ARGS
environment variable can be used to pass arbitrary Ansible arguments.
For example, the following shows how to use `--skip-tags` when testing
a role with tags.

.. code-block:: console

    $ export TRIPLEO_JOB_ANSIBLE_ARGS="--skip-tags tag_one,tag_two"
    $ ./scripts/run-local-test ${ROLENAME}


Running molecule tests manually
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Role based testing with `molecule`_ can be executed directly from within
the role directory.

.. note::

    All tests require `Podman`_ for container based testing. If `Podman`_ is not
    available on the local workstation it will need to be installed prior to
    executing most molecule based tests.


.. note::

    The script `bindep-install`, in the **scripts** path, is available and will
    install all system dependencies.


.. note::

   Each molecule tests are configured to bind mount a read-only volume on the
   container where the tests are running:

   .. code-block:: yaml

      volumes:
        - /etc/ci/mirror_info.sh:/etc/ci/mirror_info.sh:ro

   It is an OpenStack Zuul requirement for detecting if we are on a CI node.  Of
   course, when running your `molecule`_ test on your workstation, it is going
   to fail because you don't have the empty `mirror_info.sh` script in the
   `/etc/ci/` directory. You can workaround this by creating it in your
   workstation or removing the volume key in the global configuration file for
   molecule.

   .. code-block:: console

      $ sudo mkdir -p /etc/ci
      $ sudo touch /etc/ci/mirror_info.sh



Before running basic `molecule`_ tests, it is recommended to install all
of the python dependencies in a virtual environment.

.. code-block:: console

    $ sudo dnf install python3 python3-virtualenv
    $ python3 -m virtualenv --system-site-packages "${HOME}/test-python"
    $ source "${HOME}/test-python/bin/activate"
    (test-python) $ python3 -m pip install "pip>=19.1.1" setuptools bindep --upgrade
    (test-python) $ scripts/./bindep-install
    (test-python) $ python3 -m pip install -r requirements.txt \
                                           -r test-requirements.txt \
                                           -r molecule-requirements.txt
    (test-python) $ ansible-galaxy install -fr ansible-collections-requirements.yml


Now, it is important to install `validations-common` and `tripleo-ansible` as
dependencies.

.. note::

    `validation-common` contains Ansible Custom modules needed by
    `tripleo-validations` roles. That's the reason why we will need to clone it
    beforehand.

    Cloning `tripleo-ansible` project is only necessary in order to run the
    `molecule` test(s) for the `image_serve` role. Otherwise, you probably won't
    need it.


.. code-block:: console

    $ cd tripleo-validations/
    $ for REPO in validations-common tripleo-ansible; do git clone https://opendev.org/openstack/${REPO} roles/roles.galaxy/${REPO}; done


To run a basic `molecule`_ test, simply source the `ansible-test-env.rc`
file from the project root, and then execute the following commands.

.. code-block:: console

    (test-python) $ source ansible-test-env.rc
    (test-python) $ cd roles/${NEWROLENAME}/
    (test-python) $ molecule test --all


If a role has more than one scenario, a specific scenario can be
specified on the command line. Running specific scenarios will
help provide developer feedback faster. To pass-in a scenario use
the `--scenario-name` flag with the name of the desired scenario.

.. code-block:: console

    (test-python) $ cd roles/${NEWROLENAME}/
    (test-python) $ molecule test --scenario-name ${EXTRA_SCENARIO_NAME}


When debugging `molecule`_ tests its sometimes useful to use the
`--debug` flag. This flag will provide extra verbose output about
test being executed and running the environment.

.. code-block:: console

    (test-python) $ molecule --debug test

.. _molecule: https://github.com/ansible-community/molecule
.. _podman: https://podman.io/
