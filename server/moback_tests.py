import moback
import unittest
import json
from moback_utils import make_query
import uuid


class MobackTestCase(unittest.TestCase):
    def setUp(self):
        self.app = moback.app.test_client()

    def test_index(self):
        '''Testing Server Connection...'''
        r = self.app.get('/')
        jsonData = json.loads(r.data)
        self.assertEqual(jsonData['success'], True)

    def test_score(self):
        '''Testing insertion of score'''
        data = dict(
                duration=5,
                difficulty='hard',
                practice_point=100,
                speed=0.2,
                accuracy=70,
                access_token=uuid.uuid1(),
                id=uuid.uuid1()
                )
        r = self.app.post(make_query('/api/v1/point', data))

    def test_get_scores(self):
        '''Testing getting scores from thje user'''
        data = dict(
                person_id='1',
                access_token='f830f634-cc22-5fc2-b7d1-ca07353faa95'
                )
        r = self.app.get(make_query('/api/v1/point', data))
        print r.data
if __name__ == '__main__':
    unittest.main()
