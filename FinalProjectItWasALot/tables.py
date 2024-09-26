from collections import Counter

from flask_login import *
from flask_sqlalchemy import *
from sqlalchemy import func
from sqlalchemy.orm import relationship

db = SQLAlchemy()


class Achievement(db.Model):
    achievement_id = db.Column(db.Integer, primary_key=True)
    achievement_name = db.Column(db.String(100))
    achievement_description = db.Column(db.String(1000))
    achievement_rarity = db.Column(db.String(25))
    achievement_time = db.Column(db.String(25))
    game_id = db.Column(db.Integer, db.ForeignKey('games.game_id'))
    achiever_id = db.Column(db.Integer, db.ForeignKey('users.uid'))
    game = relationship('Games', backref='achievements')

    @classmethod
    def get_achievements(cls, game_name, platform, developer, rarity_threshold):
        return cls.query.join(Games).filter(
            Games.game_name == game_name,
            Games.platform == platform,
            Games.publisher == developer,
            cls.achievement_rarity <= rarity_threshold
        ).all()

    @classmethod
    def get_top_10_rare_achievements(cls, game_name):
        return (cls.query.join(Games).filter(Games.game_name == game_name).order_by
                (cls.achievement_rarity.desc()).limit(10).all())

    @classmethod
    def get_total_achievements_above(cls, game_name, platform, developer, rarity_threshold):
        hardest_achievements = cls.query.join(Games).filter(
            Games.game_name == game_name,
            Games.publisher == developer,
            cls.achievement_rarity <= rarity_threshold,
            Games.platform == platform
        ).order_by(cls.achievement_time.desc()).all()
        total_achievements_above = len(hardest_achievements)
        return total_achievements_above

    @classmethod
    def get_platforms_displayed(cls):
        top_10_hardest_achievements = cls.query.order_by(cls.achievement_time.desc()).limit(10).all()
        platforms_displayed = set(achievement.game.platform for achievement in top_10_hardest_achievements)
        return platforms_displayed

    @classmethod
    def get_most_listed_platform(cls):
        top_10_hardest_achievements = cls.query.order_by(cls.achievement_time.desc()).limit(10).all()
        platform_counter = Counter(achievement.game.platform for achievement in top_10_hardest_achievements)
        most_listed_platform = platform_counter.most_common(1)[0][0] if platform_counter else None
        return most_listed_platform


class User(db.Model, UserMixin):

    __tablename__ = 'users'

    uid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(25), unique=True)
    password = db.Column(db.String(15))
    email = db.Column(db.String(50))
    primary_platform = db.Column(db.String(20))
    achiever_id = db.Column(db.Integer, autoincrement=True)

    achievements = db.relationship('Achievement', backref='achiever')

    def get_id(self):
        return self.uid

    @classmethod
    def get_login(cls, uid):
        return cls.query.get(int(uid))

    @classmethod
    def get_by_username(cls, username):
        return cls.query.filter_by(username=username).first()


class Games(db.Model):
    game_id = db.Column(db.Integer, primary_key=True)
    game_name = db.Column(db.String(50))
    publisher = db.Column(db.String(50))
    platform = db.Column(db.String(20))
    exclusive = db.Column(db.Boolean, default=False)

    @classmethod
    def get_game_by_platform_and_name(cls, platform, game_name):
        return cls.query.filter_by(game_name=game_name, platform=platform).first()

    @classmethod
    def get_game_name(cls, game_name):
        return cls.query.filter_by(game_name=game_name).all()

    @classmethod
    def get_platform(cls, platform):
        return cls.query.filter_by(platform=platform).all()

    @classmethod
    def get_publisher(cls, publisher):
        return cls.query.filter_by(publisher=publisher).all()

    @classmethod
    def get_exclusive(cls):
        return cls.query.filter_by(exclusive=True).all()


class System(db.Model):
    console_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    console_name = db.Column(db.String(50))