# Graphing Tumblr with Neo4j

This is a simple script, using py2neo, that gets all reblog data on a specific Tumblr post and adds it to a Neo4j database.

## Usage

1. Download Neo4j from [http://www.neo4j.org/](http://www.neo4j.org/) if you don't already have it, start the server and open [http://localhost:7474](http://localhost:7474).
2. Run the script from the terminal with `python tumblr-graphing.py [URL of post]`.

The nodes in the graph represent Tumblr users and are labelled "poster", "reblogger" and "source" (someone from whom the post was reblogged). Currently the only relationship in the graph is "reblogged from", with any text added by the reblogger included in the relationship as "comment".
