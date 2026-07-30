"""Implements BE-050: zero outbound network requests.

Patches socket-level connection functions to raise on any non-loopback
target, then exercises every endpoint. This catches an accidental outbound
call (a stray HTTP client, a DNS lookup for an external host) at the network
layer, not just by trusting that the code review didn't miss one.
"""

from __future__ import annotations

import socket

import pytest
from fastapi.testclient import TestClient

from dashboard.server.app import create_app

LOOPBACK_HOSTS = {"127.0.0.1", "::1", "localhost"}


@pytest.fixture(autouse=True)
def block_non_loopback_egress(monkeypatch):
    real_create_connection = socket.create_connection

    def guarded_create_connection(address, *args, **kwargs):
        host = address[0] if isinstance(address, tuple) else address
        if host not in LOOPBACK_HOSTS:
            raise AssertionError(f"blocked outbound connection attempt to {host!r} (BE-050 violation)")
        return real_create_connection(address, *args, **kwargs)

    monkeypatch.setattr(socket, "create_connection", guarded_create_connection)

    real_getaddrinfo = socket.getaddrinfo

    def guarded_getaddrinfo(host, *args, **kwargs):
        if host not in LOOPBACK_HOSTS and host is not None:
            raise AssertionError(f"blocked DNS lookup for {host!r} (BE-050 violation)")
        return real_getaddrinfo(host, *args, **kwargs)

    monkeypatch.setattr(socket, "getaddrinfo", guarded_getaddrinfo)


def test_no_outbound_calls_across_all_endpoints(dashboard_config_file):
    app = create_app(config_path=str(dashboard_config_file))
    client = TestClient(app)

    for path in ("/log", "/tasks", "/config", "/stats", "/panes"):
        response = client.get(path)
        assert response.status_code == 200
