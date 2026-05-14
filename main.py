'''
Starts a hello world webserver.
'''

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn
import sqlite3

app = FastAPI()
app.mount('/static', StaticFiles(directory='static'), name='static')
templates = Jinja2Templates(directory='templates')

def get_db():
    con = sqlite3.connect('twitter_clone.db')
    con.row_factory = sqlite3.Row
    return con

def check_credentials(request: Request):
    '''
    return username is user is logged in
    if not logged in, returns none
    '''

    # query_username = request.query_params.get('username')
    # query_password = request.query_params.get('password')
    # print('query_username=', query_username)
    # print('query_password=', query_password)

    cookie_username = request.cookies.get('username')
    cookie_password = request.cookies.get('password')
    print('cookie_username=', cookie_username)
    print('cookie_password=', cookie_password)

    if not cookie_username or not cookie_password:
        return None

    con = get_db()
    cur = con.cursor()
    cur.execute(
        'SELECT username FROM users WHERE username = ? AND password = ?',
        (cookie_username, cookie_password)
    )
    row = cur.fetchone()
    con.close()
 
    if row:
        return row['username']
    return None

@app.get('/', response_class=HTMLResponse)
async def index(request: Request):
    is_logged_in = check_credentials(request)

    # extract username from database
    con = sqlite3.connect('twitter_clone.db')
    cur = con.cursor()
    sql = """
    SELECT messages.message, messages.created_at, users.username, users.age
    FROM messages
    JOIN users ON messages.sender_id = users.id
    ORDER BY messages.created_at DESC;
    """
    cur.execute(sql)
    rows = cur.fetchall()
    con.close()

    messages = [
        {'message': r[0], 'created_at': r[1], 'username': r[2], 'age': r[3]}
        for r in rows
    ]

    # for row in cur.fetchall():
        # username = row[0]

    # create response
    return templates.TemplateResponse(
        request=request,
        name='index.html',
        context={
            'is_logged_in': check_credentials(request), 
            'username': check_credentials(request),
            'messages': messages,
        }
    )

@app.get('/logout', response_class=HTMLResponse)
async def logout(request: Request):
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

@app.get('/create_message', response_class=HTMLResponse)
async def create_message(request: Request):
    return templates.TemplateResponse(
        request=request, 
        name='create_message.html',
        context={
            'is_logged_in': check_credentials(request)
        }
    )

@app.get('/create_user', response_class=HTMLResponse)
async def create_user(request: Request):
    return templates.TemplateResponse(
        request=request, 
        name='create_user.html',
        context={
            'is_logged_in': check_credentials(request)
        }
    )


if __name__ == '__main__':
    uvicorn.run("main:app", host='127.0.0.1', port=8080, reload=True)
