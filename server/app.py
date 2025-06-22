#!/usr/bin/env python3

from flask import request, session, jsonify
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from config import app, db, api
from models import User, Recipe

class Signup(Resource):
    def post(self):
        data = request.get_json()
        try:
            user = User(
                username=data['username'],
                image_url=data.get('image_url'),
                bio=data.get('bio')
            )
            user.password_hash = data['password']
            db.session.add(user)
            db.session.commit()

            session['user_id'] = user.id
            return user.to_dict(), 201
        except IntegrityError:
            db.session.rollback()
            return {"errors": ["Username must be unique."]}, 422
        except Exception as e:
            db.session.rollback()
            return {"errors": [str(e)]}, 422

class CheckSession(Resource):
    def get(self):
        user_id = session.get('user_id')
        if user_id:
            user = db.session.get(User, user_id)
            if user:
                return user.to_dict(), 200
        return {"error": "Unauthorized"}, 401

class Login(Resource):
    def post(self):
        data = request.get_json()
        user = User.query.filter_by(username=data.get('username')).first()
        if user and user.authenticate(data.get('password')):
            session['user_id'] = user.id
            return user.to_dict(), 200
        return {"error": "Invalid username or password"}, 401

class Logout(Resource):
    def delete(self):
        if session.get('user_id'):
            session.pop('user_id')
            return '', 204
        return {"error": "Not authorized"}, 401

class RecipeIndex(Resource):
    def get(self):
        try:
            user_id = session.get('user_id')
            if not user_id:
                return {"error": "Unauthorized"}, 401

            user = db.session.get(User, user_id)
            if not user:
                return {"error": "User not found"}, 404

            recipes = Recipe.query.filter_by(user_id=user_id).all()
            return [r.to_dict() for r in recipes], 200

        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}, 500

    def post(self):
        try:
            user_id = session.get('user_id')
            if not user_id:
                return {"error": "Unauthorized"}, 401

            data = request.get_json()
            title = data.get('title')
            instructions = data.get('instructions')
            minutes = data.get('minutes_to_complete')

            errors = []
            if not title or title.strip() == "":
                errors.append("Title is required.")
            if not instructions or len(instructions.strip()) < 50:
                errors.append("Instructions must be at least 50 characters long.")
            if minutes is None:
                errors.append("Minutes to complete is required.")

            if errors:
                return {"errors": errors}, 422

            recipe = Recipe(
                title=title.strip(),
                instructions=instructions.strip(),
                minutes_to_complete=minutes,
                user_id=user_id
            )
            db.session.add(recipe)
            db.session.commit()
            return recipe.to_dict(), 201

        except Exception as e:
            db.session.rollback()
            return {"errors": [f"An unexpected error occurred: {str(e)}"]}, 422


# Register resources
api.add_resource(Signup, '/signup')
api.add_resource(CheckSession, '/check_session')
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(RecipeIndex, '/recipes')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
