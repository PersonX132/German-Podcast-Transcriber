import json
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

#Vocabulary database table
class Vocabulary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    german = db.Column(db.String(100), nullable=False, unique=True)
    english = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(10), nullable=True)
    details_json = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'german': self.german,
            'english': self.english,
            'gender': self.gender,
            'details': json.loads(self.details_json) if self.details_json else None
        }
      
#transcripts database table
class Transcript(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    audio_filename = db.Column(db.String(200), nullable=False, unique=True)
    transcript_json = db.Column(db.Text, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'audio_url': f'/audio/{self.audio_filename}'
        }
