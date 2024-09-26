import pytest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from main import db, User, Games, Achievement

@pytest.fixture
def flask_app_mock():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:ja23paNpanda@localhost/games'
    db.init_app(app)
    return app

@pytest.fixture
def mock_user_table():
    user = User()
    user.username = 'user1'
    user.email = '<EMAIL>'
    user.password = '<PASSWORD>'
    user.primary_platform = 'playstation'




@pytest.fixture
def mock_get_sqlalchemy(mocker):
    mock = mocker.patch('flask_sqlalchemy._QueryProperty.__get__').return_value = mocker.Mock()
    return mock


class TestUserMethods:
    def test_get_login(self, flask_app_mock, mock_user_table):
        with flask_app_mock.app_context():
            user = User.get_login(1)
            assert user is not None
            assert user.username == 'user'
            assert user.email == 'bob@gmail.com'
            assert user.password == 'password'
            assert user.primary_platform == 'playstation'

    def test_get_by_username(self, flask_app_mock, mock_user_table):
        with flask_app_mock.app_context():
            user = User.get_by_username('user')
            assert user is not None
            assert user.username == 'user'
            assert user.email == 'bob@gmail.com'
            assert user.password == 'password'
            assert user.primary_platform == 'playstation'

    def test_get_by_platform_andname(self, flask_app_mock):
        with flask_app_mock.app_context():
            game = Games.get_game_by_platform_and_name('PlayStation', 'FALLOUT 4')
            assert game is not None
            assert game.game_name == 'FALLOUT 4'
            assert game.platform == 'PlayStation'
            assert game.publisher == 'BETHESDA'

    def test_get_name(self, flask_app_mock):
        with flask_app_mock.app_context():
            game = Games.get_game_name('FALLOUT 4')
            assert game is not None
            assert len(game) == 1

    def test_get_platform(self, flask_app_mock):
        with flask_app_mock.app_context():
            game = Games.get_platform('PlayStation')
            assert game is not None
            assert len(game) == 1

    def test_get_exclusive(self, flask_app_mock):
        with flask_app_mock.app_context():
            game = Games.get_exclusive()
            assert game is not None
            assert len(game) == 0

    def test_get_publisher(self, flask_app_mock):
        with flask_app_mock.app_context():
            game = Games.get_publisher('BETHESDA')
            assert game is not None
            assert len(game) == 1

    def test_get_top_10_length(self, flask_app_mock):
        with flask_app_mock.app_context():
            game = Achievement.get_top_10_rare_achievements('FALLOUT 4')
            assert game is not None
            assert len(game) <= 10
