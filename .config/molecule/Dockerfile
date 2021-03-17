# Molecule managed
# Copyright 2021 Red Hat, Inc.
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.


{% if item.registry is defined %}
FROM {{ item.registry.url }}/{{ item.image }}
{% else %}
FROM {{ item.image }}
{% endif %}

RUN dnf makecache && dnf install -y sudo python*-devel python*-dnf bash {{ item.pkg_extras | default('') }}
# TODO(gchamoul): find a better to get always the latest version of those rpms
# below from the centos mirror
RUN dnf install -y http://mirror.centos.org/centos/8/BaseOS/x86_64/os/Packages/centos-gpg-keys-8-2.el8.noarch.rpm
RUN dnf install -y http://mirror.centos.org/centos/8/BaseOS/x86_64/os/Packages/centos-linux-repos-8-2.el8.noarch.rpm && dnf install -y epel-release && dnf clean all

{% for pkg in item.easy_install | default([]) %}
# install pip for centos where there is no python-pip rpm in default repos
RUN easy_install {{ pkg }}
{% endfor %}

CMD ["sh", "-c", "while true; do sleep 10000; done"]
