from datetime import timedelta

import flask
from flask import Flask, request
from flask_cors import CORS
from neo4j import GraphDatabase
from App import DatabaseComunication
from credentials import uri, user, password

neo_db = DatabaseComunication(uri, user, password)

def exit_application():
    neo_db.close()

app = Flask(__name__)
app.secret_key = "s3cr3t"
app.permanent_session_lifetime = timedelta(days=5)
CORS(app)

driver = GraphDatabase.driver(uri=uri, auth=(user, password))
driver_session = driver.session()

@app.get('/get-friends')
async def get_friends():
    person = request.args.get('person')
    result = neo_db.find_friend(person)
    return result

@app.get('/get-person')
async def get_person():
    person = request.args.get('person')
    result = neo_db.find_person(person)
    return result

@app.get('/get-all')
async def get_all():
    result = neo_db.find_all()
    return result

@app.get('/get-recommendations')
async def get_recommendations():
    person = request.args.get('person')
    result = neo_db.find_recommendations(person)
    return result

@app.get('/get-credentials')
async def get_credentials():
    login = request.args.get('login')
    result = neo_db.login(login)
    return result

@app.post('/get-films')
async def get_films():
    cuisine = request.json['cuisine']
    location = request.json['location']
    person = request.json['person']
    result = neo_db.find_films(cuisine, location, person)
    print(result)
    return result

@app.post('/like')
async def like_film():
    person = request.json['person']
    film = request.json['film']
    result = neo_db.like_film(person, film)
    return result

@app.post('/dislike')
async def dislike_film():
    person = request.json['person']
    film = request.json['film']
    result = neo_db.dislike_film(person, film)
    return result

@app.post('/create-user')
async def create_user():
    name = request.json["name"]
    login = request.json['login']
    password = request.json['password']
    print(name, login, password)
    result = neo_db.create_user(name, login, password)
    return result

@app.post('/make-friends')
async def make_friends():
    p1 = request.json['p1']
    p2 = request.json['p2']
    result = neo_db.make_friends(p1, p2)
    return result

@app.post('/delete-friends')
async def delete_friends():
    p1 = request.json['p1']
    p2 = request.json['p2']
    result = neo_db.delete_friends(p1, p2)
    return result


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)


