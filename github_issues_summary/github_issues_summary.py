#!/usr/local/bin/python

print 'Content-Type:text/html' #HTML is following
print                          #Leave a blank line


######################## IMPORTS #########################
import cgi
import cgitb
cgitb.enable()

# much easier html requests
import requests

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
    print("The request headers were {}".format(tmp_headers))
    print("we're checking the token. The response is {}".format(response))

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

    print("I'm in get_page_links. response headers are {}".format(response.headers))
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
        if last_page >0:
            for page in range(1, last_page+1):
                url = new_base_url + "?page=" + str(page)
                page_links_list.append(url)
        else:
            # Something has gone wrong.
            raise Exception("we couldn't construct a page list")
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

if 'token' in form and form['token'].value not in [None, ""]:
    token = form['token'].value
    if valid_token(token):
        logged_in = True
        token_string = "token {}".format(token)
        # We will use this following variable when we make our call to GitHub
        # for the table data
        request_headers = {'Authorization': token_string }

###################### HTML TEMPLATE DEFINITION #####################

html = """
<html>
    <head>
        <title>
           Github Issues Summary for {repo_string}
        </title>
    </head>
    <body>
        <section id='main_content'>
            <h1>
                {repo_string} Github Issues
            </h1>
            {authenticate_form_string}
            {new_issue_form_string}
            <table border='1' id='issues_table'>
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
            <ul>
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
            <td colspan='9'>
                Error: Not able to retrieve issues data from Github. This
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
        <fieldset>
            <legend>
                You are currently logged in.
            </legend>
                <input type="hidden" name="token" value="">
                </input>
                <input type="submit" value="Log Out">
        </fieldset>
    </form>
    """

else:
    authenticate_form_string = """
    <form id='authenticate_form' method="POST">
        <fieldset>
            <legend>
                Log in to add a new issue or view all issues on a single page.
            </legend>
            <label>40 Character OAuth Token:
                <input type="text" name="token" required
                placeholder="eg: e529880b2b81d98cc28a802a3bdbf32ce98a0d47">
                </input>
            </label>
            <input type="submit" value="Log In">
            <p>
                <em>Please be patient after logging in.</em> Displaying all issues on a
                single page can take up to a full minute or longer.
            </p>
        </fieldset>
    </form>
    """

###################### NEW ISSUE FORM CREATION #########################
if logged_in:
    new_issue_form_string = """
    <form id="new_issue_form" method="POST">
        <label for="client_input">
            Client:
        </label>
        <select id="client_input" name="client">
            {client_options}
        </select>

        <label for="action_input">
            Action:
        </label>
        <input name="action" id ="action_input">
        </input>

        <label for="description_input">
            Description:
        </label>
        <textarea id="description_input" name="description">
        </textarea>

        <label for="priority_input">
            Priority:
        </label>
        <select id="priority_input" name="priority">
            {priority_options}
        </select>

        <label for="category_input">
            Category:
        </label>
        <select id="category_input" name="category">
            {category_options}
        </select>

        <label for="client_input">
            Client:
        </label>
        <select id="client_input" name="client">
            {client_options}
        </select>

        <label for="client_input">
            Client:
        </label>
        <select id="client_input" name="client">
            {client_options}
        </select>

        <label for="client_input">
            Client:
        </label>
        <select id="client_input" name="client">
            {client_options}
        </select>

    </form>
    """

###################### SANITISE AND RENDER THE HTML #########################

# Remove any dangerous tags etc
if len(tbody_string) > 0:
    tbody_string = clean_html(tbody_string)

# Complete the HTML
html = html.format(
        authenticate_form_string = authenticate_form_string,
        new_issue_form_string = new_issue_form_string,
        repo_string=GITHUB_REPO,
        nav_string = nav_string,
        tbody_string=tbody_string
        )

print(html)


