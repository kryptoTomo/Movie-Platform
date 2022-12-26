from flask import logging, jsonify
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable
from credentials import uri, user, password

class DatabaseComunication:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def find_friend(self, person_name):
        with self.driver.session() as session:
            result = session.read_transaction(self._find_and_return_friend, person_name)
            return {"friends": result}

    @staticmethod
    def _find_and_return_friend(tx, person_name):
        query = (
            "MATCH (p:Person {name: $person_name})-[:IS_FRIEND_OF]-(friend) "
            "RETURN friend.name AS name"
        )
        result = tx.run(query, person_name=person_name)
        return [record["name"] for record in result]

    def find_person(self, person_name):
        with self.driver.session() as session:
            result = session.read_transaction(self._find_and_return_person, person_name)
            return {"person": result}

    @staticmethod
    def _find_and_return_person(tx, person_name):
        query = (
            """MATCH (p:Person), (per:Person {name: $person_name}) 
            WHERE NOT (p)-[:IS_FRIEND_OF]->(per) 
            AND NOT (per)-[:IS_FRIEND_OF]->(p) 
            AND NOT p.name = $person_name RETURN p.name AS name"""
        )
        result = tx.run(query, person_name=person_name)
        return [record["name"] for record in result]

    def find_all(self):
        with self.driver.session() as session:
            result = session.read_transaction(self._find_and_return_all)
            return {"all": result}

    @staticmethod
    def _find_and_return_all(tx):
        query = (
            """MATCH (n:Person) RETURN n.name AS name, n.login AS login"""
        )
        result = tx.run(query)
        return [{"user": row["name"], "login": row["login"]} for row in result]

    def find_films(self, cuisine, location, person):
        print("start")
        with self.driver.session() as session:
            result = session.read_transaction(
                self._find_and_return_films,
                cuisine,
                location,
                person)
            print(result)
            return {"films": result}

    @staticmethod
    def _find_and_return_films(tx, cuisine, location, person):
        cuisine_string = "" if cuisine == '' else f""" WHERE m.genre = '{cuisine}' """
        location_string = "" if location == '' else f""" WHERE m.studio = '{location}' """
        person_string = "" if person == '' else ",(person:Person {name: $person})-[:LIKES]->(m)"
        print(location_string)
        print("person; ", person,person_string)
        print("koniec")
        query = '''MATCH (film:Film)-[:LOCATED_IN]->{location_string},
                    (film)-[:SERVES]->{cuisine_string}
                    {person_string}
                    WITH film.name AS name, cuisine.name AS cuisine, location.name AS location
                    RETURN name, cuisine, location'''.format(location_string=location_string, cuisine_string=cuisine_string, person_string=person_string)
        query1 = '''MATCH (m:Movie {location_string}{cuisine_string})
                    {person_string}
                    WITH m.title AS title, m.genre AS genre, m.studio AS studio
                    RETURN title, genre, studio'''.format(location_string=location_string,  cuisine_string=cuisine_string, person_string=person_string)
        result = tx.run(query1, person=person)
        # for row in result:
        #     print(row["title"]," ", row["genre"])
        print("test1: ",result)

        try:
            return_values = [{"film": row["title"], "cuisine": row["genre"], "location": row["studio"]} for row in result]
            print(return_values)
            return return_values
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(query=query, exception=exception))
            raise

    def find_recommendations(self, person):
        with self.driver.session() as session:
            result = session.read_transaction(
                self._find_recommendations,
                person
                )
            return {"recommendations": result}

    @staticmethod
    def _find_recommendations(tx, person):
        query = (
            """MATCH (p:Person {name:$person})-[:IS_FRIEND_OF]->(friend),
            (friend)-[:LIKES]->(m)
            WHERE NOT (p)-[:LIKES]->(m)
            RETURN m.title AS filmName, 
            collect(friend.name) AS reccomendedBy, 
            count(*) AS numberOfRecommendations 
            ORDER BY numberOfRecommendations DESC"""
        )
        result = tx.run(query, person=person)
        records = []
        for el in result:
            records.append({
                'name': el['filmName'],
                'recommenders': el['reccomendedBy'],
                'count': el['numberOfRecommendations']
            })

        return records


    def find_best(self, cuisine_name, location_name, person_list, max):
        with self.driver.session() as session:
            result = session.read_transaction(self._find_best, cuisine_name, location_name, person_list, max)
            return result

    @staticmethod
    def _find_best(tx, cuisine_name, location_name, person_list, max):
        # simple hack to generalized and parameterized functions into one
        cuisine_string = "(cuisine)" if cuisine_name == '' else "(cuisine:Cuisine {name: $cuisine_name})"
        location_string = "(location)" if location_name == '' else "(location:Location {name: $location_name})"
        person_string = "" if len(person_list) == 0 else "WHERE person.name IN %s" % (str(person_list))

        # if True, return only the films with the highest number of likes by friends
        if (max):
            query = (
                '''MATCH (film:Film)-[:LOCATED_IN]->{location},
                      (film)-[:SERVES]->{cuisine},
                      (person:Person)-[:LIKES]->(film)
                {person}
                WITH film.name AS name, collect(person.name) AS likers, COUNT(*) AS occurence
                WITH MAX(occurence) as max_count
                MATCH (film:Film)-[:LOCATED_IN]->{location},
                    (film)-[:SERVES]->{cuisine},
                    (person:Person)-[:LIKES]->(film)
                {person}
                    WITH film.name AS name, collect(person.name) AS likers, COUNT(*) AS occurence, max_count
                    WHERE occurence = max_count
                    RETURN name, likers, occurence'''.format(location=location_string, cuisine=cuisine_string,
                                                             person=person_string)
                )
        else:
            query = (
                    '''MATCH (film:Film)-[:LOCATED_IN]->%s,
                            (film)-[:SERVES]->%s,
                            (person:Person)-[:LIKES]->(film)
                    %s
                    RETURN film.name AS name, collect(person.name) AS likers, COUNT(*) AS occurence
                    ORDER BY occurence DESC''' % (location_string, cuisine_string, person_string)
            )

        result = tx.run(query, cuisine_name=cuisine_name, location_name=location_name, person_list=person_list)
        try:
            return jsonify([{"film": row["name"], "likers": row["likers"], "occurence": row["occurence"]} for row in result])
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(query=query, exception=exception))
            raise



    def like_film(self, person_name, film_name):
        with self.driver.session() as session:
            result = session.write_transaction(
                self._create_relation_person_film,
                person_name,
                film_name)
            return result

    def dislike_film(self, person_name, film_name):
        with self.driver.session() as session:
            result = session.write_transaction(
                self._delete_relation_person_film,
                person_name,
                film_name)
            return result

    @staticmethod
    def _create_relation_person_film(tx, person_name, film_name):
        print(film_name)
        query = (
            """MATCH (p:Person{name:$person_name}), (m:Movie{title:$film_name})
            CREATE (p)-[:LIKES]->(m) RETURN p.name"""
        )
        result = tx.run(query, person_name=person_name, film_name=film_name)
        return result.data()[0]

    @staticmethod
    def _delete_relation_person_film(tx, person_name, film_name):
        query = (
            """OPTIONAL MATCH (p:Person{name:$person_name})-[relation:LIKES]->(m:Movie{title:$film_name})
            DELETE relation RETURN p.name"""
        )
        result = tx.run(query, person_name=person_name, film_name=film_name)
        return result.data()[0]

    def create_user(self, name, login, passw):
        with self.driver.session() as session:
            result = session.write_transaction(
                self._create_node_person,
                name,
                login,
                passw)
            return result

    @staticmethod
    def _create_node_person(tx, name, login, passw):
        query = (
            """CREATE (p:Person {name:$name, login:$login, password:$password}) RETURN p.name"""
        )
        result = tx.run(query, name=name, login=login, password=passw)
        try:
            return result.data()[0]
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(query=query, exception=exception))
            raise

    def make_friends(self, name1, name2):
        with self.driver.session() as session:
            result = session.write_transaction(
                self._create_or_delete_relation_person_person,
                True,
                name1,
                name2)
            return result

    def delete_friends(self, name1, name2):
        with self.driver.session() as session:
            result = session.write_transaction(
                self._create_or_delete_relation_person_person,
                False,
                name1,
                name2)
            return result

    @staticmethod
    def _create_or_delete_relation_person_person(tx, create, name1, name2):
        if create:
            query = (
                """MATCH (p:Person{name:$name1}), (r:Person{name:$name2})
                CREATE (p)-[:IS_FRIEND_OF]->(r) RETURN p.name"""
            )
        else:
            query = (
                """MATCH (p:Person {name:$name1})-[relation:IS_FRIEND_OF]->(r:Person{name:$name2})
                    DELETE relation return p.name"""
            )
        result = tx.run(query, name1=name1, name2=name2)
        try:
            return result.data()[0]
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(query=query, exception=exception))
            raise

    def login(self, login):
        with self.driver.session() as session:
            result = session.read_transaction(
                self._check_password,
                login)
        return result

    @staticmethod
    def _check_password(tx, login):
        query = (
            """OPTIONAL MATCH (p:Person{login:$login}) RETURN p.password AS password, p.name as name"""
        )
        result = tx.run(query, login=login)
        return result.data()[0]

# for testing purpose, can be commented out
# if __name__ == "__main__":

#     app = Recommender(uri, user, password)
#     app.close()