#!/usr/local/bin/python

print 'Content-Type:text/html' #HTML is following
print                          #Leave a blank line


######################## IMPORTS #########################
import cgi
import cgitb
cgitb.enable()

# much easier html requests
import requests

import json

# Used to remove any dangerous HTML (<script> tags etc)
from lxml.html.clean import clean_html


######################## SETTINGS #########################
GITHUB_USERNAME = 'WorkAtSwordfish'
GITHUB_REPO = 'GitIntegration'
LOCAL_URL_PATH = '/cgi-bin/github_issues_summary.py'



########################## FUNCTIONS ############################

def valid_token(token):
    '''
    Checks a provided OAuth token with GitHub and returns True if valid or
    False otherwise.
    '''
    token_string = "token {}".format(token)
    tmp_headers = {'Authorization': token_string }

    response = requests.get(issues_url, headers=tmp_headers)

    if response.headers['Status'] == '200 OK':
        return True

    else:
        return False


def filter_labels(labels_list, prefix):
    '''
    Given a list of labels and a prefix, this function returns a sub list of
    labels that match the prefix
    '''
    filtered_labels = []
    for label in labels_list:
        label_name = label['name'].encode()
        if prefix in label_name:
            no_prefix_label = label_name[len(prefix):]
            clean_label = no_prefix_label.strip()
            filtered_labels.append(clean_label)
    return filtered_labels

def get_page_links(root_issues_url):
    '''
    Github limits each request to 30 issues. This function returns a list of
    links for all subsequent pages of results"
    '''
    page_links_list = []
    if len(request_headers) > 0:
        response = requests.get(issues_url, headers = request_headers)
    else:
        response = requests.get(issues_url)

    if response.headers['Status'] == '200 OK':
        # First, we need to find the link with associated 'rel="last"' This will
        # give us the last page number
        last_page = 0
        links_list =response.headers['link'].split(',')
        for link in links_list:
            link_parts = link.split(';')
            rel_label = link_parts[1].strip(" rel=").strip('"')
            if rel_label == "last":
                # We found the right link item. Now let's get the number
                url_parts = link_parts[0].split("=")
                last_page = int(url_parts[1].strip(">"))
                # Finally, remember the new base url for constructing page links
                new_base_url = url_parts[0].strip(" <?page")
        # Now construct the page list

        if last_page == 0:
            # We only have 1 page of issues
            page_links_list.append(root_issues_url)
        elif last_page >0:
            for page in range(1, last_page+1):
                url = new_base_url + "?page=" + str(page)
                page_links_list.append(url)
        else:
            # Something has gone wrong.
            raise Exception("""we couldn't construct a page list. 'last page'
                    should be 0 or > 0, but it is {},
                    and its type is {}""".format(last_page, type(last_page)))

    return(page_links_list)

def get_nav_items(url):
    """
    This function will return a dictionary of navigation items based on the
    'first', 'pref', 'next' and 'last' page links optionally provided in
    the header of each response
    """
    response = requests.get(url)
    nav_items_dict = {}


    if response.headers['Status'] == '200 OK':
        if (response.headers.get('link') is not None):
            links_list = response.headers['link'].split(',')
            for link in links_list:
                link_parts = link.split(';')
                rel_label = link_parts[1].strip(" rel=").strip('"')
                if rel_label == "first":
                    first_url = link_parts[0].strip(" <>")
                    nav_items_dict["first"] = first_url

                if rel_label == "prev":
                    prev_url = link_parts[0].strip(" <>")
                    nav_items_dict["prev"] = prev_url

                if rel_label == "next":
                    next_url = link_parts[0].strip(" <>")
                    nav_items_dict["next"] = next_url

                if rel_label == "last":
                    last_url = link_parts[0].strip(" <>")
                    nav_items_dict["last"] = last_url
    return nav_items_dict


######################## INITIALISE VARIABLES #########################

logged_in = False

# Set template 'tags' to empty string. This ensures the final string format function
# doesn't fail if one is left out.
nav_string = ""
tbody_string = ""
authenticate_form_string = ""
new_issue_form_string = ""
request_headers = {}
token = ""
token_error_string = ""
created_success_string = ""
created_error_string = ""

# Allows access to any submitted data (whether GET url suffixes or POST data
form = cgi.FieldStorage()


####################### PROCESS SUBMITTED DATA ######################

# Use a specific page of issues data if specified, otherwise just use the root
# issues URL
if 'github_data' in form:
    issues_url = form['github_data'].value.strip('"')
