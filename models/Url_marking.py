from others import db


class Url_marking(db.Model):
    __tablename__ = "url_marking"
    url = db.Column(db.String(255), primary_key=True)
    domain = db.Column(db.String(20), nullable=False)
    marking = db.Column(db.String(255), nullable=False)

    def __init__(self, url, domain, marking):
        self.url = url
        self.domain = domain
        self.marking = marking