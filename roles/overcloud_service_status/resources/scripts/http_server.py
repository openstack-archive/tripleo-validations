#!/usr/bin/env python3
"""
Simple http server to mock a keystone token and service list.
If arguments are passed, they will either set the services as down
or create additionnal services.

Example:
./http_server.py --scenario default
- will return services based on the 'services' dict below.

./http_server.py --scenario deprecated_services
- will return services based on the 'services' dict below, as well
  as a nova-consoleauth service.

./http_server.py --scenario down_services
- will return services based on the 'services' dict below, as well
  as marking one of the services as down.
"""
import argparse
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
import json

server_port = 8080
server_url = "http://127.0.0.1"

# List of services to mock
# Controllers are going to be created 3 times, computes and hostgroups once
services = {
    "nova": {
        "controller": ["nova-scheduler", "nova-conductor"],
        "compute": ["nova-compute"],
    },
    "cinder": {
        "controller": ["cinder-scheduler"],
        "hostgroup": ["cinder-volume"],
    },
}

parser = argparse.ArgumentParser(description="mocking keystone and os-service calls")
parser.add_argument(
    "--scenario",
    action="store",
    default="default",
    help="Scenario to reproduce",
)
args = parser.parse_args()


class S(BaseHTTPRequestHandler):
    def _set_response(self, code=200, **kwargs):
        self.send_response(code)
        self.send_header("Content-type", "application/json; charset=utf-8")
        for key, val in kwargs.items():
            self.send_header(key, val)
        self.end_headers()

    def _write_body(self, text):
        self.wfile.write(text.encode("utf-8"))

    def do_GET(self):
        self._set_response()
        path_split = self.path.split("/")
        self._write_body(self._generate_services(path_split[1]))

    def do_POST(self):
        content_length = int(self.headers["Content-Length"])
        self._set_response(201, x_subject_token=123)
        self._write_body(self._generate_token())

    def _generate_services(self, service):
        data = {"services": []}
        svc = services[service]
        for key, binaries in svc.items():
            number_of_nodes = 3 if key == "controller" else 1
            for i in range(number_of_nodes):
                for binary in binaries:
                    data["services"].append(
                        self._generate_service(binary, f"{key}-{i}.redhat.local")
                    )
        # NOTE(dvd): yeah this is ugly and won't work if we remove nova-consoleauth
        #            from overcloud_deprecated_services. We should probably just
        #            pass the overcloud_deprecated_services list as an argument to
        #            to make this future proof
        if service == "nova" and args.scenario == "deprecated_services":
            data["services"].extend(
                [
                    self._generate_service(
                        "nova-consoleauth", "controller-0.redhat.local"
                    ),
                    self._generate_service(
                        "nova-consoleauth", "controller-1.redhat.local", "disabled"
                    ),
                    self._generate_service(
                        "nova-consoleauth",
                        "controller-2.redhat.local",
                        "enabled",
                        "down",
                    ),
                ]
            )
        if args.scenario == "down_services":
            data["services"][0]["state"] = "down"

        return json.dumps(data)

    def _generate_service(self, binary, host, status="enabled", state="up"):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return {
            "binary": binary,
            "host": host,
            "status": status,
            "state": state,
            "updated_at": now,
        }

    def _generate_token(self):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data = {
            "token": {
                "catalog": [
                    {
                        "endpoints": [
                            {
                                "url": f"{server_url}:{server_port}/cinder",
                                "interface": "public",
                            },
                            {
                                "url": f"{server_url}:{server_port}/cinder",
                                "interface": "public",
                            },
                            {
                                "url": f"{server_url}:{server_port}/cinder",
                                "interface": "public",
                            },
                        ],
                        "name": "cinderv3",
                    },
                    {
                        "endpoints": [
                            {
                                "url": f"{server_url}:{server_port}/nova",
                                "interface": "public",
                            },
                            {
                                "url": f"{server_url}:{server_port}/nova",
                                "interface": "public",
                            },
                            {
                                "url": f"{server_url}:{server_port}/nova",
                                "interface": "public",
                            },
                        ],
                        "name": "nova",
                    },
                ],
            }
        }
        return json.dumps(data)


def run(server_class=HTTPServer, handler_class=S, port=server_port):
    server_address = ("", port)
    httpd = server_class(server_address, handler_class)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()


if __name__ == "__main__":
    run()
