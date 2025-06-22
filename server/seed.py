#!/usr/bin/env python3

from random import randint, choice as rc
from faker import Faker

from app import app
from models import db, Recipe, User

fake = Faker()

with app.app_context():

    print("Deleting all records...")
    Recipe.query.delete()
    User.query.delete()

    print("Creating users...")
    users = []
    usernames = set()

    for _ in range(20):
        username = fake.first_name()
        while username in usernames:
            username = fake.first_name()
        usernames.add(username)

        user = User(
            username=username,
            image_url=fake.image_url(),
            bio=fake.paragraph(nb_sentences=3)
        )

        # ✅ Use setter so password is hashed properly
        user.password_hash = "password123"

        users.append(user)

    db.session.add_all(users)
    db.session.commit()

    print("Creating recipes...")
    recipes = []
    for _ in range(100):
        recipe = Recipe(
            title=fake.sentence(),
            instructions=fake.paragraph(nb_sentences=6),
            minutes_to_complete=randint(15, 90),
            user=rc(users)  # ✅ Assign user directly
        )
        recipes.append(recipe)

    db.session.add_all(recipes)
    db.session.commit()
    print("Complete.")
