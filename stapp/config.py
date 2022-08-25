import pytz

port = 8000
BASE_URL = f'http://127.0.0.1:{port}'
URL_USERS = f'{BASE_URL}/users'
URL_USER = f'{BASE_URL}/user'
URL_POSTS = f'{BASE_URL}/posts'
URL_POST = f'{BASE_URL}/post'
LOCAL_TZ = pytz.timezone('Asia/Taipei')
