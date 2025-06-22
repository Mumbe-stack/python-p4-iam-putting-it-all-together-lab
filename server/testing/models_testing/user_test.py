import pytest
from sqlalchemy.exc import IntegrityError

from app import app
from models import db, User, Recipe

class TestUser:
    '''User in models.py'''

    def test_has_attributes(self):
        '''has attributes username, _password_hash, image_url, and bio.'''

        with app.app_context():
            Recipe.query.delete()
            User.query.delete()
            db.session.commit()

            user = User(
                username="Liz",
                image_url="https://example.com/liz.jpg",
                bio="Famous actress and public figure."
            )
            user.password_hash = "securepassword123"

            db.session.add(user)
            db.session.commit()

            created_user = User.query.filter_by(username="Liz").first()

            assert created_user.username == "Liz"
            assert created_user.image_url == "https://example.com/liz.jpg"
            assert created_user.bio == "Famous actress and public figure."

            # Ensure password hash is write-only
            with pytest.raises(AttributeError):
                _ = created_user.password_hash

    def test_requires_username(self):
        '''requires each record to have a username.'''

        with app.app_context():
            Recipe.query.delete()
            User.query.delete()
            db.session.commit()

            user = User()
            user.password_hash = "somepassword"

            with pytest.raises((IntegrityError, ValueError)):
                db.session.add(user)
                db.session.commit()

    def test_requires_unique_username(self):
        '''requires each record to have a unique username.'''

        with app.app_context():
            Recipe.query.delete()
            User.query.delete()
            db.session.commit()

            user_1 = User(username="Ben")
            user_1.password_hash = "password1"

            user_2 = User(username="Ben")
            user_2.password_hash = "password2"

            db.session.add(user_1)
            db.session.commit()

            with pytest.raises(IntegrityError):
                db.session.add(user_2)
                db.session.commit()

    def test_has_list_of_recipes(self):
        '''has records with lists of recipe records attached.'''

        with app.app_context():
            Recipe.query.delete()
            User.query.delete()
            db.session.commit()

            user = User(username="Prabhdip")
            user.password_hash = "secret789"

            recipe_1 = Recipe(
                title="Delicious Shed Ham",
                instructions="""Or kind rest bred with am shed then. In raptures building an bringing be. Elderly is detract tedious assured private so to visited. Do travelling companions contrasted it. Mistress strongly remember up to. Ham him compass you proceed calling detract. Better of always missed we person mr. September smallness northward situation few her certainty something.""",
                minutes_to_complete=60,
                user=user
            )

            recipe_2 = Recipe(
                title="Hasty Party Ham",
                instructions="""As am hastily invited settled at limited civilly fortune me. Really spring in extent an by. Judge but built gay party world. Of so am he remember although required. Bachelor unpacked be advanced at. Confined in declared marianne is vicinity.""",
                minutes_to_complete=30,
                user=user
            )

            db.session.add_all([user, recipe_1, recipe_2])
            db.session.commit()

            assert user.id is not None
            assert recipe_1.id is not None
            assert recipe_2.id is not None
            assert recipe_1 in user.recipes
            assert recipe_2 in user.recipes
