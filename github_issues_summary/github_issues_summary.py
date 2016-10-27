#!/usr/local/bin/python

print 'Content-Type:text/html' #HTML is following
print                          #Leave a blank line

import cgitb
cgitb.enable()

GITHUB_USERNAME = "WorkAtSwordfish"
GITHUB_REPO = "GitIntegration"

html = """
<html>
    <head>
        <title>
           Github Issues Summary for {repo} 
        </title>
    </head>
    <body>
        <section id="main_content">
            <h1>
                Github Issues
            </h1>
            <table border='1' id='issues_table'>
                <caption>
                    List of issues in Github Repo '{repo}'. If you log in,
                    you'll be able to add a new issue or edit existing issues.
                </caption
                <thead>
                    <tr>
                        <th id="client_column">
                           Client Name
                        </th>
                        <th id="action_column">
                           Action item/Request
                        </th>
                        <th id="description_column">
                           Description
                        </th>
                        <th id="gh_column">
                           GH number
                        </th>
                        <th id="priority_column">
                           Priority
                        </th>
                        <th id="category_column">
                           Category
                        </th>
                        <th id="assigned_column">
                           Assigned To
                        </th>
                        <th id="comments_column">
                           Comments
                        </th>
                        <th id="status_column">
                           Status
                        </th>
                    </tr>
                </thead>
                <tbody>
                </tbody>
            </table>
        </section>
    </body>
</html>
"""

html = html.format(
        repo=GITHUB_REPO
        )

print(html)