else:
    issues_url = "https://api.github.com/repos/{}/{}/issues".format(
            GITHUB_USERNAME,
            GITHUB_REPO
            )

# Logging on
if form.getfirst('token',"") != "":
    token = form['token'].value
    if valid_token(token):
        logged_in = True
        token_string = "token {}".format(token)

        # We will use this following variable when we make our call to GitHub
        # for the table data
        request_headers = {'Authorization': token_string }

        # Reset the base URL to ensure that we will have a 'rel = last' value
        # in the response headers in order to construct our page list from.
        # This fixes a bug that occurs when the user is on the last page and
        # logs in.
        issues_url = "https://api.github.com/repos/{}/{}/issues".format(
                GITHUB_USERNAME,
                GITHUB_REPO
                )

    else:
        token_error_string = """
            <section class="error panel panel-danger">
                <div class="panel-heading">
                    <h3 class="panel-title">
                        Error
                    </h3>
                </div>
                <p class="error_message panel-body">
                    The supplied token does not appear to be valid. Please try
                    again
                </p>
            </section>
        """


# Process submitted new issue data

if form.getfirst('action_input',"") != "":

    # Construct the request dictionary
    new_issue_data = {"title": form['action_input'].value}

    # We will use this for priority, category and status fields if present
    submitted_labels_list = []

    if form.getfirst('client_input',"") != "":
        submitted_labels_list.append("C: " + form.getfirst('client_input'))

    if form.getfirst('description_input',"") != "":
        new_issue_data["body"] = form.getfirst('description_input')

    if form.getfirst('priority_input',"") != "":
        submitted_labels_list.append("P: " + form.getfirst('priority_input'))

    if form.getfirst('category_input',"") != "":
        submitted_labels_list.append("Cat: " + form.getfirst('category_input'))

    if form.getfirst('assigned_input',"") != "":
        new_issue_data["assignees"] = [form.getfirst('assigned_input')]

    if form.getfirst('status_input',"") != "":
        tmp_status = form.getfirst('status_input',"")
        if tmp_status == "Backlog":
            submitted_labels_list.append("1: " + tmp_status)
        elif tmp_status == "In Development":
            submitted_labels_list.append("2: " + tmp_status)
        elif tmp_status == "In Testing":
            submitted_labels_list.append("3: " + tmp_status)
        elif tmp_status == "Deployed":
            submitted_labels_list.append("4: " + tmp_status)

    if len(submitted_labels_list) > 0:
        new_issue_data["labels"] = submitted_labels_list

    # Now, construct and make the request
    payload = {'Authorization': token_string}
    response = requests.post(
            issues_url, headers=payload, data=json.dumps(new_issue_data)
            )
    if response.headers['status'] == '201 Created':
        # Success - new issue was added to Github
        created_success_string = """
        <div class="panel panel-success">
            <section class="panel-heading">
                <h3 class="panel-title">
                    Success!
                </h3>
                <p id="new_issue_success_message" class="panel-body">
                    Your issue has been successfully added.
                </p>
            </section>
        </div>

        """

    else:
        # Something went wrong - new issue wasn't created.
        created_error_string = """
        <div class="panel panel-warning">
        <section class="panel-heading">
            <h3 class="panel-title">
                Error
            </h3>
            <p id="new_issue_error_message" class="panel-body">
                Something went wrong. We cannot create your new issue - sorry.
            </p>
        </section>
        """


###################### HTML TEMPLATE DEFINITION #####################

html = """
<!DOCTYPE html>
<html lang="en_gb">
    <head>
        <meta charset="utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1">

        <link rel="stylesheet"
        href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css"
        integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u"
        crossorigin="anonymous">
        <link rel="stylesheet"
        href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap-theme.min.css"
        crossorigin="anonymous">

        <title>
           Github Issues Summary for {repo_string}
        </title>
    </head>
    <body>
        <div class="container theme-showcase">
            <section id='main_content'>
                <div class="jumbotron">
                    <h1>
                        {repo_string} Github Issues
                    </h1>
                </div>
                {token_error_string}
                {authenticate_form_string}
                {created_success_string}
                {created_error_string}
                {new_issue_form_string}
                <table border='1' id='issues_table' class="table table-striped">
                    {nav_string}
                    <caption>
                        List of issues in Github Repo '{repo_string}'.
                    </caption
                    <thead>
                        <tr>
                            <th id='client_column'>
                               Client Name
                            </th>
                            <th id='action_column'>
                               Action item/Request
                            </th>
                            <th id='description_column'>
                               Description
                            </th>
                            <th id='gh_column'>
                               GH number
                            </th>
                            <th id='priority_column'>
                               Priority
                            </th>
                            <th id='category_column'>
                               Category
                            </th>
                            <th id='assigned_column'>
                               Assigned To
                            </th>
                            <th id='comments_column'>
                               Comments
                            </th>
                            <th id='status_column'>
                               Status
                            </th>
                        </tr>
                    </thead>
                    <tbody>
                        {tbody_string}
                    </tbody>
                </table>
            </section>
        </div> <!-- container -->
    </body>
</html>
"""


