import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = 'dev'
    # Update database path to use instance folder
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'instance', 'todo.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False