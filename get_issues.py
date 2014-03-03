import urllib, urllib2, cookielib, os, csv, re, getpass
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
while 1 == 1:
# This line contains the query url from which an xls (that is really just html tables) is downloaded
# This particular query returns only bugs and user stories, but this should be extensible to any jql passed to the url
# After downloading each xls, it is converted to a csv, then afterwards, all the csvs are concatenated to form one master.csv file
    resp = opener.open(jira_url + '/sr/jira.issueviews:searchrequest-excel-all-fields/temp/SearchRequest.xls?jqlQuery=issuetype%20in%20(Bug%2C%20"User%20Story")&tempMax=1000&pager/start=' + `start`)
    print "downloading xls..." + `start`
    with open('JIRA_EXPORT_' + `start` + '.xls', "wb") as local_file:
        local_file.write(resp.read())
    statinfo = os.stat('JIRA_EXPORT_' + `start` + '.xls')
    if statinfo.st_size < 3000:
        break
    soup = BeautifulSoup(open('JIRA_EXPORT_' + `start` + '.xls'))
    table = soup.find('table', attrs={ "id" : "issuetable"})
    headers = [re.sub(' +', ' ', header.text.encode('utf8')).strip() for header in table.find_all('th')]
    rows = []
    for row in table.find_all('tr'):
        rows.append([re.sub(' +', ' ', val.text.encode('utf8')).strip() for val in row.find_all('td')])
    with open('JIRA_EXPORT_' + `start` + '.csv', 'wb') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        if start == 0:
            writer.writerow(headers)
        writer.writerows(row for row in rows if row)
    os.system('cat ' + 'JIRA_EXPORT_' + `start` + '.csv' + ' >> master.csv')
    start += 1000
