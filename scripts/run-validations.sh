#!/bin/bash

# IF running on Undercloud
source ${HOME}/stackrc || { echo "The stackrc file is missing or cannot be read"; exit 1; }
# IF running on standalone, replace by
# export OS_CLOUD=standalone

usage() {
    echo "Usage:"
    echo "    run-validations.sh [--help]"
    echo "                       [--debug]"
    echo "                       [--ansible-default-callback]"
    echo "                       [--plan <overcloud>]"
    echo "                       --validation-name <validation_name>"
    echo ""
    echo "--debug:                      Enable ansible verbose mode (-vvvv connection debugging)"
    echo "--ansible-default-callback:   Use the 'default' Ansible callback plugin instead of the"
    echo "                              tripleo-validations custom callback 'validation_output'"
    echo "--plan:                       Stack name to use for generating the inventory data"
    echo "--validation-name:            The name of the validation"
    echo ""
    exit 1
}

if [[ "$*" =~ "--help" ]]; then
    usage
fi

if [[ "$#" = 0 ]]; then
    usage
fi

while [ $# != 0 ]; do
    case $1 in
        --help|-h)
            usage
            ;;
        --debug)
            DEBUG="yes"
            ;;
        --ansible-default-callback)
            CALLBACK="yes"
            ;;
        --plan)
            PLAN_NAME=$2
            shift
            ;;
        --validation-name)
            VALIDATION=$2
            shift
            ;;
        *)
            echo "invalid arg -- $1"
            usage
            exit 1
            ;;
    esac
    shift
done

if [[ -z $VALIDATION ]]; then
    echo "Missing required validation name file"
    exit 1
fi

ANSIBLE_DEBUG=""

if [ ${DEBUG:-no} == "yes" ]; then
    ANSIBLE_DEBUG="-vvvv"
fi

VALIDATIONS_BASEDIR="/usr/share/openstack-tripleo-validations"

VAL=$(find $VALIDATIONS_BASEDIR/playbooks -type f -regex ".*playbooks\/${VALIDATION}\.y[a]?ml")
if [[ -z ${VAL} ]]; then
    echo "The ${VALIDATION} validation doesn't exist"
    exit 1
fi

# Use custom validation-specific formatter
if [ ${CALLBACK:-no} = "yes" ]; then
    export ANSIBLE_STDOUT_CALLBACK=default
else
    export ANSIBLE_STDOUT_CALLBACK=validation_output
fi
# Disable retry files to avoid messages like this:
# [Errno 13] Permission denied:
# u'/usr/share/openstack-tripleo-validations/validations/*.retry'
export ANSIBLE_RETRY_FILES_ENABLED=false
export ANSIBLE_KEEP_REMOTE_FILES=1

export ANSIBLE_CALLBACK_PLUGINS="${VALIDATIONS_BASEDIR}/callback_plugins"
export ANSIBLE_ROLES_PATH="${VALIDATIONS_BASEDIR}/roles"
export ANSIBLE_LOOKUP_PLUGINS="${VALIDATIONS_BASEDIR}/lookup_plugins"
export ANSIBLE_LIBRARY="${VALIDATIONS_BASEDIR}/library"

# Environment variable is the easiest way to pass variables to an Ansible
# dynamic inventory script
export TRIPLEO_PLAN_NAME=${PLAN_NAME:-overcloud}

# IF running on Undercloud
export ANSIBLE_INVENTORY=$(which tripleo-ansible-inventory)
# IF running on standalone, create a "hosts" file with mandatory [undercloud]
# entry, and pass it in the ANSIBLE_INVENTORY

ansible-playbook ${ANSIBLE_DEBUG} ${VAL}
