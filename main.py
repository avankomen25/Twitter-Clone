'''
Starts a hello world webserver.
'''

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import uvicorn
import sqlite3

app = FastAPI()
templates = Jinja2Templates(directory='templates')

def check_credentials(request: Request):
    '''
    return username is user is logged in
    if not logged in, returns none
    '''

    query_username = request.query_params.get('username')
    query_password = request.query_params.get('password')
    print('query_username=', query_username)
    print('query_password=', query_password)

    cookie_username = request.cookies.get('username')
    cookie_password = request.cookies.get('password')
    print('cookie_username=', cookie_username)
    print('cookie_password=', cookie_password)

    username = cookie_username
    password = cookie_password

    if username == 'Trump' and password == '12345':
        print(f'Logged in as {username}')
        return 'Trump'
    else:
        print('not logged in')
        return None

    # FIXME: implement this

@app.get('/', response_class=HTMLResponse)
async def index(request: Request):
    is_logged_in = check_credentials(request)

    # extract username from database
    con = sqlite3.connect('twitter_clone.db')
    cur = con.cursor()
    sql = """
    SELECT username FROM users WHERE id=1;
    """
    # cur.execute(sql)
    # for row in cur.fetchall():
        # username = row[0]

    # create response
    return templates.TemplateResponse(
        request=request,
        name='index.html',
        context={
            'is_logged_in': check_credentials(request), 
            'username': check_credentials(request),
        }
    )

@app.get('/logout', response_class=HTMLResponse)
async def login(request: Request):
    response = templates.TemplateResponse(
        request=request,
        name='logout.html',
    )
    response.delete_cookie(key='username')
    response.delete_cookie(key='password')
    return response

@app.get('/login', response_class=HTMLResponse)
async def login(request: Request):
    is_logged_in = check_credentials(request)
    response = templates.TemplateResponse(
        request=request,
        name='login.html',
        context={
            'is_logged_in': check_credentials(request) 
        }
    )
    response.set_cookie(key='username', value=request.query_params.get('username'))
    response.set_cookie(key='password', value=request.query_params.get('password'))
    return response


if __name__ == '__main__':
    uvicorn.run("main:app", host='127.0.0.1', port=8080, reload=True)
