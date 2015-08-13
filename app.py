# coding: utf-8

from elegon.app import create_app

app = create_app(init=True)

if __name__ == '__main__':
    app.run('0.0.0.0', 5000, debug=True)
