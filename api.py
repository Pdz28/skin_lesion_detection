from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api, reqparse, fields, marshal_with, abort
from flask import Flask, render_template, request, jsonify



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)
api = Api(app)

class UserModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)

    def __repr__(self):
        return f"User(name={self.username}, email={self.email})"

user__args = reqparse.RequestParser()
user__args.add_argument('name', type=str, required=True, help='Name of the user')
user__args.add_argument('email', type=str, required=True, help='Email of the user')

userFileds = {
    'id': fields.Integer,
    'username': fields.String,
    'email': fields.String
}

class Users(Resource):
    @marshal_with(userFileds)
    def get(self):
        users = UserModel.query.all()
        return users
    
    @marshal_with(userFileds)
    def post(self):
        args = user__args.parse_args()
        user = UserModel(username=args['name'], email=args['email'])
        if UserModel.query.filter_by(username=args['name']).first():
            abort(409, message='User already exists')
        if UserModel.query.filter_by(email=args['email']).first():
            abort(409, message='Email already exists')
        db.session.add(user)
        db.session.commit()
        users = UserModel.query.all()
        return users, 201

class User(Resource):
    @marshal_with(userFileds)
    def get(self, user_id):
        user = UserModel.query.get(user_id)
        if not user:
            abort(404, message='User not found')
        return user
    
    @marshal_with(userFileds)
    def patch(self, user_id):
        args = user__args.parse_args()
        user = UserModel.query.get(user_id)
        if not user:
            abort(404, message='User not found')
        user.username = args['name']
        user.email = args['email']
        db.session.commit()
        return user

    @marshal_with(userFileds)
    def delete(self, user_id):
        user = UserModel.query.get(user_id)
        if not user:
            abort(404, message='User not found')
        db.session.delete(user)
        db.session.commit()
        users = UserModel.query.all()
        return users, 204



api.add_resource(Users, '/api/users/')
api.add_resource(User, '/api/users/<int:user_id>')

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True,debug=True)