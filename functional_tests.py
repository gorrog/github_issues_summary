import unittest
from selenium import webdriver


class SueVisitorTest(unittest.TestCase):
    def setUp(self):
        self.browser = webdriver.Firefox()

    def tearDown(self):
        self.browser.quit()

    def test_page_components_are_present(self):
	# Sue is tasked with keeping track of the issues in her company's Github 
	# repository. She remembers that there is a specific company webapp for
	# that. She navigates to the URL that she was given.
        self.browser.get("http://localhost:8000")

	# She notices that the title of the web page mirrors the name of the
	# Github repo being used.

	# Sue can see a table summarising all the issues preceded by a heading
	# that says 'Github issues'.

	# The table of issues has a number of useful standard columns. There is a
	# column for Client Name

	# There is a column for Action item/Request

	# There is a column for Description

	# There is a column for GH Number

	# There is a column for Priority

	# There is a column for Category

	# There is a column for Assigned To

	# There is a column for Comments

	# There is a column for Status

	# Sue can't see any way to edit the information shown and wonders if she
	# needs to be authorised to make changes. Then she notices a small form
	# at the top of the page with the legend "Log In to Add/Modify Issues".

	# Sue clicks in the username field and enters the username.
	# TODO: check these field names

	# Sue clicks the 'login' button, but nothing happens because her browser
	# tells her to fill in the password field as well

	# Sue clicks in the password field and enters the password, incorrectly.

	# She then clicks the 'login' button.

	# The page refreshes and at the top, a message tells her that either her
	# username or password is incorrect.

	# Sue realises that she had Caps lock on when entering her password. She
	# corrects this error and hits enter.

	# The page refreshes. Sue wonders if she logged on successfully, but then
	# she sees a button labelled 'Log Off', so she knows she did.

	# After logging in, Sue notices that there is now also a column called
	# 'Action' containing buttons. Sue is curious about what this column is
	# for.

	# Sue notices that all the fields in the issues table are now editable!
	# She is happy about this, because one of the existing issues has a
	# spelling mistake that she wants to correct. She corrects the spelling
	# mistake and then realises that the 'action' column allows actions to be
	# performed on each row.

	# She clicks the 'update' button to the right of her updated row.

	# The page updates and Sue can see that the change she made has been
	# preserved. Satisfied that updates are working, Sue now wonders if the
	# system allows for new entries.

	# Sue notices that the top row of the table is empty and that the action
	# button on the right is labelled 'create issue'.

	# Sue realises that she can create a new issue by filling out the fields
	# and hitting the 'update button'. She fills out the
	# 'Action item/Request' field.

	# Sue clicks the 'Create Issue' button, but her browser warns her that
	# there are mandatory fields that she needs to fill out.
    # TODO: write tests for mandatory fields.

	# Sue fills out the last mandatory field

	# Sue clicks the 'Create Issue' button.

	# The page updates, and now Sue's issue appears in the list.

	# Sue realises that she made a mistake with her submission. She changes
	# one of the fields

	# Sue clicks the 'Update' button.

	# The page refreshes and Sue can see that the change has persisted.

	# Satisfied that her work for the day is done, Sue closes her browser.

	# Five minutes later, Sue realises that she forgot to click the Log Off
	# button. She becomes anxious that the system might still be logged on.

	# She opens up the URL again, and notices that the system seems to have
	# logged her off, because the "Log In to Add/Modify Issues" form is
	# displayed.

	# Being a cautious person though, Sue decides that she had better log on
	# again and click the Log Off button to be 100% sure. She enters her
	# username and presses tab to get to the next field.

	# She enters the password and presses the 'Log In' button.

	# As before, the page refreshes. The 'Log Out' button is visible. Sue
	# clicks the button.

	# The page refreshes and the "Log In to Add/Modify Issues" form is again
	# visible. Sue is satisfied that she has logged off properly, so she
	# closes her web browser.

if __name__ == "__main__":
    unittest.main()
