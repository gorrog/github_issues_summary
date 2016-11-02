import unittest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
import time

from settings import SECRET_TOKEN


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
            if gh_number.text == '720':
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

        # She then clicks the 'login' button.
        login_button = self.browser.find_element_by_id("log_in_button")
        login_button.click()
        time.sleep(30)

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
        token_input.send_keys(SECRET_TOKEN)
        token_input.send_keys(Keys.ENTER)
        time.sleep(60)


        # The page refreshes. Sue wonders if she logged on successfully, but
        # then she sees that where the login form was, there is now a message
        # saying "You are logged in"
        logged_in_legend = self.browser.find_element_by_css_selector(
                "form#authenticate_form legend"
                )
        self.assertEqual("You are logged in",logged_in_legend.text)

    def test_login_page_shows_all_data(self):
        # Set up
        self.browser.get("http://localhost/cgi-bin/github_issues_summary.py")
        token_input = self.browser.find_element_by_css_selector(
            "form#authenticate_form input"
            )
        token_input.click()
        token_input.send_keys(SECRET_TOKEN)
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
        token_input.send_keys(SECRET_TOKEN)
        token_input.send_keys(Keys.ENTER)
        time.sleep(60)

        # After logging in, Sue notices that there is now a form titled "Create
        # New Issue"
        new_issue_legend = self.browser.find_element_by_css_selector(
                "form#new_issue_form fieldset legend"
                )
        self.assertEqual("Create a New Issue",new_issue_legend.text)

        # Sue realises that she can create a new issue by filling out the
        # fields and hitting the 'Create New Issue' button. She starts by
        # selecting 'Client ZZ' from the Client drop down list.
        client_select = Select(self.browser.find_element_by_id("client_input"))
        client_select.select_by_visible_text("Client ZZ")

        # She enters "Heading is wrong colour" in the Action Item/Request
        # field
        action_field = self.browser.find_element_by_id("action_input")
        action_field.send_keys("Heading is wrong colour")

        # She enters "Client requested that the header be in blue, but it is
        # currently red. Please change it to a dark blue" in the Description
        # field
        description_field = self.browser.find_element_by_id(
                "description_input"
                )
        description_field.send_keys("""
                Client requested that the header be in blue, but it is
                currently red. Please change it to a dark blue
                """)


        # This is an urgent issue, so Sue selects "High" from the priority
        # picker
        priority_select = Select(
                self.browser.find_element_by_id("priority_input")
                )
        priority_select.select_by_visible_text("High")

        # This is a bug report, so Sue "bug" from the category picker
        category_select = Select(self.browser.find_element_by_id(
            "category_input"
            ))
        category_select.select_by_visible_text("bug")

        # Since 'gorrog' is the person responsible for front end work, she puts
        # his github username in the 'Assigned To' field
        assigned_field = self.browser.find_element_by_id(
                "assigned_input"
                )
        assigned_field.send_keys("gorrog")

        # Finally, Sue selects 'Backlog' from the status picker
        status_select = Select(self.browser.find_element_by_id("status_input"))
        status_select.select_by_visible_text("Backlog")

        # Sue clicks the 'Create Issue' button.
        create_issue_button = self.browser.find_element_by_id(
                "new_issue_submit_button"
                )
        create_issue_button.click()
        time.sleep(60)

        # The page updates. Sue isn't immediately sure if her submission has
        # worked, but then she sees a message saying 'Your issue was added
        # successfully'
        new_issue_success_message = self.browser.find_element_by_id(
                "new_issue_success_message"
                )
        self.assertEqual(
                "Your issue has been successfully added.",
                new_issue_success_message.text
                )

        # On closer inspection, Sue realises that her issue has been added to
        # the list
        actions = self.browser.find_elements_by_class_name(
                'action'
                )
        search_string_present = False
        for action in actions:
            if action.text == "Heading is wrong colour":
                search_string_present = True
        self.assertTrue(search_string_present)

    def test_log_off(self):
        # Satisfied that her work for the day is done, Sue closes her browser.

        # Five minutes later, Sue realises that she forgot to click the Log Off
        # button. She becomes anxious that the system might still be logged on.

        # She opens up the URL again, and notices that the system seems to have
        # logged her off, because the "Log In to Add/Modify Issues" form is
        # displayed.
        self.browser.get("http://localhost/cgi-bin/github_issues_summary.py")
        log_in_legend = self.browser.find_element_by_css_selector(
                "form#authenticate_form legend"
                )
        self.assertIn("Log in",log_in_legend.text)

        # Being a cautious person though, Sue decides that she had better log
        # on again and click the Log Off button to be 100% sure. She enters her
        # username and presses tab to get to the next field.

        # She enters her token and clicks the 'Log In' button.
        token_input = self.browser.find_element_by_css_selector(
            "form#authenticate_form input"
            )
        token_input.click()
        token_input.send_keys(SECRET_TOKEN)
        token_input.send_keys(Keys.ENTER)
        time.sleep(60)

        # As before, the page refreshes. The 'Log Out' button is visible. Sue
        # clicks the button.
        log_out_button = self.browser.find_element_by_id(
            "logout_button"
            )
        log_out_button.click()

        # The page refreshes and the "Log In to Add/Modify Issues" form is
        # again visible. Sue is satisfied that she has logged off properly, so
        # she closes her web browser.
        log_in_legend = self.browser.find_element_by_css_selector(
                "form#authenticate_form legend"
                )
        self.assertIn("Log in",log_in_legend.text)

if __name__ == "__main__":
    unittest.main()
