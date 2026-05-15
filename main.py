'''
Starts a webserver for the website.
'''

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import sqlite3

app = FastAPI()
app.mount('/static', StaticFiles(directory='static'), name='static')
templates = Jinja2Templates(directory='templates')

import re

def make_links(text):
    url_pattern = re.compile(r'(https?://\S+)')
    return url_pattern.sub(r'<a href="\1">\1</a>', text)

templates.env.filters['make_links'] = make_links

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
    try:
        page = int(request.query_params.get('page', 1))
        if page < 1:
            page = 1
    except ValueError:
        page = 1
    offset = (page - 1) * 50

    con = get_db()
    cur = con.cursor()
    
    # get total message count for next button
    cur.execute('SELECT COUNT(*) FROM messages')
    total = cur.fetchone()[0]
    
    cur.execute('''
        SELECT messages.id, messages.message, messages.created_at, users.username, users.age
        FROM messages
        JOIN users ON messages.sender_id = users.id
        ORDER BY messages.created_at DESC
        LIMIT 50 OFFSET ?
    ''', (offset,))
    rows = cur.fetchall()
    con.close()

    messages = [
        {
            'id': row['id'],
            'message': row['message'],
            'created_at': row['created_at'],
            'username': row['username'],
            'age': row['age'] if row['age'] is not None else 'N/A',
        }
        for row in rows
    ]

    return templates.TemplateResponse(
        request=request,
        name='index.html',
        context={
            'is_logged_in': check_credentials(request),
            'messages': messages,
            'page': page,
            'has_next': (offset + 50) < total,
            'has_prev': page > 1,
        }
    )

@app.get('/logout', response_class=HTMLResponse)
async def logout(request: Request):
    response = templates.TemplateResponse(
        request=request,
        name='logout.html',
        context={'is_logged_in': None}
    )
    response.delete_cookie(key='username')
    response.delete_cookie(key='password')
    return response

@app.get('/login', response_class=HTMLResponse)
async def login_get(request: Request):
    return templates.TemplateResponse(
        request=request,
        name='login.html',
        context={
            'is_logged_in': check_credentials(request),
            'error': None,
        }
    )

@app.post('/login', response_class=HTMLResponse)
async def login_post(request: Request):
    form = await request.form()
    username = form.get('username', '').strip()
    password = form.get('password', '')
 
    if not username or not password:
        return templates.TemplateResponse(
            request=request,
            name='login.html',
            context={
                'is_logged_in': None,
                'error': 'Please enter both username and password.',
            }
        )
 
    con = get_db()
    cur = con.cursor()
    cur.execute(
        'SELECT username FROM users WHERE username = ? AND password = ?',
        (username, password)
    )
    row = cur.fetchone()
    con.close()
 
    if row is None:
        return templates.TemplateResponse(
            request=request,
            name='login.html',
            context={
                'is_logged_in': None,
                'error': 'Invalid username or password.',
            }
        )
 
    response = RedirectResponse(url='/', status_code=303)
    response.set_cookie(key='username', value=username, httponly=True)
    response.set_cookie(key='password', value=password, httponly=True)
    return response

@app.get('/create_user', response_class=HTMLResponse)
async def create_user(request: Request):
    return templates.TemplateResponse(
        request=request, 
        name='create_user.html',
        context={
            'is_logged_in': check_credentials(request),
            'error': None,
        }
    )

@app.post('/create_user', response_class=HTMLResponse)
async def create_user_post(request: Request):
    form = await request.form()
    username = form.get('username', '').strip()
    password = form.get('password', '')
    password2 = form.get('password2', '')
    age = form.get('age', '').strip()
 
    if not username or not password:
        return templates.TemplateResponse(
            request=request,
            name='create_user.html',
            context={
                'is_logged_in': None,
                'error': 'Username and password are required.',
            }
        )
 
    if password != password2:
        return templates.TemplateResponse(
            request=request,
            name='create_user.html',
            context={
                'is_logged_in': None,
                'error': 'Passwords do not match.',
            }
        )
 
    age_val = int(age) if age.isdigit() else None
 
    con = get_db()
    cur = con.cursor()
    try:
        cur.execute(
            'INSERT INTO users (username, password, age) VALUES (?, ?, ?)',
            (username, password, age_val)
        )
        con.commit()
    except sqlite3.IntegrityError:
        con.close()
        return templates.TemplateResponse(
            request=request,
            name='create_user.html',
            context={
                'is_logged_in': None,
                'error': f'Username "{username}" is already taken.',
            }
        )
    con.close()
 
    # Auto-login and redirect to home (optional task)
    response = RedirectResponse(url='/', status_code=303)
    response.set_cookie(key='username', value=username, httponly=True)
    response.set_cookie(key='password', value=password, httponly=True)
    return response

