import unittest
from bs4 import BeautifulSoup
import requests

GITHUB_ISSUES_SUMMARY_URL = "http://localhost/cgi-bin/github_issues_summary.py"

class AnonymousTableTest(unittest.TestCase):
    html = requests.get(GITHUB_ISSUES_SUMMARY_URL).text
    soup = BeautifulSoup(html,"lxml")
    table = soup.find_all(id='issues_table')
    tbody = table[0].tbody
    rows = tbody.find_all('tr')


    def setUp(self):
        pass

    def test_table_has_correct_number_of_cells_per_row(self):
        # There should be exactly 9 cells of data per row
        # when not logged in
        for row in self.rows:
            cells = row.find_all('td')
            self.assertEqual(len(cells),9)

    def test_column_4_contains_numberical_data_only(self):
        # Column 4 is for Github Number. This data should always
        # be numerical
        for row in self.rows:
            cells = row.find_all('td')
            self.assertTrue(cells[3].text.strip().isnumeric())


if __name__ == '__main__':
    unittest.main()
