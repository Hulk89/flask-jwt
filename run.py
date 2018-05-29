from flask import Flask
from flask_restful import Api


app = Flask(__name__)
api = Api(app)  # API 등록하기 위함

## db setting
from flask_sqlalchemy import SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '이거슨비밀이다.절때알려져서는안댄다.'
db = SQLAlchemy(app)

@app.before_first_request
def create_tables():
    db.create_all()

## JWT setting
from flask_jwt_extended import JWTManager
app.config['JWT_SECRET_KEY'] = '이거슨JWT비밀이다.'
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']
jwt = JWTManager(app)

import views, models, resources

api.add_resource(resources.UserRegistration, '/registration')
api.add_resource(resources.UserLogin, '/login')
api.add_resource(resources.UserLogoutAccess, '/logout/access')
api.add_resource(resources.UserLogoutRefresh, '/logout/refresh')
api.add_resource(resources.TokenRefresh, '/token/refresh')
api.add_resource(resources.AllUsers, '/users')
api.add_resource(resources.SecretResource, '/secret')



@jwt.token_in_blacklist_loader  # secure endpoint를 access할 때 모두 불림
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return models.RevokedTokenModel.is_jti_blacklisted(jti)