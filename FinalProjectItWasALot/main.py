from flask import Flask, render_template, request, redirect, url_for, flash, session, abort, jsonify
import os
from tables import *

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:password@databasetablename'
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)



def generate_csrf_token():
    if '_csrf_token' not in session:
        session['_csrf_token'] = os.urandom(24)
    return session['_csrf_token']


@app.context_processor
def inject_csrf_token():
    return {'csrf_token': generate_csrf_token}


@login_manager.user_loader
def load_user(uid):
    return User.get_login(uid)



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.get_by_username(username)
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Incorrect username or password')
            return redirect(url_for('login'))




@app.route('/home')
@login_required
def home():
    print(current_user)
    return render_template('home.html', username=current_user.uid)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')
    elif request.method == 'POST':
        username = request.form['username']
        user = User.get_by_username(username)
        if user is None:
            password = request.form['password']
            email = request.form['email']
            platform = request.form['platform']

            user = User()
            user.username = username
            user.password = password
            user.email = email
            user.primary_platform = platform
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('login'))
        else:
            flash('This username is already taken')
            return redirect(url_for('signup'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/add_game', methods=['GET', 'POST'])
@login_required
def add_game():
    if request.method == 'POST':
        game = Games()
        game.game_name = request.form['name'].upper()
        game.publisher = request.form['publisher'].upper()
        game.platform = request.form['platform']
        if request.form['exclusive'] == 'Y':
            game.exclusive = True
        else:
            game.exclusive = False
        db.session.add(game)
        db.session.commit()
        return redirect(url_for('add'))


@app.route('/add_achievement', methods=['GET', 'POST'])
@login_required
def add_achievement():
    if request.method == 'POST':
        game_name = request.form['name'].upper()
        platform = request.form['platform']
        game = Games.get_game_by_platform_and_name(platform, game_name)
        user = User.query.filter_by(username=current_user.username).first()
        if game:
            print(type(game))
            new_achievement = Achievement()
            new_achievement.game_id = game.game_id
            new_achievement.achiever_id = current_user.uid
            new_achievement.achievement_name = request.form['achievement_name'].upper()

            new_achievement.achievement_description = request.form['description'].upper()
            new_achievement.achievement_rarity = request.form['rarity'].upper()
            new_achievement.achievement_time = request.form['time']
            db.session.add(new_achievement)
            db.session.commit()
            return redirect(url_for('add'))
        else:
            flash('Game not found')
            return redirect(url_for('add'))
    else:
        return jsonify({'error': 'Method not allowed'}), 405


@app.route('/add_console', methods=['GET', 'POST'])
@login_required
def add_console():
    if request.method == 'POST':
        system = System()
        system.console_name = request.form['console_name']
        db.session.add(system)
        db.session.commit()
        return redirect(url_for('add'))

@app.route('/search_game', methods=['GET', 'POST'])
@login_required
def search_game():
    if request.method == 'POST':
        name = request.form.get('name').upper()
        platform = request.form.get('platform')
        publisher = request.form.get('publisher').upper()
        if request.form['exclusive'].upper() == "Y":
            exclusive = True
        else:
            exclusive = None

        if name or platform or publisher or exclusive:
            games = Games.query

            if name:
                games = Games.get_game_name(name)
            if platform:
                games = Games.get_platform(platform)
            if publisher:
                games = Games.get_publisher(publisher)
            if exclusive:
                games = Games.get_exclusive()

            if games:
                return render_template('result_of_game_search.html', games=games)
            else:
                flash('Game not found with this search criteria')
                return redirect(url_for('search_game'))
        else:
            flash('Please provide at least one search criteria')
            return redirect(url_for('search_game'))

    return render_template('search_game.html')

@app.route('/display_all_achieve', methods=['GET', 'POST'])
@login_required
def display_all_achieve():
    if request.method == 'POST':
        game = request.form['game'].upper()
        platform = request.form['platform'].upper()
        developer = request.form['developer'].upper()
        difficulty = request.form['difficulty']
        achievements = Achievement.get_achievements(game, platform, developer, difficulty)
        top_10 = Achievement.get_top_10_rare_achievements(game)
        total_amount = Achievement.get_total_achievements_above(game, platform, developer, difficulty)
        platforms_displayed = Achievement.get_platforms_displayed()
        most_listed_platform = Achievement.get_most_listed_platform()

        if achievements is None:
            flash('No achievements could be found with these given criteria')
            return redirect(url_for('display_all_achieve'))
        elif achievements is not None:
            return render_template('display_achievement_stuff.html', achievements=achievements,
                                   game=game, platform=platform, difficulty=difficulty,
                                   top_10=top_10, total_amount=total_amount, platforms_displayed=platforms_displayed,
                                   most_listed_platform=most_listed_platform)

    return render_template('display_all_achieve.html')


@app.route('/display_achievement_stuff', methods=['GET', 'POST'])
@login_required
def display_achievement_stuff():
    return render_template('display_achievement_stuff.html', username=current_user.username)

@app.route('/result_of_game_search', methods=['GET', 'POST'])
@login_required
def result_of_game_search():
    return render_template('result_of_game_search.html', username=current_user.uid)
@app.route('/add')
@login_required
def add():
    return render_template('add.html', username=current_user.uid)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        name = User.query.filter_by(username='user').first()
        if name is None:
            user = User()
            user.username = 'user'
            user.password = 'password'
            user.email = 'bob@gmail.com'
            user.platform = 'PlayStation'
            db.session.add(user)
            db.session.commit()
            game = Games()
            game.game_name = 'FALLOUT 4'
            game.publisher = 'BETHESDA'
            game.platform = 'PlayStation'
            game.exclusive = False
            db.session.add(game)
            db.session.commit()
    app.run(debug=True)
