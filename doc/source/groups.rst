About Group
===========

For now, the validations are grouped by the deployment stage they should be run
on. A validation can belong to multiple groups.

Adding a new group
------------------

To add a new group, you will need to edit the ``groups.yaml`` file located in
the root of the TripleO Validations directory:

.. code-block:: yaml

    ...
    pre-update:
      - description: >-
          Validations which try to validate your OpenStack deployment before you
          update it.
    ...

And a new entry in the sphinx documentation index ``doc/source/index.rst``:

.. code-block:: RST

    Existing validations
    ====================

    .. toctree::
      :maxdepth: 2

      validations-no-op-details
      validations-prep-details
      validations-pre-introspection-details
      validations-pre-deployment-details
      validations-post-deployment-details
    ...

Group list
----------

Here is a list of groups and their associated validations.

.. include:: validations-groups.rst
