import unittest
from unittest.mock import patch, Mock
from ai.drone_os_status import get_status


class DroneOSStatusTest(unittest.IsolatedAsyncioTestCase):

    @patch("ai.drone_os_status.fetch_drone_with_drone_id")
    def test_status_no_drone(self, fetch_drone_with_drone_id):
        # setup
        fetch_drone_with_drone_id.return_value = None

        # run
        status = get_status('9814', 782638723)

        # assert
        self.assertIsNone(status)
        fetch_drone_with_drone_id.assert_called_once_with('9814')

    @patch("ai.drone_os_status.get_trusted_users")
    @patch("ai.drone_os_status.fetch_drone_with_drone_id")
    def test_status_not_trusted(self, fetch_drone_with_drone_id, get_trusted_users):
        # setup
        drone = Mock()
        drone.id = 7263486234

        fetch_drone_with_drone_id.return_value = drone
        get_trusted_users.return_value = []

        # run
        status = get_status('9813', 782638723)

        # assert
        self.assertIsNotNone(status)
        self.assertEqual("You are not registered as a trusted user of this drone.", status.description)
        fetch_drone_with_drone_id.assert_called_once_with('9813')
        get_trusted_users.assert_called_once_with(drone.id)

    @patch("ai.drone_os_status.get_trusted_users")
    @patch("ai.drone_os_status.fetch_drone_with_drone_id")
    def test_status(self, fetch_drone_with_drone_id, get_trusted_users):
        # setup
        drone = Mock()
        drone.id = 7263486234
        drone.optimized = True
        drone.glitched = False
        drone.id_prepending = False
        drone.battery_minutes = 300

        fetch_drone_with_drone_id.return_value = drone
        requesting_user_id = 782638723
        get_trusted_users.return_value = [requesting_user_id]

        # run
        status = get_status('9813', requesting_user_id)

        # assert
        self.assertIsNotNone(status)
        self.assertEqual("You are registered as a trusted user of this drone and have access to its data.", status.description)
        self.assertEqual("Optimized", status.fields[0].name)
        self.assertEqual("Enabled", status.fields[0].value)
        self.assertEqual("Glitched", status.fields[1].name)
        self.assertEqual("Disabled", status.fields[1].value)
        self.assertEqual("ID prepending required", status.fields[2].name)
        self.assertEqual("Disabled", status.fields[2].value)

        fetch_drone_with_drone_id.assert_called_once_with('9813')
        get_trusted_users.assert_called_once_with(drone.id)
