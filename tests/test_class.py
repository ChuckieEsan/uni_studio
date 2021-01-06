from studio import create_app
import unittest
import sys
sys.path.append('../')
app = create_app()


class TestThis(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    def tearDown(self):
        pass

    def test_vote_page(self):
        res = self.app.get('/console/vote/populate', follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        res = self.app.get('/console/vote/populate/1', follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        

    def test_issues_page(self):
        res = self.app.get('/issues/')
        self.assertEqual(res.status_code, 200)
        res = self.app.post('/issues/', follow_redirects=True,data={'contact':'test'})
        self.assertEqual(res.status_code,200)



    def test_fileservice(self):
        res = self.app.get('/fileservice/')
        self.assertEqual(res.status_code, 200)
        res = self.app.get('/fileservice/upload')
        self.assertEqual(res.status_code, 200)
