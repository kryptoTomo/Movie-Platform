from neo4j import GraphDatabase

# Replace with the actual URI, username, and password
AURA_CONNECTION_URI = "neo4j+s://81d45eb9.databases.neo4j.io"
AURA_USERNAME = "neo4j"
AURA_PASSWORD = "t5rOk8KFSXlh-HZh2I1FYCzs1rViNIT3uL7IduqEMAQ"

# Instantiate the driver
driver = GraphDatabase.driver(
    AURA_CONNECTION_URI,
    auth=(AURA_USERNAME, AURA_PASSWORD)
)


# Import to prettify results
import json

# Import for the JSON helper function
from neo4j.time import DateTime

# Helper function for serializing Neo4j DateTime in JSON dumps
def default(o):
    if isinstance(o, (DateTime)):
        return o.isoformat()

movie_title_constraint = """
    CREATE CONSTRAINT FOR (movie:Movie) REQUIRE movie.title IS UNIQUE
"""


# Create the driver session
with driver.session() as session:
    # Make movie titles unique
    session.run(movie_title_constraint).data()
load_movies_csv = """
    LOAD CSV
      WITH HEADERS
      FROM 'https://raw.githubusercontent.com/kryptoTomo/Movie-Platform/main/dataset/movies.csv' AS row
    MERGE (m:Movie {title: row.Film, genre: row.Genre, studio: row.Studio})

"""

with driver.session() as session:
    # Load the CSV file
    session.run(load_movies_csv).data()





