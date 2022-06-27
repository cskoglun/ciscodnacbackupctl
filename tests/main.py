import os
import sys
import json
from unittest.mock import patch
import unittest

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import ciscodnacbackupctl


class TestBackend(unittest.TestCase):

    """Mockup settings for backend"""

    os.environ["DNA_CENTER_BASE_URL"] = "mockup-dnac"
    os.environ["DNA_CENTER_USERNAME"] = "mockup-user"
    os.environ["DNA_CENTER_PASSWORD"] = "mockup-pass"
    os.environ["DNA_CENTER_VERIFY"] = "False"

    @staticmethod
    def mockup_response(data):
        with open(f"mockup_data/{data}.json", "r") as f:
            data = json.loads(f.read())
        return data

    """Test mockup user with whoami"""

    @patch("ciscodnacbackupctl.Api._auth")
    def test_whoami(self, auth):
        print("")
        cli = ciscodnacbackupctl.Api.CLI()
        res = cli.whoami()
        self.assertEqual(res, True)
        return

    """ Test list backups """

    @patch("ciscodnacbackupctl.Api._auth")
    def test_list(self, auth):
        print("")
        with patch("ciscodnacbackupctl.Api._request") as api:
            api.return_value = self.mockup_response("list")
            cli = ciscodnacbackupctl.Api.CLI()
            res = cli.list(True)
            self.assertEqual(res, True)
            return
    
    """ Test list backups with Debug enabled """

    @patch("ciscodnacbackupctl.Api._auth")
    def test_list_debug(self, auth):
        print("")
        with patch("ciscodnacbackupctl.Api._request") as api:
            api.return_value = self.mockup_response("list")
            cli = ciscodnacbackupctl.Api.CLI(debug=True)
            res = cli.list(True)
            self.assertEqual(res, True)
            return

    """ Test list history """

    @patch("ciscodnacbackupctl.Api._auth")
    def test_history(self, auth):
        print("")
        with patch("ciscodnacbackupctl.Api._request") as api:
            api.return_value = self.mockup_response("history")
            cli = ciscodnacbackupctl.Api.CLI()
            res = cli.history()
            self.assertEqual(res, True)
            return

    """ Test list progress """

    @patch("ciscodnacbackupctl.Api._auth")
    def test_progress(self, auth):
        print("")
        with patch("ciscodnacbackupctl.Api._request") as api:
            api.return_value = self.mockup_response("progress")
            cli = ciscodnacbackupctl.Api.CLI()
            res = cli.progress()
            self.assertEqual(res, True)
            return

    """ Test create backup """

    @patch("ciscodnacbackupctl.Api._auth")
    def test_create(self, auth):
        print("")
        with patch("ciscodnacbackupctl.Api._request") as api:
            api.return_value = self.mockup_response("create")
            cli = ciscodnacbackupctl.Api.CLI()
            res = cli.create(name="mockup")
            self.assertEqual(res, True)
            return

    """ Test delete one backup """

    @patch("ciscodnacbackupctl.Api._auth")
    def test_delete_working(self, auth):
        print("")
        with patch("ciscodnacbackupctl.Api._request") as api:
            api.return_value = self.mockup_response("delete")
            cli = ciscodnacbackupctl.Api.CLI()
            res = cli.delete("54d7930a-057c-4c41-b35c-30494133234a")
            self.assertEqual(res, True)
            return
    
    """ Test delete multiple backups """

    @patch("ciscodnacbackupctl.Api._auth")
    def test_delete_multi_working(self, auth):
        print("")
        with patch("ciscodnacbackupctl.Api._request") as api:
            api.return_value = self.mockup_response("delete")
            cli = ciscodnacbackupctl.Api.CLI()
            res = cli.delete(["54d7930a-057c-4c41-b35c-30494133234a", "54d7930a-057c-4c41-b35c-30494133234b", "54d7930a-057c-4c41-b35c-30494133234c"])
            self.assertEqual(res, True)
            return
    
    """ Test delete backup with invalid uuid length """

    @patch("ciscodnacbackupctl.Api._auth")
    def test_delete_incorrect_uuid(self, auth):
        print("")
        with patch("ciscodnacbackupctl.Api._request") as api:
            api.return_value = self.mockup_response("delete")
            cli = ciscodnacbackupctl.Api.CLI()
            self.assertRaises(ValueError, cli.delete, "123")
            return
    
    """ Test delete multiple backups with invalid uuid length """

    @patch("ciscodnacbackupctl.Api._auth")
    def test_delete_incorrect_uuids(self, auth):
        print("")
        with patch("ciscodnacbackupctl.Api._request") as api:
            api.return_value = self.mockup_response("delete")
            cli = ciscodnacbackupctl.Api.CLI()
            self.assertRaises(ValueError, cli.delete, ["123", "123", "32553"])
            return
    
    """ Test delete backup with invalid type """

    @patch("ciscodnacbackupctl.Api._auth")
    def test_delete_incorrect_type(self, auth):
        print("")
        with patch("ciscodnacbackupctl.Api._request") as api:
            api.return_value = self.mockup_response("delete")
            cli = ciscodnacbackupctl.Api.CLI()
            self.assertRaises(TypeError, cli.delete, {"id": "dict"})
            return

    """ Test purge incompatible backups """

    @patch("ciscodnacbackupctl.Api._auth")
    def test_purge_incompatible(self, auth):
        print("")
        with patch("ciscodnacbackupctl.Api._request") as api:
            api.return_value = self.mockup_response("list")
            delete_patcher = patch("ciscodnacbackupctl.Api.CLI.delete")
            delete = delete_patcher.start()
            delete.return_value = None
            cli = ciscodnacbackupctl.Api().CLI()
            res = cli.purge(keep=3, incompatible=True, force=True)
            self.assertEqual(res, True)
            delete = delete_patcher.stop()
            return

    """ Test purge keep 3 backups """

    @patch("ciscodnacbackupctl.Api._auth")
    def test_purge_int(self, auth):
        print("")
        with patch("ciscodnacbackupctl.Api._request") as api:
            api.return_value = self.mockup_response("purge")
            delete_patcher = patch("ciscodnacbackupctl.Api.CLI.delete")
            delete = delete_patcher.start()
            delete.return_value = None
            cli = ciscodnacbackupctl.Api().CLI()
            res = cli.purge(keep=3, incompatible=False, force=True)
            self.assertEqual(res, True)
            delete = delete_patcher.stop()
            return

    """ Test purge keep 30 days backups """

    @patch("ciscodnacbackupctl.Api._auth")
    def test_purge_days(self, auth):
        print("")
        with patch("ciscodnacbackupctl.Api._request") as api:
            api.return_value = self.mockup_response("purge")
            delete_patcher = patch("ciscodnacbackupctl.Api.CLI.delete")
            delete = delete_patcher.start()
            delete.return_value = None
            cli = ciscodnacbackupctl.Api().CLI()
            res = cli.purge(keep="30d", incompatible=False, force=True)
            self.assertEqual(res, True)
            delete = delete_patcher.stop()
            return

    """ Test purge no backups to delete """

    @patch("ciscodnacbackupctl.Api._auth")
    def test_purge_no_backups_to_delete(self, auth):
        print("")
        with patch("ciscodnacbackupctl.Api._request") as api:
            api.return_value = self.mockup_response("purge")
            delete_patcher = patch("ciscodnacbackupctl.Api.CLI.delete")
            delete = delete_patcher.start()
            delete.return_value = None
            cli = ciscodnacbackupctl.Api().CLI()
            res = cli.purge(keep="720d", incompatible=False, force=True)
            self.assertEqual(res, False)
            delete = delete_patcher.stop()
            return


if __name__ == "__main__":
    unittest.main(verbosity=3)
