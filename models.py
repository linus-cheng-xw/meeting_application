from app import db

class transcription(db.Model):
	__tablename__ = 'transcriptions'
	Id = db.Column(db.Integer, primary_key=True)
	meeting_id = db.Column(db.String, nullable=False)
	speaker_name = db.Column(db.String, nullable=False)
	message = db.Column(db.String, nullable=False)
	spoken_at = db.Column(db.DateTime)

	def __init__(self, meeting_id, speaker_name, message, spoken_at):
		self.meeting_id = meeting_id
		self.speaker_name = speaker_name
		self.message = message
		self.spoken_at = spoken_at

	def __repr__(self):
		return '<Id {}>'.format(self.Id)
	
	def serialize(self):
		return {
			'Id': self.Id, 
			'meeting_id': self.meeting_id,
			'speaker_name': self.speaker_name,
			'message': self.message, 
			'spoken_at': self.spoken_at
		}