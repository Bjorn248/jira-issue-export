#!/usr/bin/env python
import urllib, urllib2, cookielib, os, csv, re, getpass, gc, sys, json, base64
from bs4 import BeautifulSoup
from multiprocessing import Pool
from urllib2 import urlopen
import pprint

# Get username and password from prompt
# username = raw_input("Enter JIRA Username: ")
# password = getpass.getpass()
# We are hardcoding for automation
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
columns_we_want = {"Project":1,"Key":1,"Issue Type":1,"Status":1,"Priority":1,"Resolution":1,"Assignee":1,"Reporter":1,"Creator":1,"Created":1,"Updated":1,"Due Date":1,"Votes":1,"Watchers":1,"Original Estimate":1,"Remaining Estimate":1,"Time Spent":1,"Bug Status":1,"Closed by":1,"Closed on":1,"Severity":1,"Story Points":1,"Submitted by":1}

request = urllib2.Request(jira_url + '/rest/api/2/search?jql=issuetype%20in%20("Bug"%2C%20"User%20Story")')
base64string = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
request.add_header("Authorization", "Basic %s" % base64string)
bugs_and_user_stories = urllib2.urlopen(request)
json_data = json.loads(bugs_and_user_stories.read())
number_of_issues = json_data['total']
number_of_threads = (number_of_issues / 1000) + 1
urls = []
for i in range(number_of_threads):
    urls.append(jira_url + '/sr/jira.issueviews:searchrequest-excel-all-fields/temp/SearchRequest.xls?jqlQuery=issuetype%20in%20(Bug%2C%20"User%20Story")&tempMax=1000&pager/start=' + str(i))
print urls

file_names = []
for i in range(number_of_threads):
    file_names.append('JIRA_EXPORT_' + str(i) + '.xls')
print file_names

def get_files(url):
    file_number = url.split("start=")[1]
    u = opener.open(url)
    print "Downloading file: " + file_number
    # for p,v in vars(u).iteritems():
    #     print p, ": ", v
    f = open('JIRA_EXPORT_' + file_number + '.xls', 'wb')
    f.write(u.read())
    f.close()

def gen_csv(path):
    file_name = path.split(".")[0]
    print path
    soup = BeautifulSoup(open(path))
    table = soup.find('table', attrs={ "id" : "issuetable"})
    headers = [re.sub(' +', ' ', header.text).strip() for header in table.find_all('th')]
    for index, header in enumerate(headers):
        if header in columns_we_want.keys():
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
    with open(file_name + '.csv', 'wb') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        if file_name.endswith('_0'):
            writer.writerow(headers_we_want)
        writer.writerows(row for row in rows if row)

# Below options are either spawn as many threads as there are files to download
# or spawn as many threads as there are cores...does not make a difference in performance
pool = Pool(number_of_threads)
# pool = Pool()
pool.map(get_files, urls)
pool.map(gen_csv, file_names)
# Concatenate all csv files into a single file
os.system('cat *.csv > master.csv')
