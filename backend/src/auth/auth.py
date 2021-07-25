import json
from flask import request, _request_ctx_stack
from functools import wraps
from jose import jwt
from urllib.request import urlopen


AUTH0_DOMAIN = 'python-js-golang-dev.us.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'http://127.0.0.1:5000/'



## AuthError Exception
class AuthError(Exception):
    '''
        AuthError Exception
        A standardized way to communicate auth failure modes
    '''

    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


## Auth Header

#TODO

def get_token_auth_header():
    '''
    the function attempt to get the header from the request, if no header
    is present it raise an AuthError
    it attempt to split bearer and the token if the header is malformed,
    it raise an AuthError
    return the token part of the header
    '''

    auth = request.headers.get('Authorization', None)

    if not auth:
        raise AuthError(
            {
                'code': 'authorization_header_missing',
                'description': 'Authorization header is expected.'
            }, 401)

    parts = auth.split()
    if parts[0].lower() != 'bearer':
        raise AuthError(
            {
                'code': 'invalid_header',
                'description': 'Authorization header must start with "Bearer".'
            }, 401)

    elif len(parts) == 1:
        raise AuthError(
            {
                'code': 'invalid_header',
                'description': 'Token not found.'
            }, 401)

    elif len(parts) > 2:
        raise AuthError(
            {
                'code': 'invalid_header',
                'description': 'Authorization header must be bearer token.'
            }, 401)

    token = parts[1]
    return token

'''
#TODO implement check_permissions(permission, payload) method
    @INPUTS
        permission: string permission (i.e. 'post:drink')
        payload: decoded jwt payload

    it should raise an AuthError if permissions are not included in the payload
        #NOTE check your RBAC settings in Auth0
    it should raise an AuthError if the requested permission string is not in the payload permissions array
    return true otherwise
'''
def check_permissions(permission, payload):
    """

    Keyword arguments:
    permission   --      string permission (i.e. 'post:drink')
    payload      --      decoded jwt payload
    Return: return_description
    """

    if 'permissions' not in payload:
        raise AuthError(
            {
                'code': 'invalid_claims',
                'description': 'Permissions not included in JWT.'
            }, 400)

    if permission not in payload['permissions']:
        raise AuthError(
            {
                'code': 'unauthorized',
                'description': 'Permission not found.'
            }, 401)
    return True


'''
#TODO implement verify_decode_jwt(token) method
    it should be an Auth0 token with key id (kid)
    it should verify the token using Auth0 /.well-known/jwks.json
    it should decode the payload from the token
    it should validate the claims
    return the decoded payload

    !!NOTE urlopen has a common certificate error described here: https://stackoverflow.com/questions/50236117/scraping-ssl-certificate-verify-failed-error-for-http-en-wikipedia-org
'''
def verify_decode_jwt(token):
    """
    it should be an Auth0 token with key id (kid)
    it verify the token using Auth0 /.well-known/jwks.json
    it decode the payload from the token
    it validate the claims

    Keyword arguments:
    token   --      a json web token (string)
    Return: the decoded payload
    """

    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())
    unverified_header = jwt.get_unverified_header(token)
    rsa_key = {}
    if 'kid' not in unverified_header:
        raise AuthError(
            {
                'code': 'invalid_header',
                'description': 'Authorization malformed.'
            }, 401)

    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }
    if rsa_key:
        try:
            payload = jwt.decode(token,
                                 rsa_key,
                                 algorithms=ALGORITHMS,
                                 audience=API_AUDIENCE,
                                 issuer='https://' + AUTH0_DOMAIN + '/')

            return payload

        except jwt.ExpiredSignatureError:
            raise AuthError(
                {
                    'code': 'token_expired',
                    'description': 'Token expired.'
                }, 401)

        except jwt.JWTClaimsError:
            raise AuthError(
                {
                    'code':
                    'invalid_claims',
                    'description':
                    'Incorrect claims. Please, check the audience and issuer.'
                }, 401)
        except Exception:
            raise AuthError(
                {
                    'code': 'invalid_header',
                    'description': 'Unable to parse authentication token.'
                }, 400)
    raise AuthError(
        {
            'code': 'invalid_header',
            'description': 'Unable to find the appropriate key.'
        }, 400)


def requires_auth(permission=''):
    """
    use the get_token_auth_header method to get the token then use the verify_decode_jwt
    method to decode the jwt then use the check_permissions method validate claims and
    check the requested permission

    Keyword arguments:
        permission -- string permission (i.e. 'post:drink')
    Return: the decorator which passes the decoded payload to the decorated method
    """

    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            payload = verify_decode_jwt(token)
            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)

        return wrapper
    return requires_auth_decorator
