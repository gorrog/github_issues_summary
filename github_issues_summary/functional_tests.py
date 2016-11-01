import unittest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time


class SueVisitorTest(unittest.TestCase):
    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(10)

    def tearDown(self):
        self.browser.quit()

    def test_page_components_are_present(self):
        # Sue is tasked with keeping track of the issues in her company's
        # Github repository. She remembers that there is a specific company
        # webapp for that. She navigates to the URL that she was given.
        self.browser.get("http://localhost/cgi-bin/github_issues_summary.py")

        # She notices that the title of the web page has the words "Github 
        # Issues Summary" and mentions the name of the Github Repo
        self.assertIn("Github Issues Summary", self.browser.title)
        self.assertIn("GitIntegration", self.browser.title)

        # Sue can see a table summarising all the issues preceded by a heading
        # that says 'Github issues'.
        main_heading = self.browser.find_element_by_css_selector(
                "section#main_content h1"
                )
        self.assertIn("Github Issues", main_heading.text)
        self.browser.find_element_by_id(
                "issues_table"
                )

        # The table of issues has a number of useful standard columns. There is
        # a column for Client Name
        client_column = self.browser.find_element_by_id(
                "client_column"
                )
        self.assertEqual(client_column.text, "Client Name")

        # There is a column for Action item/Request
        action_column = self.browser.find_element_by_id(
                "action_column"
                )
        self.assertEqual(action_column.text, u"Action item/Request")

        # There is a column for Description
        description_column = self.browser.find_element_by_id(
                "description_column"
                )
        self.assertEqual(description_column.text, "Description")

        # There is a column for GH Number
        gh_column = self.browser.find_element_by_id(
                "gh_column"
                )
        self.assertEqual(gh_column.text, "GH number")

        # There is a column for Priority
        priority_column = self.browser.find_element_by_id(
                "priority_column"
                )
        self.assertEqual(priority_column.text, "Priority")

        # There is a column for Category
        category_column = self.browser.find_element_by_id(
                "category_column"
                )
        self.assertEqual(category_column.text, "Category")

        # There is a column for Assigned To
        assigned_column = self.browser.find_element_by_id(
                "assigned_column"
                )
        self.assertEqual(assigned_column.text, "Assigned To")

        # There is a column for Comments
        comments_column = self.browser.find_element_by_id(
                "comments_column"
                )
        self.assertEqual(comments_column.text, "Comments")

        # There is a column for Status
        status_column = self.browser.find_element_by_id(
                "status_column"
                )
        self.assertEqual(status_column.text, "Status")

    def test_data_is_present(self):
        # Set Up
        self.browser.get("http://localhost/cgi-bin/github_issues_summary.py")

        # Sue scans down the table to find recent issue number 657 which she is
        # interested in. 
        gh_numbers = self.browser.find_elements_by_class_name(
                'gh_number'
                )
        number_present = False
        for gh_number in gh_numbers:
            if gh_number.text == '657':
                number_present = True
        self.assertTrue(number_present)

        # Sue notices that there are only a limited number of items per page,
        # but fortunately there are links to access subsequent pages.
        # Sue wonders what the first posted issue was so she clicks on the link
        # to the last page.
        last_link = self.browser.find_element_by_link_text("Last Page")
        last_link.click()

        # The last page is displayed, and she can now see the very first item,
        # number 1.
        gh_numbers = self.browser.find_elements_by_class_name(
                'gh_number'
                )
        number_present = False
        for gh_number in gh_numbers:
            if gh_number.text == '1':
                number_present = True
        self.assertTrue(number_present)

    def test_login(self):
        # Set Up
        self.browser.get("http://localhost/cgi-bin/github_issues_summary.py")
        last_link = self.browser.find_element_by_link_text("Last Page")
        last_link.click()

        # Sue can't see any way to edit the information shown and wonders if
        # she needs to be authorised to make changes. Then she notices a small
        # form at the top of the page with the legend "Log In to Add a new
        # issue or view all issues on a single page".
        log_in_legend = self.browser.find_element_by_css_selector(
                "form#authenticate_form legend"
                )
        self.assertIn("Log in",log_in_legend.text)

        # Sue clicks in the token field and enters a token incorrectly.
        token_input = self.browser.find_element_by_css_selector(
            "form#authenticate_form input"
            )
        token_input.click()
        token_input.send_keys("bobobobo")
        time.sleep(30)

        # She then clicks the 'login' button.
        login_button = self.browser.find_element_by_id("log_in_button")
        login_button.click()

        # The page refreshes and at the top, a message tells her that the token
        # that she entered is not valid
        token_error_message = self.browser.find_element_by_css_selector(
                "section.error p.error_message"
                )
        self.assertIn("token does not appear to be valid",
                token_error_message.text)

        # Sue realises that she entered an old expired token. She corrects this
        # error and hits enter.
        token_input = self.browser.find_element_by_css_selector(
            "form#authenticate_form input"
            )
        token_input.click()
        token_input.send_keys("a229810bfb81a78cc28a802a7bdbe32cd9860d26")
        token_input.send_keys(Keys.ENTER)
        time.sleep(60)


        # The page refreshes. Sue wonders if she logged on successfully, but
        # then she sees that where the login form was, there is now a message
        # saying "You are currently logged in"
        logged_in_legend = self.browser.find_element_by_css_selector(
                "form#authenticate_form legend"
                )
        self.assertEqual("You are currently logged in",logged_in_legend.text)

    def test_login_page_shows_all_data(self):
        # Set up
        self.browser.get("http://localhost/cgi-bin/github_issues_summary.py")
        token_input = self.browser.find_element_by_css_selector(
            "form#authenticate_form input"
            )
        token_input.click()
        token_input.send_keys("a229810bfb81a78cc28a802a7bdbe32cd9860d26")
        token_input.send_keys(Keys.ENTER)
        time.sleep(60)

        # Sue can now see all the issues on one page. She is happy about this
        # and scrolls down to see if issue 1 is present.
        gh_numbers = self.browser.find_elements_by_class_name(
                'gh_number'
                )
        number_present = False
        for gh_number in gh_numbers:
            if gh_number.text == '1':
                number_present = True
        self.assertTrue(number_present)

        # She then scrolls back up to make sure that a recent issue, number 709
        # is also present.
        for gh_number in gh_numbers:
            if gh_number.text == '709':
                number_present = True
        self.assertTrue(number_present)

    def test_adding_new_issue(self):
        # Set up
        self.browser.get("http://localhost/cgi-bin/github_issues_summary.py")
        token_input = self.browser.find_element_by_css_selector(
            "form#authenticate_form input"
            )
        token_input.click()
        token_input.send_keys("a229810bfb81a78cc28a802a7bdbe32cd9860d26")
        token_input.send_keys(Keys.ENTER)
        time.sleep(60)

        # After logging in, Sue notices that there is now a form titled "Create
        # New Issue"
        new_issue_legend = self.browser.find_element_by_css_selector(
                "form#new_issue_form fieldset legend"
                )
        self.assertEqual("Create a New Issue",new_issue_legend.text)

        # Sue realises that she can create a new issue by filling out the
        # fields and hitting the 'Create New Issue' button. She fills out the
        # 'Action item/Request' field.
        self.fail("Finish the test")

        # Sue clicks the 'Create Issue' button, but her browser warns her that
        # there are mandatory fields that she needs to fill out.  TODO: write
        # tests for mandatory fields.
        self.fail("Finish the test")

        # Sue fills out the last mandatory field
        self.fail("Finish the test")

        # Sue clicks the 'Create Issue' button.
        self.fail("Finish the test")

        # The page updates, and now Sue's issue appears in the list.
        self.fail("Finish the test")

        # Sue realises that she made a mistake with her submission. She changes
        # one of the fields
        self.fail("Finish the test")

        # Sue clicks the 'Update' button.
        self.fail("Finish the test")

        # The page refreshes and Sue can see that the change has persisted.
        self.fail("Finish the test")

        # Satisfied that her work for the day is done, Sue closes her browser.
        self.fail("Finish the test")

        # Five minutes later, Sue realises that she forgot to click the Log Off
        # button. She becomes anxious that the system might still be logged on.
        self.fail("Finish the test")

        # She opens up the URL again, and notices that the system seems to have
        # logged her off, because the "Log In to Add/Modify Issues" form is
        # displayed.
        self.fail("Finish the test")

        # Being a cautious person though, Sue decides that she had better log
        # on again and click the Log Off button to be 100% sure. She enters her
        # username and presses tab to get to the next field.
        self.fail("Finish the test")

        # She enters the password and presses the 'Log In' button.
        self.fail("Finish the test")

        # As before, the page refreshes. The 'Log Out' button is visible. Sue
        # clicks the button.
        self.fail("Finish the test")

        # The page refreshes and the "Log In to Add/Modify Issues" form is
        # again visible. Sue is satisfied that she has logged off properly, so
        # she closes her web browser.
        self.fail("Finish the test")

if __name__ == "__main__":
    unittest.main()
