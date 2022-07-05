from os import environ
from whatsapp import app

if __name__ == '__main__':
    HOST = environ.get('SERVER_HOST', '0.0.0.0')
    try:
        PORT = int(environ.get('SERVER_PORT', '5000'))
    except ValueError:
        PORT = 5000
    app.debug = True
    app.run(HOST, PORT)
    # app.run('0.0.0.0', 5000)
