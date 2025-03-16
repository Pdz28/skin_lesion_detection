from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api, reqparse, fields, marshal_with, abort
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_cors import CORS
from flask_session import Session
import os
from utils.model import *
from utils.image_processing import preprocess_image
from PIL import Image
import io
from waitress import serve
import json

#phong

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.urandom(24)  # Set the secret key
app.config['SESSION_TYPE'] = 'filesystem'

app.config['RESULT_FOLDER'] = os.path.join('static', 'results')
if not os.path.exists(app.config['RESULT_FOLDER']):
    os.makedirs(app.config['RESULT_FOLDER'])
    
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

Session(app)
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

# Set permanent user for testing purposes
def create_permanent_user():
    username = "admin"
    email = "a@b.c"
    password = "123"
    
    if not UserModel.query.filter_by(username=username).first():
        hashed_password = generate_password_hash(password)
        new_user = UserModel(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        print("Permanent user created.")
    else:
        print("This user already exists.")
        
@app.route('/')
def home():
    if 'username' in session:
        return render_template('index.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        user = UserModel.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['username'] = user.username
            return jsonify({"message": "Login successful"}), 200
        return jsonify({"message": "Invalid credentials"}), 401
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if UserModel.query.filter_by(username=username).first():
            return jsonify({"message": "Username already exists"}), 409
        if UserModel.query.filter_by(email=email).first():
            return jsonify({"message": "Email already exists"}), 409
        
        hashed_password = generate_password_hash(password)
        new_user = UserModel(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({"message": "Registration successful"}), 201
    return render_template('register.html')

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/process-image', methods=['POST'])
def process_image():
    if 'username' not in session:
        return redirect(url_for('login'))

    if 'image' not in request.files:
        return jsonify({"message": "No image file provided"}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({"message": "No selected file"}), 400

    if file and allowed_file(file.filename):
        # Save the original image
        original_image_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
        file.save(original_image_path)
        
        image = Image.open(original_image_path)
        processed_image = preprocess_image(image)
        model = load_model()

        # Get both result image and predictions
        result_image, predictions, status = detect_skin_disease(model, processed_image)

        # Save the result image
        result_image_path = os.path.join(app.config['RESULT_FOLDER'],
                                          'result_' + secure_filename(file.filename))
        result_image.save(result_image_path)

        return jsonify({"original_image": secure_filename(file.filename), 
                        "result_image": 'result_' + secure_filename(file.filename),
                        "predictions": predictions,
                        "status": status
                        }), 200

    return jsonify({"message": "Invalid file type"}), 400

@app.route('/results')
def results():
    if 'username' not in session:
        return redirect(url_for('login'))

    original_image = request.args.get('original_image')
    result_image = request.args.get('result_image')
    
    # Parse status từ URL parameters
    status_json = request.args.get('status')
    
    try:
        if status_json:
            status = json.loads(status_json)
            print("Status from URL:", status)
        else:
            print("Status is None, re-processing image...")
            # Nếu không có status, xử lý lại ảnh để lấy status
            if original_image and result_image:
                # Tải ảnh gốc
                original_image_path = os.path.join(app.config['UPLOAD_FOLDER'], original_image)
                if os.path.exists(original_image_path):
                    image = Image.open(original_image_path)
                    processed_image = preprocess_image(image)
                    model = load_model()
                    
                    # Chỉ lấy status từ model mà không lưu ảnh mới
                    _, _, status = detect_skin_disease(model, processed_image)
                    print("Status re-generated:", status)
                else:
                    status = {"has_detection": False, "message": "Không tìm thấy ảnh gốc"}
            else:
                status = {"has_detection": False, "message": "Không có dữ liệu phát hiện"}
    except Exception as e:
        print(f"Error processing status: {e}")
        status = {"has_detection": False, "message": "Lỗi xử lý dữ liệu phát hiện"}

    if not original_image or not result_image:
        return redirect(url_for('home'))

    return render_template(
        'results.html',
        username=session['username'],
        original_image=original_image,
        result_image=result_image,
        status=status
    )

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

if __name__ == '__main__':
    with app.app_context():
        db.drop_all()
        db.create_all()  # Tạo bảng nếu chưa có
        create_permanent_user() # Tạo người dùng
    serve(app, host='0.0.0.0', port=5000)
