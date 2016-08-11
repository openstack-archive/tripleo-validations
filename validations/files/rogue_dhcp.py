#!/tmp/validations-venv/bin/python

# -*- coding: utf-8 -*-
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Disable scapy's warning to stderr:
import logging
import sys
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)


from scapy.all import BOOTP
from scapy.all import conf
from scapy.all import DHCP
from scapy.all import Ether
from scapy.all import get_if_raw_hwaddr
from scapy.all import IP
from scapy.all import srp
from scapy.all import UDP


def find_dhcp_servers(timeout_sec, interface):
    conf.checkIPaddr = False
    fam, hw = get_if_raw_hwaddr(interface)
    dhcp_discover = (Ether(dst="ff:ff:ff:ff:ff:ff") /
                     IP(src="0.0.0.0", dst="255.255.255.255") /
                     UDP(sport=68, dport=67) /
                     BOOTP(chaddr=hw) /
                     DHCP(options=[("message-type", "discover"), "end"]))
    ans, unans = srp(dhcp_discover, multi=True,
                     timeout=timeout_sec, verbose=False)

    return [(unicode(packet[1][IP].src), packet[1][Ether].src)
            for packet in ans]


def main():
    dhcp_servers = []
    for interface in sys.argv[1:]:
        dhcp_servers.extend(find_dhcp_servers(30, interface))
    if dhcp_servers:
        sys.stderr.write('Found {} DHCP servers:'.format(len(dhcp_servers)))
        for ip, mac in dhcp_servers:
            sys.stderr.write("\n* {} ({})".format(ip, mac))
        sys.exit(1)
    else:
        print("No DHCP servers found.")


if __name__ == '__main__':
    main()
