from others import db
class UrlUserCount(db.Model):
    __tablename__ = "url_user_count"
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    url = db.Column(db.String(255))
    user = db.Column(db.String(255))
    date = db.Column(db.String(255))
    Pc = db.Column(db.String(255))
    count = db.Column(db.Integer)
    one = db.Column(db.Integer)
    two = db.Column(db.Integer)
    three = db.Column(db.Integer)
    four = db.Column(db.Integer)
