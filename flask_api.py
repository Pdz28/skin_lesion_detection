from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api, reqparse, fields, marshal_with, abort
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
api = Api(app)

class UserModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)  # Lưu mật khẩu đã mã hóa

    def __repr__(self):
        return f"User(name={self.username}, email={self.email})"

user__args = reqparse.RequestParser()
user__args.add_argument('name', type=str, required=True, help='Name of the user')
user__args.add_argument('email', type=str, required=True, help='Email of the user')
user__args.add_argument('password', type=str, required=True, help='Password of the user')

userFields = {
    'id': fields.Integer,
    'username': fields.String,
    'email': fields.String
}

class Users(Resource):
    @marshal_with(userFields)
    def get(self):
        users = UserModel.query.all()
        return users
    
    @marshal_with(userFields)
    def post(self):
        args = user__args.parse_args()
        
        # Kiểm tra user đã tồn tại chưa
        if UserModel.query.filter_by(username=args['name']).first():
            abort(409, message='User already exists')
        if UserModel.query.filter_by(email=args['email']).first():
            abort(409, message='Email already exists')

        # Mã hóa mật khẩu
        hashed_password = generate_password_hash(args['password'])

        user = UserModel(username=args['name'], email=args['email'], password=hashed_password)
        db.session.add(user)
        db.session.commit()
        
        return user, 201

class User(Resource):
    @marshal_with(userFields)
    def get(self, user_id):
        user = UserModel.query.get(user_id)
        if not user:
            abort(404, message='User not found')
        return user
    
    @marshal_with(userFields)
    def patch(self, user_id):
        args = user__args.parse_args()
        user = UserModel.query.get(user_id)
        if not user:
            abort(404, message='User not found')

        user.username = args['name']
        user.email = args['email']
        db.session.commit()
        return user

    @marshal_with(userFields)
    def delete(self, user_id):
        user = UserModel.query.get(user_id)
        if not user:
            abort(404, message='User not found')
        db.session.delete(user)
        db.session.commit()
        return {}, 204

api.add_resource(Users, '/api/users/')
api.add_resource(User, '/api/users/<int:user_id>')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = UserModel.query.filter_by(username=data['username']).first()
    
    # Kiểm tra mật khẩu đã mã hóa
    if user and check_password_hash(user.password, data['password']):
        return jsonify({"message": "Login successful"}), 200
    return jsonify({"message": "Invalid credentials"}), 401

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    if UserModel.query.filter_by(username=data['username']).first():
        return jsonify({"message": "Username already exists"}), 400
    
    # Mã hóa mật khẩu trước khi lưu
    hashed_password = generate_password_hash(data['password'])

    new_user = UserModel(
        username=data['username'],
        password=hashed_password,
        email=data['email']
    )
    
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User created successfully"}), 201

if __name__ == '__main__':
    with app.app_context():
        db.drop_all()
        db.create_all()  # Tạo bảng nếu chưa có
    app.run(host='0.0.0.0', port=5000, threaded=True, debug=True)