@app.get('/create_message', response_class=HTMLResponse)
async def create_message_get(request: Request):
    username = check_credentials(request)
    if not username:
        return RedirectResponse(url='/login', status_code=303)
    return templates.TemplateResponse(
        request=request,
        name='create_message.html',
        context={
            'is_logged_in': username,
            'error': None,
        }
    )

@app.post('/create_message', response_class=HTMLResponse)
async def create_message_post(request: Request):
    username = check_credentials(request)
    if not username:
        return RedirectResponse(url='/login', status_code=303)
 
    form = await request.form()
    message = form.get('message', '').strip()
 
    if not message:
        return templates.TemplateResponse(
            request=request,
            name='create_message.html',
            context={
                'is_logged_in': username,
                'error': 'Message cannot be empty.',
            }
        )
 
    con = get_db()
    cur = con.cursor()
    cur.execute('SELECT id FROM users WHERE username = ?', (username,))
    row = cur.fetchone()
    sender_id = row['id']
 
    cur.execute(
        'INSERT INTO messages (sender_id, message) VALUES (?, ?)',
        (sender_id, message)
    )
    con.commit()
    con.close()
 
    return RedirectResponse(url='/', status_code=303)

@app.get('/json')
async def messages_json(request: Request):
    con = get_db()
    cur = con.cursor()
    cur.execute('''
        SELECT messages.message, messages.created_at, users.username, users.age
        FROM messages
        JOIN users ON messages.sender_id = users.id
        ORDER BY messages.created_at DESC
    ''')
    rows = cur.fetchall()
    con.close()

    messages = [
        {
            'message': row['message'],
            'created_at': row['created_at'],
            'username': row['username'],
            'age': row['age'] if row['age'] is not None else None,
        }
        for row in rows
    ]

    return JSONResponse(content={'messages': messages})

@app.post('/delete_message/{message_id}')
async def delete_message(message_id: int, request: Request):
    username = check_credentials(request)
    if not username:
        return RedirectResponse(url='/login', status_code=303)

    con = get_db()
    cur = con.cursor()
    # only let users delete their own messages
    cur.execute('''
        DELETE FROM messages 
        WHERE id = ? AND sender_id = (SELECT id FROM users WHERE username = ?)
    ''', (message_id, username))
    con.commit()
    con.close()

    return RedirectResponse(url='/', status_code=303)

@app.post('/delete_account')
async def delete_account(request: Request):
    username = check_credentials(request)
    if not username:
        return RedirectResponse(url='/login', status_code=303)

    con = get_db()
    cur = con.cursor()
    cur.execute('DELETE FROM messages WHERE sender_id = (SELECT id FROM users WHERE username = ?)', (username,))
    cur.execute('DELETE FROM users WHERE username = ?', (username,))
    con.commit()
    con.close()

    response = RedirectResponse(url='/', status_code=303)
    response.delete_cookie(key='username')
    response.delete_cookie(key='password')
    return response

@app.get('/search', response_class=HTMLResponse)
async def search(request: Request):
    query = request.query_params.get('q', '').strip()
    messages = []
    
    if query:
        con = get_db()
        cur = con.cursor()
        cur.execute('''
            SELECT messages.id, messages.message, messages.created_at, users.username, users.age
            FROM messages
            JOIN users ON messages.sender_id = users.id
            WHERE messages.message LIKE LOWER(?)
            ORDER BY messages.created_at DESC
        ''', (f'%{query}%',))
        rows = cur.fetchall()
        con.close()

        messages = [
            {
                'id': row['id'],
                'message': row['message'],
                'created_at': row['created_at'],
                'username': row['username'],
                'age': row['age'] if row['age'] is not None else 'N/A',
            }
            for row in rows
        ]

    return templates.TemplateResponse(
        request=request,
        name='search.html',
        context={
            'is_logged_in': check_credentials(request),
            'messages': messages,
            'query': query,
        }
    )

if __name__ == '__main__':
    uvicorn.run("main:app", host='127.0.0.1', port=8080, reload=True)
