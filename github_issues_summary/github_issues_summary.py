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
            <table border='1'>
                <caption>
                    List of issues in Github Repo '{repo}'. If you log in,
                    you'll be able to add a new issue or edit existing issues.
                </caption
                <thead>
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