############# TABLE NAV SECTION CREATION ################ 
if not logged_in:
    nav_items_dict = get_nav_items(issues_url)
    if len(nav_items_dict) > 0:
        first_link = ""
        prev_link = ""
        next_link = ""
        last_link = ""

        if nav_items_dict.get("first") is not None:
            first_href = '{local_url_path}?github_data="{first_url}"'
            first_href = first_href.format(
                    local_url_path = LOCAL_URL_PATH,
                    first_url = nav_items_dict["first"]
                    )
            if logged_in:
                first_href += "&token={}".format(token)
            first_link = """
            <li>
                <a href='{first_href}'>First Page</a>
            </li>
            """
            first_link = first_link.format(first_href = first_href)

        if nav_items_dict.get("prev") is not None:
            prev_href = '{local_url_path}?github_data="{prev_url}"'
            prev_href = prev_href.format(
                    local_url_path = LOCAL_URL_PATH,
                    prev_url = nav_items_dict["prev"]
                    )
            if logged_in:
                prev_href += "&token={}".format(token)
            prev_link = """
            <li>
                <a href='{prev_href}'>Previous Page</a>
            </li>
            """
            prev_link = prev_link.format(prev_href = prev_href)

        if nav_items_dict.get("next") is not None:
            next_href = '{local_url_path}?github_data="{next_url}"'
            next_href = next_href.format(
                    local_url_path = LOCAL_URL_PATH,
                    next_url = nav_items_dict["next"]
                    )
            if logged_in:
                next_href += "&token={}".format(token)
            next_link = """
            <li>
                <a href='{next_href}'>Next Page</a>
            </li>
            """
            next_link = next_link.format(next_href = next_href)

        if nav_items_dict.get("last") is not None:
            last_href = '{local_url_path}?github_data="{last_url}"'
            last_href = last_href.format(
                    local_url_path = LOCAL_URL_PATH,
                    last_url = nav_items_dict["last"]
                    )
            if logged_in:
                last_href += "&token={}".format(token)
            last_link = """
            <li>
                <a href='{last_href}'>Last Page</a>
            </li>
            """
            last_link = last_link.format(last_href = last_href)

        nav_string = """
        <nav>
            <ul class="nav nav-pills">
                {first_link}
                {prev_link}
                {next_link}
                {last_link}
            </ul>
        </nav>
        """
        nav_string = nav_string.format(
                first_link = first_link,
                prev_link = prev_link,
                next_link = next_link,
                last_link = last_link
                )

############### TABLE BODY CREATION ############### 

# Github only allows a few requests per hour if not logged in. Iterating
# through all the pages at once will quickly exhaust this limit. So, if we
# aren't logged in, we should just show one page at a time and allow the user
# to page through the results.

if logged_in:
    # Get a list of pages to iterate through to display all issues on one page
    pages = get_page_links(issues_url)
    # Initialise 3 empty sets to keep track of clients, priorities and
    # categories
    clients_set = set()
    priorities_set = set()
    categories_set = set()
    status_set = set()
else:
    # We only have one page to display
    pages = []
    pages.append(issues_url)

