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
    </body>
</html>
"""

html = html.format(
        repo=GITHUB_REPO
        )

print(html)
