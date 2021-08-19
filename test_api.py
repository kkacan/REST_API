import unittest
from main import app
import json

class BasicTestCase(unittest.TestCase):

    def test_tip_proizvoda(self):
        tester = app.test_client(self)
        response = tester.get('/api/v1/tip_proizvoda', query_string={'apikey': 'stipe@gmail.com'}, content_type='html/text')
        self.assertEqual(response.status_code, 200)

    def test_ponuda(self):
        tester = app.test_client(self)
        response = tester.get('/api/v1/ponuda', query_string={'apikey': 'stipe@gmail.com'}, content_type='html/text')
        self.assertEqual(response.status_code, 200)
    
    def test_user_login(self):
        tester = app.test_client(self)
        response = tester.post('/api/v1/login', data=json.dumps(dict(email='stipe@gmail.com', lozinka='lozinka')), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_response['response'], 'Success')

if __name__ == '__main__':
    unittest.main()

    