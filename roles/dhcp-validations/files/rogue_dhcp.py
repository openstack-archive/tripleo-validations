#!/usr/bin/env python
# Copyright 2017 Red Hat, Inc.
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
import fcntl
import six
import socket
import struct
import sys
import threading
import time

ETH_P_IP = 0x0800
SIOCGIFHWADDR = 0x8927

dhcp_servers = []
interfaces_addresses = {}


class DHCPDiscover(object):
    def __init__(self, interface):
        self.interface = interface
        self.mac = interfaces_addresses[interface]
        self.socket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW)

    def bind(self):
        self.socket.bind((self.interface, 0))

    def send(self):
        packet = self.packet()
        self.bind()
        self.socket.send(packet)

    def close_socket(self):
        self.socket.close()

    def packet(self):
        return self.ethernet_header() \
            + self.ip_header() \
            + self.udp_header() \
            + self.dhcp_discover_payload()

    def ethernet_header(self):
        return struct.pack('!6s6sH',
                           b'\xff\xff\xff\xff\xff\xff',  # Dest HW address
                           self.mac,                     # Source HW address
                           ETH_P_IP)                     # EtherType - IPv4

    def ip_header(self, checksum=None):
        # 0                   1                   2                   3
        # 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
        # +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
        # |Version|  IHL  |Type of Service|          Total Length         |
        # +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
        # |         Identification        |Flags|      Fragment Offset    |
        # +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
        # |  Time to Live |    Protocol   |         Header Checksum       |
        # +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
        # |                       Source Address                          |
        # +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
        # |                    Destination Address                        |
        # +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
        # |                    Options                    |    Padding    |
        # +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
        if checksum is None:
            checksum = self.ip_checksum()
        return struct.pack('!BBHHHBBHI4s',
                           (4 << 4) + 5,  # IPv4 + 20 bytes header length
                           0,             # TOS
                           272,           # Total Length
                           1,             # Id
                           0,             # Flags & Fragment Offset
                           64,            # TTL
                           socket.IPPROTO_UDP,
                           checksum,
                           0,             # Source
                           socket.inet_aton('255.255.255.255'))  # Destination

    def ip_checksum(self):
        generated_checksum = self._checksum(self.ip_header(checksum=0))
        return socket.htons(generated_checksum)

    def udp_header(self, checksum=None):
        #  0      7 8     15 16    23 24    31
        # +--------+--------+--------+--------+
        # |     Source      |   Destination   |
        # |      Port       |      Port       |
        # +--------+--------+--------+--------+
        # |                 |                 |
        # |     Length      |    Checksum     |
        # +--------+--------+--------+--------+
        if checksum is None:
            checksum = self.udp_checksum()
        return struct.pack('!HHHH',
                           68,
                           67,
                           252,
                           checksum)

    def udp_checksum(self):
        pseudo_header = self.ip_pseudo_header()
        generated_checksum = self._checksum(pseudo_header + self.udp_header(
            checksum=0) + self.dhcp_discover_payload())
        return socket.htons(generated_checksum)

    def ip_pseudo_header(self):
        #  0      7 8     15 16    23 24    31
        # +--------+--------+--------+--------+
        # |          source address           |
        # +--------+--------+--------+--------+
        # |        destination address        |
        # +--------+--------+--------+--------+
        # |  zero  |protocol|   UDP length    |
        # +--------+--------+--------+--------+
        return struct.pack('!I4sBBH',
                           0,
                           socket.inet_aton('255.255.255.255'),
                           0,
                           socket.IPPROTO_UDP,
                           252)  # Length

    def dhcp_discover_payload(self):
        return struct.pack('!BBBBIHHIIII6s10s67s125s4s3s1s',
                           1,                    # Message Type - Boot Request
                           1,                    # Hardware Type - Ethernet
                           6,                    # HW Address Length
                           0,                    # Hops
                           0,                    # Transaction ID
                           0,                    # Seconds elapsed
                           0,                    # Bootp flags
                           0,                    # Client IP Address
                           0,                    # Your IP Address
                           0,                    # Next server IP Address
                           0,                    # Relay Agent IP Address
                           self.mac,             # Client MAC address
                           b'\x00' * 10,         # Client HW address padding
                           b'\x00' * 67,         # Server host name not given
                           b'\x00' * 125,        # Boot file name not given
                           b'\x63\x82\x53\x63',  # Magic Cookie
                           b'\x35\x01\x01',      # DHCP Message Type = Discover
                           b'\xff'               # Option End
                           )

    def _checksum(self, msg):
        s = 0
        for i in range(0, len(msg), 2):
            if six.PY3:
                w = msg[i] + (msg[i + 1] << 8)
            else:
                w = ord(msg[i]) + (ord(msg[i + 1]) << 8)
            s = s + w
        s = (s >> 16) + (s & 0xffff)
        s = s + (s >> 16)
        s = ~s & 0xffff
        return s


def get_hw_addresses(interfaces):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    for interface in interfaces:
        info = fcntl.ioctl(s.fileno(),
                           SIOCGIFHWADDR,
                           struct.pack('256s', interface[:15].encode('utf-8')))
        interfaces_addresses[interface] = info[18:24]
    s.close()


def inspect_frame(data):
    eth_type = struct.unpack('!H', data[12:14])[0]
    protocol = data[23] if six.PY3 else ord(data[23])
    src_port = struct.unpack('!H', data[34:36])[0]
    dst_port = struct.unpack('!H', data[36:38])[0]
    msg_type = data[42] if six.PY3 else ord(data[42])
    # Make sure we got a DHCP Offer
    if eth_type == ETH_P_IP \
            and protocol == socket.IPPROTO_UDP \
            and src_port == 67 \
            and dst_port == 68 \
            and msg_type == 2:  # DHCP Boot Reply
        if six.PY3:
            server_ip_address = '.'.join(["%s" % m for m in
                                         data[26:30]])
            server_hw_address = ":".join(["%02x" % m for m in
                                         data[6:12]])
        else:
            server_ip_address = '.'.join(["%s" % ord(m) for m in
                                         data[26:30]])
            server_hw_address = ":".join(["%02x" % ord(m) for m in
                                         data[6:12]])
        dhcp_servers.append([server_ip_address, server_hw_address])


def wait_for_dhcp_offers(interfaces, timeout):
    listening_socket = socket.socket(socket.PF_PACKET, socket.SOCK_RAW,
                                     socket.htons(ETH_P_IP))
    listening_socket.settimeout(timeout)
    allowed_macs = interfaces_addresses.values()
    end_of_time = time.time() + timeout
    try:
        while time.time() < end_of_time:
            data = listening_socket.recv(1024)
            dst_mac = struct.unpack('!6s', data[0:6])[0]
            if dst_mac in allowed_macs:
                inspect_frame(data)
    except socket.timeout:
        pass
    listening_socket.close()


def main():
    interfaces = sys.argv[1:]
    timeout = 5

    get_hw_addresses(interfaces)

    listening_thread = threading.Thread(target=wait_for_dhcp_offers,
                                        args=[interfaces, timeout])
    listening_thread.start()

    for interface in interfaces:
        dhcp_discover = DHCPDiscover(interface)
        dhcp_discover.send()
        dhcp_discover.close_socket()

    listening_thread.join()

    if dhcp_servers:
        sys.stderr.write('Found {} DHCP servers:'.format(len(dhcp_servers)))
        for ip, mac in dhcp_servers:
            sys.stderr.write("\n* {} ({})".format(ip, mac))
        sys.exit(1)
    else:
        print("No DHCP servers found.")


if __name__ == '__main__':
    main()
