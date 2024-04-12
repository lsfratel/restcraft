import unittest

from restipy.core.response import Response
from restipy.routing import HTTP_STATUS_LINES


class TestResponse(unittest.TestCase):
    data = {'firstname': 'john', 'lastname': 'doe'}
    headers = {'header-1': '1', 'header-3': 4}

    def setUp(self) -> None:
        self.resp = Response(
            body=self.data.copy(), status_code=404, headers=self.headers.copy()
        )

    def test_response_header_list(self):
        header_list = [
            ('content-type', 'application/json; charset=utf-8'),
            ('header-1', '1'),
            ('header-3', '4'),
        ]
        self.assertListEqual(self.resp.header_list, header_list)

    def test_response_header(self):
        self.assertEqual(self.resp.header['header-1'], '1')
        self.assertEqual(self.resp.header['header-3'], 4)
        self.assertEqual(
            self.resp.header['content-type'], 'application/json; charset=utf-8'
        )

    def test_response_status(self):
        self.assertEqual(self.resp.status, 404)

    def test_response_status_line(self):
        self.assertEqual(
            self.resp.status_line, HTTP_STATUS_LINES[self.resp.status]
        )

    def test_response_set_status(self):
        self.resp.set_status = 200
        self.assertEqual(self.resp.status, 200)
        self.assertEqual(
            self.resp.status_line, HTTP_STATUS_LINES[self.resp.status]
        )

    def test_response_set_status_error(self):
        with self.assertRaises(Exception) as e:
            self.resp.set_status = 9090
        ex = e.exception
        self.assertEqual(str(ex), 'Invalid status code.')

    def test_response_data(self):
        self.assertDictEqual(self.resp.data, self.data)
