import unittest



class TestMain(unittest.TestCase):

    def test_test():
        self.assertEqual('hi', 'hi')


    def test_new():
        self.assertEqual('a', 'b')


    def setUp():
        pass


    def tearDown():
        pass   


if __name__ == '__main__':
    unittest.main()