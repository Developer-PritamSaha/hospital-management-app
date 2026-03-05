from ..extensions import db

class Notification(db.Model):
    __tablename__ = 'notification'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True) 
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    data = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(30), nullable=False)