import requests
import csv
from flask import session
from threading import Thread

COLUMNS = [
    "Title",
    "Description",
    "Priority",
    "Severity",
    "Component",
    "Assign To",
    "Milestone",
]

XMLTAGS = [
    "summary",
    "description",
    "priority",
    "severity-id",
    "component-id",
    "assignee-id",
    "milestone-id",
]

last_error = None

def get_generic(path):
    global last_error
    last_error = None

    url = "https://%s/%s" % (session.get('domain'), path)
    headers = {'Accept': 'application/json'}
    auth = requests.auth.HTTPBasicAuth(session.get('user'), session.get('pw'))

    try:
        r = requests.get(url, headers=headers, auth=auth, timeout=15.0)
    except requests.exceptions.Timeout:
        last_error = (408, "Connection timeout.")
        return False
    except requests.exceptions.RequestException as e:
        last_error = (111, "Connection error.")
        return False

    if r.status_code == 200 or r.status_code == 304:
        return r.json()

    if r.status_code == 401:
        last_error = (401, "Authorization failure.")
        return False

    app.logger.debug("Unexpected status code %d for %s" % (r.status_code, url))
    last_error = (r.status_code, "Connection error.")
    return False

def get_last_error():
    return last_error

def get_projects():
    projects = get_generic('projects')
    if projects == False:
        return False
    return [(p['id'],p['title']) for p in projects]

def get_severities(projectid):
    severities = get_generic("projects/%d/severities" % (projectid,))
    if severities == False:
        return False
    return {s['id']: s['name'] for s in severities} or {}

def get_components(projectid):
    components = get_generic("projects/%d/components" % (projectid,))
    if components == False:
        return False
    return {c['id']: c['name'] for c in components}

def get_milestones(projectid):
    milestones = get_generic("projects/%d/milestones" % (projectid,))
    if milestones == False:
        return False
    return {m['id']: m['title'] for m in milestones}

def get_people(projectid):
    people = get_generic("projects/%d/people" % (projectid,))
    if people == False:
        return False
    return {p['id']: (p['first_name'] + ' ' + p['last_name']).strip() for p in people}

def parse_tickets(csvfile, projectid):
    columnchoices = [
        None,
        None,
        {1: "Lowest", 2: "Low", 3: "Normal", 4: "High", 5: "Highest"},
        session['severities'],
        session['components'],
        session['people'],
        session['milestones'],
    ]
    reader = csv.reader(csvfile)
    columns = [c.casefold() for c in COLUMNS]
    columnmap = {} # index the recognized columns
    othermap = []  # index the unrecognized columns
    tickets = []
    rownum = 0
    for row in reader:
        if rownum == 0:
            colnum = 0
            for col in row:
                cc = col.strip().rstrip(':')
                cf = cc.casefold()
                if cf in columns:
                    columnmap[columns.index(cf)] = colnum
                else:
                    othermap.append((cc, colnum))
                colnum += 1
        else:
            ticket = [(None,'')] * len(COLUMNS)
            extras = []
            for i in columnmap:
                ticket[i] = fuzzyfind(row[columnmap[i]], columnchoices[i])

            # add all the unknown fields to the description
            for cc, colnum in othermap:
                if row[colnum]:
                    extras.append("**%s**\n\n%s\n" % (cc, row[colnum]))
            if extras:
                desc = ticket[1][1] + "\n\n" + "\n".join(extras)
                ticket[1] = (desc, desc)

            # require a priority
            if ticket[2][0] is None:
                ticket[2] = (3, "Normal")
            tickets.append(ticket)

            # limit 500 tickets
            if len(tickets) >= 500:
                return tickets

        rownum += 1
    return tickets

def fuzzyfind(target, choices):
    if choices is None:
        return (target, target)
    if not choices:
        return (None, '')
    t = target.casefold()
    for choice in choices:
        val = choices[choice]
        if val.casefold() == t:
            return (choice, val)
    return (None, '')

def ticket2xml(ticket):
    lines = ['<ticket>']
    for i in range(0,len(ticket)):
        val = ticket[i][0]
        if val is not None:
            tag = XMLTAGS[i]
            if tag[-3:] == "-id":
                lines.append('<%s type="integer">' % (tag,))
            else:
                lines.append('<%s>' % (tag,))
            lines.append(str(val))
            lines.append('</%s>' % (tag,))
    lines.append('</ticket>')
    return ''.join(lines)

def tickets2xml(tickets):
    lines = []
    for ticket in tickets:
        lines.append(ticket2xml(ticket))
    return '\n'.join(lines)

def post_tickets_worker(url, auth, tickets):
    headers = {'Accept': 'application/json', 'Content-Type': 'application/xml'}
    for ticket in tickets:
        data = ticket2xml(ticket)
        r = requests.post(url, headers=headers, auth=auth, data=data)
        if r.status_code != 201:
            app.logger.debug("Unexpected status code %d for %s" % (r.status_code,url))
            app.logger.debug(r.text)

def post_tickets(projectid, tickets):
    url = "https://%s/projects/%d/tickets" % (session.get('domain'), projectid)
    auth = requests.auth.HTTPBasicAuth(session.get('user'), session.get('pw'))
    t = Thread(target=post_tickets_worker, args=(url, auth, tickets), daemon=True)
    t.start()
