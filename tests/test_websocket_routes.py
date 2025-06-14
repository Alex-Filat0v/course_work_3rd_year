import pytest


def test_connection_manager():
    from server.routes.websocket_routes import ConnectionManager
    cm = ConnectionManager()
    assert isinstance(cm.active_connections, dict)
