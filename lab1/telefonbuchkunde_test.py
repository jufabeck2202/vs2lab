import os
import unittest
import telefonbuch
import kunde
import lab_logging
import json
lab_logging.setup()
class TestServerClient(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.server = telefonbuch.Server()
        pid = os.fork()
        if pid == 0:
            self.server.serve()
            os._exit(0)
        self.user = kunde.User()

    def test_srv_get(self):
        number = self.user.get_user("henning")
        self.assertEqual(number, '12345')
        all = self.user.get_all()
        self.assertEqual(all, {
        "henning": "12345",
        "tobias": "31313131",
        "julian": "1001"
        })

        print(all)
        self.user.client_close()
        user1 = kunde.User()
        self.server.close()




if __name__ == '__main__':
    unittest.main()
