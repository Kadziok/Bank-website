from app import app
import ssl
import OpenSSL
import werkzeug.serving
from app.models import User
from flask_jwt import JWT, jwt_required, current_identity

'''def verify_request(self, request, client_address):
    cert = request.getpeercert(True)
    #raw = decoder.decode(cert)[0]
    #print("Serial Number of your certificate is: ", str(raw[0][1]))
    # todo: do checks & if serial no is ok then return true
    return True'''

'''werkzeug.serving.BaseWSGIServer.verify_request = verify_request'''


def authenticate(username, password):
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        return user

def identity(payload):
    user_id = payload['identity']
    return User.query.filter_by(id=user_id).first()


jwt = JWT(app, authenticate, identity)



@app.route('/protected')
@jwt_required()
def protected():
    return "you're in"

app_key = 'certs/server.key'
app_key_password = None
app_cert = 'certs/server.cer'
ssl_context = ssl.create_default_context( purpose=ssl.Purpose.CLIENT_AUTH,
                                              cafile='certs/ca.cer' )

ssl_context.load_cert_chain( certfile=app_cert, keyfile=app_key, password=app_key_password )
ssl_context.verify_mode = ssl.CERT_REQUIRED




app.run(port=443, ssl_context=ssl_context)