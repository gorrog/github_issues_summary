#!/usr/local/bin/python

print 'Content-Type:text/html' #HTML is following
print                          #Leave a blank line

import cgi
import cgitb
cgitb.enable()

# much easier html requests
import requests

from lxml.html.clean import clean_html

# Settings
GITHUB_USERNAME = 'WorkAtSwordfish'
GITHUB_REPO = 'GitIntegration'
LOCAL_URL_PATH = '/cgi-bin/github_issues_summary.py'

# Initialise variables
logged_in = False
nav_string = ""
tbody_string = ""
form = cgi.FieldStorage()
if 'github_data' in form:
    issues_url = form['github_data'].value.strip('"')
    print("form['github_data'] is {}".format(issues_url))
else:
    issues_url = "https://api.github.com/repos/{}/{}/issues".format(
            GITHUB_USERNAME,
            GITHUB_REPO
            )

########################## FUNCTIONS ############################

def filter_labels(labels_list, prefix):
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
    response = requests.get(issues_url)
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
    page_links_list = []

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
    if response.headers.get('link') is not None:
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
                Github Issues
            </h1>
            <table border='1' id='issues_table'>
                {nav_string}
                <caption>
                    List of issues in Github Repo '{repo_string}'. Once you log
                    in, you'll be able to add a new issue or edit existing
                    issues.
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

############### TABLE CONTENTS CREATION ############### 

# Github only allows a few requests per hour if not logged in. Iterating
# through all the pages at once will quickly exhaust this limit. So, if we
# aren't logged in, we should just show one page at a time and allow the user
# to page through the results.

if logged_in:
    # Get a list of pages to iterate through to display all issues on one page
    page_links_list = get_page_links(issues_url)
else:
    # We only have one page to display
    page_links_list=[issues_url]

for page_link in page_links_list:
    r = requests.get(page_link)
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
        priorities_string = priorities_string.strip(', ')

        ## Category Data ##
        # Get labels starting with 'Cat:' - these signify categories
        categories_list = filter_labels(issue['labels'],'Cat:')
        categories_string = ""
        for categories_name in categories_list:
            categories_string += (str(categories_name) + ", ")
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
            comments = requests.get(comments_url).json()
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


###################### SANITISE AND RENDER THE HTML #########################

# Remove any dangerous tags etc
tbody_string = clean_html(tbody_string)

# Complete the HTML
html = html.format(
        repo_string=GITHUB_REPO,
        nav_string = nav_string,
        tbody_string=tbody_string
        )

print(html)


