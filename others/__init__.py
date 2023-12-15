from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    HOSTNAME = "127.0.0.1"
    PORT = "3306"
    USERNAME = "root"
    PASSWORD = "301218"
    DATABASE = "insider_threats"
    app.config[
        "SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://{USERNAME}:{PASSWORD}@{HOSTNAME}:{PORT}/{DATABASE}?charset=utf8"
    db.init_app(app)
    # 注册蓝图
    from views.scene_one import bp as scene_one_bp
    from views.scene_two import bp as scene_two_bp
    from views.scene_three import bp as scene_three_bp
    app.register_blueprint(scene_one_bp)
    app.register_blueprint(scene_two_bp)
    app.register_blueprint(scene_three_bp)

    return app