for page_link in pages:
    if len(request_headers) > 0:
        r = requests.get(page_link, headers = request_headers)
    else:
        r = requests.get(page_link)

    if r.headers['Status'] == '200 OK':
        issues = r.json()
        for issue in issues:
            row_html = """
            <tr>
                <td class='client'>
                    {clients_string}
                </td>
                <td class='action'>
                    {action_string}
                </td>
                <td class='description'>
                    {description_string}
                </td>
                <td class='gh_number'>
                    {gh_number_string}
                </td>
                <td class='priority'>
                    {priorities_string}
                </td>
                <td class='category'>
                    {categories_string}
                </td>
                <td class='assigned'>
                    {assigned_string}
                </td>
                <td class='comments'>
                    {comments_string}
                </td>
                <td class='status'>
                    {status_string}
                </td>
            </tr>
            """

            ## Client Data ##
            # Get labels starting with 'C:' - these signify clients
            clients_list = filter_labels(issue['labels'],'C:')
            clients_string = ""
            for client_name in clients_list:
                clients_string += (str(client_name) + ", ")
                if logged_in:
                    clients_set.add(client_name)
            clients_string = clients_string.strip(', ')

            ## Action Data ##
            # Get 'title' field 
            action_string = issue['title']

            ## Description Data ##
            # Get 'body' field 
            description_string = issue['body']

            ## GH Number Data ##
            # Get 'number' field 
            gh_number_string = issue['number']

            ## Priority Data ##
            # Get labels starting with 'P:' - these signify priorities
            priorities_list = filter_labels(issue['labels'],'P:')
            priorities_string = ""
            for priorities_name in priorities_list:
                priorities_string += (str(priorities_name) + ", ")
                if logged_in:
                    priorities_set.add(priorities_name)
            priorities_string = priorities_string.strip(', ')

            ## Category Data ##
            # Get labels starting with 'Cat:' - these signify categories
            categories_list = filter_labels(issue['labels'],'Cat:')
            categories_string = ""
            for categories_name in categories_list:
                categories_string += (str(categories_name) + ", ")
                if logged_in:
                    categories_set.add(categories_name)
            categories_string = categories_string.strip(', ')

            ## Assigned To Data ##
            # Get 'assignees[login']' fields
            assigned_string = ""
            if isinstance(issue['assignees'],list):
                for assigned in issue['assignees']:
                    assigned_string += (str(assigned['login']) + ", ")
                assigned_string = assigned_string.strip(', ')
            else:
                assigned_string += issue['assignees']

            ## Comments Data ##
            comments_string = ""
            if issue['comments'] > 0:
                # We have comments. Retrieve them.
                comments_url = issue['comments_url']
                if len(request_headers) > 0:
                    r = requests.get(comments_url, headers = request_headers)
                else:
                    r = requests.get(comments_url)

                if r.headers['Status'] == '200 OK':
                    comments = r.json()
                    for comment in comments:
                        # e.g. Johnny12 @ 2015-11-03T09:32:12 : "Comment"
                        tmp_string = '''
                        <p>
                            {user} @ {timestamp} : "{comment}"
                        </p>
                        '''
                        tmp_string = tmp_string.format(
                                user = comment['user']['login'],
                                timestamp = comment['updated_at'],
                                comment = comment['body']
                                )
                        comments_string += tmp_string

            ## Status Data ##
            # Get labels starting with '1:', '2:', '3:' or '4:'- these signify
            # status
            status_list = []
            status_list += filter_labels(issue['labels'],'1:')
            status_list += filter_labels(issue['labels'],'2:')
            status_list += filter_labels(issue['labels'],'3:')
            status_list += filter_labels(issue['labels'],'4:')
            status_string = ""
            for status_item in status_list:
                status_string += (str(status_item) + ", ")
                if logged_in:
                    status_set.add(status_item)
            status_string = status_string.strip(', ')

            # Add the row to the table data string
            tbody_string += (row_html.format(
                clients_string = clients_string,
                action_string = action_string.encode(),
                description_string = description_string,
                gh_number_string = gh_number_string,
                priorities_string = priorities_string,
                categories_string = categories_string,
                assigned_string = assigned_string,
                comments_string = comments_string,
                status_string = status_string
                ))


    else:
        tbody_string = """
        <tr>
            <td colspan='9' class="alert alert-warning" role="alert">
                <strong>Error:</strong> Not able to retrieve issues data from Github. This
                may be because you have exceeded the maximum request limit
                of 60 requests per hour for an anonymous user. Log in to
                increase your limit to 5000 requests per hour.
            </td>
        </tr>
        """


################## AUTHENTICATION FORM CREATION #################### 
if logged_in:
    authenticate_form_string = """
    <form id='authenticate_form' method="POST">
        <fieldset class="form-group">
            <legend>
                You are logged in.
            </legend>
            <input type="hidden" name="token" value="">
            </input>
            <input type="submit" id="logout_button" value="Log Out"
            class="btn">
        </fieldset>
    </form>
    """

