#!/usr/local/bin/python

print 'Content-Type:text/html' #HTML is following
print                          #Leave a blank line

import cgitb
cgitb.enable()

# much easier html requests
import requests

from lxml.html.clean import clean_html

GITHUB_USERNAME = 'WorkAtSwordfish'
GITHUB_REPO = 'GitIntegration'

def filter_labels(labels_list, prefix):
    filtered_labels = []
    for label in labels_list:
        label_name = label['name'].encode()
        if prefix in label_name:
            no_prefix_label = label_name[len(prefix):]
            clean_label = no_prefix_label.strip()
            filtered_labels.append(clean_label)
    return filtered_labels

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

tbody_string = ""

# Get the issues data from Github
issues_url = "https://api.github.com/repos/{}/{}/issues".format(
        GITHUB_USERNAME,
        GITHUB_REPO
        )
r = requests.get(issues_url)
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

tbody_string = clean_html(tbody_string)

html = html.format(
        repo_string=GITHUB_REPO,
        tbody_string=tbody_string
        )

print(html)


