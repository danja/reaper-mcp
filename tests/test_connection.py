import unittest
from unittest.mock import patch

from reaper_mcp import connection


class ConnectionTests(unittest.TestCase):
    def setUp(self):
        connection._connected = False
        self.original_enum_projects = getattr(connection.RPR, "EnumProjects", None)

    def tearDown(self):
        connection._connected = False
        if self.original_enum_projects is None:
            try:
                delattr(connection.RPR, "EnumProjects")
            except AttributeError:
                pass
        else:
            connection.RPR.EnumProjects = self.original_enum_projects

    def test_reconnects_when_api_was_imported_offline(self):
        try:
            delattr(connection.RPR, "EnumProjects")
        except AttributeError:
            pass

        def reconnect():
            connection.RPR.EnumProjects = object()

        with patch.object(connection.reapy, "reconnect", side_effect=reconnect) as recovery:
            with patch.object(connection.reapy, "connect") as normal_connect:
                connection.ensure_connected()

        recovery.assert_called_once_with()
        normal_connect.assert_not_called()
        self.assertTrue(connection._connected)

    def test_uses_normal_connection_when_api_is_available(self):
        connection.RPR.EnumProjects = object()

        with patch.object(connection.reapy, "connect") as normal_connect:
            with patch.object(connection.reapy, "reconnect") as recovery:
                connection.ensure_connected()

        normal_connect.assert_called_once_with()
        recovery.assert_not_called()
        self.assertTrue(connection._connected)

    def test_rejects_incomplete_reconnection(self):
        try:
            delattr(connection.RPR, "EnumProjects")
        except AttributeError:
            pass

        with patch.object(connection.reapy, "reconnect"):
            with self.assertRaisesRegex(RuntimeError, "Cannot connect to REAPER"):
                connection.ensure_connected()

        self.assertFalse(connection._connected)


if __name__ == "__main__":
    unittest.main()
