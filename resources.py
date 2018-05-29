from flask_restful import Resource, reqparse
import werkzeug
from models import UserModel, RevokedTokenModel


from flask_jwt_extended import (create_access_token, 
                                create_refresh_token, 
                                jwt_required, 
                                jwt_refresh_token_required, 
                                get_jwt_identity, 
                                get_raw_jwt)

parser = reqparse.RequestParser()
parser.add_argument('username', required=True)
parser.add_argument('password', required=True)
parser.add_argument('imagefile',  # 이미지를 받을땐 요렇게..
                    type=werkzeug.datastructures.FileStorage,
                    location='files')


'''
curl --header "Content-Type: application/json" \
     -d "{\"username\": \"hulk\", \"password\": \"GG\"}" \
    localhost:5000/registration
'''
class UserRegistration(Resource):
    def post(self):
        data = parser.parse_args()
        print(data)
        if data['imagefile']:  #바로 보낼 수 없으니까..
            data['imagefile'] = 'well received'
        
        if UserModel.find_by_username(data['username']):
            return {'message': 'User {} already exists'.format(data['username'])}

        new_user = UserModel(
            username=data['username'],
            password=UserModel.generate_hash(data['password'])
        )
        try:
            new_user.save_to_db()
            ## 여기서 만들자
            access_token = create_access_token(identity=data['username'])
            refresh_token = create_refresh_token(identity=data['username'])
            return {'message': 'User {} was created'.format(data['username']),
                    'access_token': access_token,
                    'refresh_token': refresh_token}
        except:
            return {'message': 'something went wrong'}, 500



class UserLogin(Resource):
    def post(self):
        data = parser.parse_args()
        current_user = UserModel.find_by_username(data['username'])

        if not current_user:
            return {'message': 'User {} does not exists'.format(data['username'])}
        if not UserModel.verify_hash(data['password'], current_user.password):
            return {'message': 'wrong credentials'}
        
        ## 여기서 만들자
        access_token = create_access_token(identity=data['username'])
        refresh_token = create_refresh_token(identity=data['username'])
        
        return {'message': 'Loged in as {}'.format(data['username']),
                'access_token': access_token,
                'refresh_token': refresh_token}
      
class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity() # refresh token에서 id를 만들어냄
        access_token = create_access_token(identity = current_user)
        return {'access_token': access_token}

class AllUsers(Resource):
    def get(self):
        return UserModel.return_all()

    def delete(self):
        return UserModel.delete_all()
      
      
class SecretResource(Resource):
    @jwt_required
    def get(self):
        return {
            'answer': 42
        }


## logout용!!

class UserLogoutAccess(Resource):
    @jwt_required
    def post(self):
        jti = get_raw_jwt()['jti']
        try:
            revoked_token = RevokedTokenModel(jti = jti)
            revoked_token.add()
            return {'message': 'Access token has been revoked'}
        except:
            return {'message': 'Something went wrong'}, 500


class UserLogoutRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        jti = get_raw_jwt()['jti']
        try:
            revoked_token = RevokedTokenModel(jti = jti)
            revoked_token.add()
            return {'message': 'Refresh token has been revoked'}
        except:
            return {'message': 'Something went wrong'}, 500