import pytest
from sqlalchemy.exc import IntegrityError

from app import app
from models import db, Recipe, User

class TestRecipe:
    def test_has_attributes(self):
        '''has attributes title, instructions, and minutes_to_complete.'''
        with app.app_context():
            Recipe.query.delete()
            User.query.delete()
            db.session.commit()

            user = User(username="chef123")
            user.password_hash = "strongpass"
            db.session.add(user)
            db.session.commit()

            recipe = Recipe(
                title="Delicious Shed Ham",
                instructions=("Or kind rest bred with am shed then. In raptures building an bringing be. "
                              "Elderly is detract tedious assured private so to visited. Do travelling companions "
                              "contrasted it. Mistress strongly remember up to. Ham him compass you proceed calling detract."),
                minutes_to_complete=60,
                user_id=user.id
            )
            db.session.add(recipe)
            db.session.commit()

            new_recipe = Recipe.query.filter_by(title="Delicious Shed Ham").first()
            assert new_recipe.title == "Delicious Shed Ham"
            assert new_recipe.minutes_to_complete == 60
            assert new_recipe.user_id == user.id

    def test_requires_title(self):
        '''requires each record to have a title.'''
        with app.app_context():
            Recipe.query.delete()
            User.query.delete()
            db.session.commit()

            user = User(username="tempuser")
            user.password_hash = "temppass"
            db.session.add(user)
            db.session.commit()

            valid_instructions = (
                "These instructions are definitely long enough to pass the 50 character requirement."
            )

            # Expect IntegrityError due to title=None
            with pytest.raises(IntegrityError):
                recipe = Recipe(
                    title=None,
                    instructions=valid_instructions,
                    minutes_to_complete=45,
                    user_id=user.id
                )
                db.session.add(recipe)
                db.session.commit()

    def test_requires_50_plus_char_instructions(self):
        '''instructions must be 50+ characters or raise error.'''
        with app.app_context():
            Recipe.query.delete()
            User.query.delete()
            db.session.commit()

            user = User(username="shortinstr")
            user.password_hash = "abc123"
            db.session.add(user)
            db.session.commit()

            # Expect ValueError from validation
            with pytest.raises(ValueError):
                recipe = Recipe(
                    title="Quick Ham",
                    instructions="Too short.",
                    minutes_to_complete=25,
                    user_id=user.id
                )
                db.session.add(recipe)
                db.session.flush()  # Use flush() to trigger validation before full commit
