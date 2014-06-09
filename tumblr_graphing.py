# -*- coding: utf-8 -*-

import requests, sys, re
from bs4 import BeautifulSoup
from py2neo import neo4j, node, rel


def get_all_notes(posturl):
    r = requests.get(posturl)
    soup = BeautifulSoup(r.text)
    morenotes = soup.find_all("a", "more_notes_link")
    reblogs = []
    if not morenotes:
        for reblog in soup.find_all("li", "reblog"):
            reblogs.append(reblog.get_text())
    else:
        while morenotes:
            # get notes from front page
            for reblog in soup.find_all("li", "reblog"):
                reblogs.append(reblog.get_text())

            # get notes page url
            regex = u"'(/notes/[\w=?/]*)'"
            blogurl = "/".join(posturl.split("/")[0:3])
            notes_url = blogurl + re.search(regex, str(morenotes[0])).group(1)
            
            # request and soupify the next page of notes
            r = requests.get(notes_url)
            soup = BeautifulSoup(r.text)
            morenotes = soup.find_all("a", "more_notes_link")
            
    print len(reblogs)
    return reblogs
    
def reblogs_into_db(reblogs):
    graph_db = neo4j.GraphDatabaseService("http://localhost:7474/db/data/")
    people = graph_db.get_or_create_index(neo4j.Node, "People")
    p_regex = u"([a-z0-9-]*) posted this"
    rb_regex = u"([a-z0-9-]*) reblogged this from ([a-z0-9-]*)( and added:(.*)$)?"
    for reblog in reblogs:
        p_match = re.search(p_regex, reblog)
        rb_match = re.search(rb_regex, reblog)
        if p_match:
            poster = graph_db.create({"name": p_match.group(1)})[0]
            poster.add_labels("poster")
        elif rb_match:
            reblogger = graph_db.get_or_create_indexed_node("People", "name", rb_match.group(1), properties={"name": rb_match.group(1)})
            print reblogger
            reblogger.add_labels("reblogger")
            source = graph_db.get_or_create_indexed_node("People", "name", rb_match.group(2), properties={"name": rb_match.group(2)})
            source.add_labels("source")
            if rb_match.group(3):
                properties = {"comment": rb_match.group(3)}
            else:
                properties = {}
            graph_db.create(rel(reblogger, ("Reblogged_from", properties), source))

# TODO
# look at tags? recommendations?
# is there something fun i can do with comments?
# add likers as and commenters as separate labels


if __name__ == "__main__":
    posturl = sys.argv[1]
    reblogs = get_all_notes(posturl)
    reblogs_into_db(reblogs)
