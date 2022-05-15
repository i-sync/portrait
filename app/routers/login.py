
from datetime import timedelta
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_login import LoginManager
from fastapi_login.exceptions import InvalidCredentialsException
from starlette.responses import Response, RedirectResponse
from fastapi import APIRouter

router = APIRouter()

SECRET = 'a31bf483b1e56eb34635a541ae45097a81b31b826c991280'
COOKIE_NAME = 'access-token'

manager = LoginManager(SECRET, token_url='/auth/token', use_cookie=True, use_header=False, cookie_name=COOKIE_NAME)

fake_db = {'admin@admin.com': {'password': 'xMWVuKAKVWTZ3nA'}}

@manager.user_loader()
def load_user(email: str):  # could also be an asynchronous function
    user = fake_db.get(email)
    return user


# the python-multipart package is required to use the OAuth2PasswordRequestForm
@router.post('/auth/token')
async def login(response: Response, data: OAuth2PasswordRequestForm = Depends()):
    email = data.username
    password = data.password

    user = load_user(email)  # we are using the same function to retrieve the user
    if not user:
        raise InvalidCredentialsException  # you can also use your own HTTPException
    elif password != user['password']:
        raise InvalidCredentialsException
    
    access_token = manager.create_access_token(
        data=dict(sub=email),
        expires=timedelta(days=7)
    )
    #return {'access_token': access_token, 'token_type': 'bearer'}
    manager.set_cookie(response, access_token if isinstance(access_token, str) else access_token.decode('utf-8'))
    response.status_code=200
    return response

@router.get('/logout')
async def logout(response: Response):
    response = RedirectResponse(url='/')
    response.set_cookie(COOKIE_NAME, '-deleted-', max_age=0, httponly=True)
    return response