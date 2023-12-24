from others import db


class User_marking(db.Model):
    __tablename__ = "user_marking"
    ip = db.Column(db.String(100), primary_key=True)
    user = db.Column(db.String(255), nullable=False)
    domain = db.Column(db.String(100), nullable=False)
    identity = db.Column(db.String(50), nullable=False)

    def __init__(self,ip,user,domain,identity):
        self.ip = ip
        self.user = user
        self.domain = domain
        self.identity = identity