else:
    authenticate_form_string = """
    <form id='authenticate_form' method="POST">
        <fieldset class="form-group">
            <legend>
                Log in to add a new issue or view all issues on a single page.
            </legend>
            <table class="table table-condensed">
                <tr>
                    <th>
                        <label for="token">
                            40 Character OAuth Token:
                        </label>
                    </th>
                </tr>
                <tr>
                    <td>
                        <input type="text" name="token" required id="token"
                        placeholder=
                        "eg: e529880b2b81d98cc28a802a3bdbf32ce98a0d47">
                        </input>
                    </td>
                </tr>
                <tr>
                    <td>
                        <input type="submit" value="Log In" id="log_in_button"
                        class="btn">
                    </td>
                </tr>

            </table>
            <p class="alert alert-info" role="alert">
                <strong>Please be patient after logging in.</strong> Displaying all issues on a
                single page can take up to a full minute or longer.
            </p>
        </fieldset>
    </form>
    """

###################### NEW ISSUE FORM CREATION #########################
if logged_in:
    new_issue_form_string = """
    <form id="new_issue_form" method="POST">
        <fieldset class="form-group">

            <legend>
               Create a New Issue
            </legend>

            <table class="table table-condensed">
                <tr>
                    <th>
                        <label for="client_input"> Client: </label>
                    </th>
                    <th>
                        <label for="action_input">Action:</label>
                    </th>
                    <th>
                        <label for="description_input">Description:</label>
                    </th>
                    <th>
                        <label for="priority_input">Priority:</label>
                    </th>
                    <th>
                        <label for="category_input">Category:</label>
                    </th>
                    <th>
                        <label for="assigned_input">Assigned To:</label>
                    </th>
                    <th>
                        <label for="status_input">Status:</label>
                    </th>
                    <th>
                    </th>
                </tr>
                <tr>
                    <td>
                        <select id="client_input" name="client_input">
                            {client_options}
                        </select>
                    </td>
                    <td>
                        <input name="action_input" id ="action_input" required>
                        </input>
                    </td>
                    <td>
                        <textarea id="description_input"
                        name="description_input" ></textarea>
                    </td>
                    <td>
                        <select id="priority_input" name="priority_input">
                            {priority_options}
                        </select>
                    </td>
                    <td>
                        <select id="category_input" name="category_input">
                            {category_options}
                        </select>
                    </td>
                    <td>
                        <input name="assigned_input" id ="assigned_input">
                        </input>
                    </td>
                    <td>
                        <select id="status_input" name="status_input">
                            {status_options}
                        </select>
                    </td>
                </tr>
                <tr colspan="7">
                    <td>
                        <input type='hidden' name='token' value='{token}'>
                        </input>

                        <input type='submit' id="new_issue_submit_button"
                        value='Create New Issue' class="btn">
                        </input>
                    </td>
                </tr>
        </fieldset>
    </form>
    """

    # Construct list of client options
    client_options = """
    <option value=''>Select a Client</option>
    """
    for client in clients_set:
        tmp_string = """
        <option value='{client}'>{client}</option>
        """
        tmp_string = tmp_string.format(client=client)
        client_options += tmp_string

    # Construct list of priority options
    priority_options = """
    <option value=''>Select a Priority</option>
    """
    for priority in priorities_set:
        tmp_string = """
        <option value='{priority}'>{priority}</option>
        """
        tmp_string = tmp_string.format(priority=priority)
        priority_options += tmp_string


    # Construct list of category options
    category_options = """
    <option value=''>Select a Category</option>
    """
    for category in categories_set:
        tmp_string = """
        <option value='{category}'>{category}</option>
        """
        tmp_string = tmp_string.format(category=category)
        category_options += tmp_string

    # Construct list of status options
    status_options = """
    <option value=''>Select a Status</option>
    """
    for status in status_set:
        tmp_string = """
        <option value='{status}'>{status}</option>
        """
        tmp_string = tmp_string.format(status=status)
        status_options += tmp_string

    new_issue_form_string = new_issue_form_string.format(
            client_options = client_options,
            priority_options = priority_options,
            category_options = category_options,
            status_options = status_options,
            token = token
            )

###################### SANITISE AND RENDER THE HTML #########################

# Remove any dangerous tags etc
if len(tbody_string) > 0:
    tbody_string = clean_html(tbody_string)

# Complete the HTML
html = html.format(
        token_error_string = token_error_string,
        authenticate_form_string = authenticate_form_string,
        created_success_string = created_success_string,
        created_error_string = created_error_string,
        new_issue_form_string = new_issue_form_string,
        repo_string=GITHUB_REPO,
        nav_string = nav_string,
        tbody_string=tbody_string
        )

print(html)


