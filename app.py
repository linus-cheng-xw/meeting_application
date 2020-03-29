#import
import os
import re
import datetime
from flask import Flask, jsonify, request, render_template, url_for
from flask_sqlalchemy import SQLAlchemy

#initialize 
app = Flask(__name__)
app.debug = False

#db config
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://salesforce_user:password@localhost:5432/salesforce_casestudy_db'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from models import transcription


# def meeting_id_validation(meeting_id):
# 	#check format:
# 	if meeting_id == '': 
# 		return 'Please enter a meeting_id'
# 	if not re.fullmatch(r"meet-[a-z]{5}", meeting_id):
# 		return 'Please enter a valid meeting_id'

# def speaker_name_validation(speaker_name):
# 	#check format:
# 	if speaker_name == '': 
# 		return 'Please enter a speaker_name'
# 	if not isinstance(speaker_name, str):
# 		return 'Please enter a valid speaker_name'

# def message_validation(message):
# 	#check format:
# 	if message == '': 
# 		return 'Please enter a message'
# 	if not isinstance(message, str):
# 		return 'Please enter a valid message'

# def spoken_at_validation(spoken_at):
# 	#check format
# 	if spoken_at == '': 
# 		return 'Please enter a spoken_at'

# 	if not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", spoken_at):
# 		return 'Please enter a valid datetime or format, YYYY-MM-DDTHH:MM:ssZ'
	
# 	#check for valid date
# 	my_date = datetime.datetime.strptime(spoken_at,'%Y-%m-%dT%H:%M:%SZ')

# 	if my_date > datetime.datetime.now():
# 		return 'Please enter a valid datetime or format, YYYY-MM-DDTHH:MM:ssZ'

@app.route('/submit', methods=['POST']) 
def submit_message():

	try:
		if 'meeting_id' in request.json:
			meeting_id = request.json['meeting_id']
		else:
			return 'Missing meeting_id parameter'

		if 'speaker_name' in request.json:
			speaker_name = request.json['speaker_name'] 
		else: 
			return 'Missing speaker_name parameter'

		if 'message' in request.json:
			message = request.json['message']
		else:
			return 'Missing message parameter'

		if 'spoken_at' in request.json:
			spoken_at = request.json['spoken_at'] 
		else: 
			return 'Missing spoken_at parameter'
		
		#check meeting_id format:
		if meeting_id == '': 
			return 'Please enter a meeting_id'
		if not re.fullmatch(r"meet-[a-z]{5}", meeting_id):
			return 'Please enter a valid meeting_id'
		
		#check speaker_name format:
		if speaker_name == '': 
			return 'Please enter a speaker_name'
		if not isinstance(speaker_name, str):
			return 'Please enter a valid speaker_name'

		#check message format:
		if message == '': 
			return 'Please enter a message'
		if not isinstance(message, str):
			return 'Please enter a valid message'
		
		#check spoken_at format
		if spoken_at == '': 
			return 'Please enter a spoken_at'

		if not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", spoken_at):
			return 'Please enter a valid datetime or format, YYYY-MM-DDTHH:MM:ssZ'
		
		#check for valid date
		my_date = datetime.datetime.strptime(spoken_at,'%Y-%m-%dT%H:%M:%SZ')

		if my_date > datetime.datetime.now():
			return 'Please enter a valid datetime or format, YYYY-MM-DDTHH:MM:ssZ'

		new_entry = transcription(
		meeting_id=meeting_id, 
		speaker_name=speaker_name,
		message = message,
		spoken_at = spoken_at
		)

		db.session.add(new_entry)
		db.session.commit()

		created_entry = transcription.query.filter_by(speaker_name=speaker_name).first().serialize()
		return jsonify('{} was recorded'.format(created_entry['Id']))

	except Exception as e:
			return (str(e))

@app.route('/', methods = ['GET'])
def get_all_meetings():

	transcriptions = transcription.query.all()
	unique_meeting_ids = {t.serialize()['meeting_id'] for t in transcriptions}
	return render_template('home.html', umid = unique_meeting_ids, title = "Home Page")

@app.route('/meetings', methods = ['GET'])
def show_meeting_transcript():
	#remember to negative slice
	meeting_id = request.args.get('id')
	specific_transcriptions = transcription.query.filter_by(meeting_id = meeting_id).all()

	#check for non-existant meeting
	if len(specific_transcriptions) == 0:
		return 'Meeting does not exist!'
	meeting_transcriptions = [t.serialize() for t in specific_transcriptions]

	length = len(meeting_transcriptions)
	for_sorting = [(meeting_transcriptions[i]['spoken_at'],i) for i in range(length)]

	sorted_timings = sorted(for_sorting, key=lambda tup: tup[0], reverse = True)
	sorted_meeting_transcriptions = [meeting_transcriptions[i[1]] for i in sorted_timings]
	return render_template('meetings.html', meeting_transcriptions = sorted_meeting_transcriptions, title = "meeting transcriptions")

if __name__ == '__main__':
    app.run(debug=False)
