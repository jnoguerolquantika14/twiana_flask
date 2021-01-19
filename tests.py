import twiana
import unittest

class TestTwiana(unittest.TestCase):
    def setUp(self):
        self.num_errors = 0
        self.verificationErrors = []

    def tearDown(self):
        try: self.assertEqual(0, self.num_errors)
        except AssertionError:
            print('Errors:',self.num_errors)
            print(self.verificationErrors)

    def test_from_file(self):
        file="tests_files/users_clasification.txt"
        f = open(file, "r", encoding='utf8')
        lineas = f.read().splitlines()
        f.close()
        for line in lineas:
                words = line.split("|||")
                account=words[0]
                tweets_limit=200
                expected_clasif=words[1]
                user_analysis, worries, clasif, user_data=twiana.twiana(account, tweets_limit)

                try: self.assertEqual(expected_clasif, clasif)
                except AssertionError: 
                    error=str(account)+': resulted '+str(clasif)+'!= expected '+str(expected_clasif)
                    self.verificationErrors.append(error)
        self.num_errors=len(self.verificationErrors)

                
if __name__ == "__main__":
    unittest.main()