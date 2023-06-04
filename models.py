from flask_sqlalchemy import SQLAlchemy 

db = SQLAlchemy()


class Request(db.Model):
    __tablename__ = 'request'
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime)
    

class Parameter(db.Model):
    __tablename__ = 'parameter'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    value = db.Column(db.String(100))
    request_id = db.Column(db.Integer, db.ForeignKey('request.id'))
    request = db.relationship('Request', backref='parametrs')


class Group(db.Model):
    __tablename__ = 'group'
    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(300))


class ReceivedGroup(db.Model):
    __tablename__ = 'received_group'
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.BigInteger, db.ForeignKey('group.id'))
    group = db.relationship('Group', backref='received_group')
    request_id = db.Column(db.Integer, db.ForeignKey('request.id'))
    request = db.relationship('Request', backref='received_groups')