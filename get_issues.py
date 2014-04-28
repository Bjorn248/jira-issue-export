#!/usr/bin/env python
import urllib, urllib2, cookielib, os, csv, re, getpass, gc
from bs4 import BeautifulSoup
from urllib2 import urlopen

# Get username and password from prompt
username = raw_input("Enter JIRA Username: ")
password = getpass.getpass()
start = 0

cj = cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
login_data = urllib.urlencode({'username' : username, 'password' : password})
# Log in to your JIRA instance
# Be sure to set the jira_url variable!
jira_url = "https://mobiquity.jira.com"
opener.open(jira_url + '/login', login_data)
# Clean up the working directory
os.system('rm *.csv')
os.system('rm *.xls')
header_indices = {}
# Dictionary that contains the columns we want to have in our final csv file
columns_we_want = {"Project":1,"Key":1,"Issue Type":1,"Status":1,"Priority":1,"Resolution":1,"Assignee":1,"Reporter":1,"Creator":1,"Created":1,"Updated":1,"Due Date":1,"Votes":1,"Watchers":1,"Original Estimate":1,"Remaining Estimate":1,"Time Spent":1,"Bug Status":1,"Closed by":1,"Closed on":1,"Severity":1,"Story Points":1,"Submitted by":1}
while 1 == 1:
    gc.collect()
# This line contains the query url from which an xls (that is really just html tables) is downloaded
# This particular query returns only bugs and user stories, but this should be extensible to any jql passed to the url
# After downloading each xls, it is converted to a csv, then afterwards, all the csvs are concatenated to form one master.csv file
    resp = opener.open(jira_url + '/sr/jira.issueviews:searchrequest-excel-all-fields/temp/SearchRequest.xls?jqlQuery=issuetype%20in%20(Bug%2C%20"User%20Story")&tempMax=1000&pager/start=' + `start`)
    print "downloading xls..." + `start`
    with open('JIRA_EXPORT_' + `start` + '.xls', "wb") as local_file:
        local_file.write(resp.read())
    statinfo = os.stat('JIRA_EXPORT_' + `start` + '.xls')
# if the size of the new file is less than 3000 bytes, break the loop, because this likely means that it is an empty table
    if statinfo.st_size < 3000:
        break
    soup = BeautifulSoup(open('JIRA_EXPORT_' + `start` + '.xls'))
    table = soup.find('table', attrs={ "id" : "issuetable"})
    headers = [re.sub(' +', ' ', header.text).strip() for header in table.find_all('th')]
    for index, header in enumerate(headers):
        if header in columns_we_want:
            header_indices[index] = 1
    headers_we_want = []
    for i in header_indices.keys():
        headers_we_want.append(headers[i])
    rows = []
    for row in table.find_all('tr'):
        vals = ([re.sub(' +', ' ', val.text).strip() for val in row.find_all('td')])
        vals_we_want = []
        if len(vals) != 0:
            for i in header_indices.keys():
                vals_we_want.append(vals[i])
        rows.append(vals_we_want)
    with open('JIRA_EXPORT_' + `start` + '.csv', 'wb') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        if start == 0:
            writer.writerow(headers_we_want)
        writer.writerows(row for row in rows if row)
    os.system('cat ' + 'JIRA_EXPORT_' + `start` + '.csv' + ' >> master.csv')
    start += 1000
os.system('rm JIRA_EXPORT_*.csv')
os.system('rm JIRA_EXPORT_*.xls')
