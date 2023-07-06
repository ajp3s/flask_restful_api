from flask import Flask
from flask_restful import Resource, Api, reqparse, abort
from flask_sqlalchemy import SQLAlchemy

app = Flask('ImageAPI')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://Tony:uniquepassword123@localhost/flask_restfull_api'
db = SQLAlchemy(app)
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('title', required=True)
parser.add_argument('upload_date', type=int, required=False)


class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    upload_date = db.Column(db.Integer)

    def __init__(self, title, upload_date):
        self.title = title
        self.upload_date = upload_date


db.create_all()


class VideoResource(Resource):
    def get(self, video_id):
        if video_id == 'all':
            videos = Video.query.all()
            return {video.id: {'title': video.title, 'upload_date': video.upload_date} for video in videos}
        else:
            video = Video.query.get(video_id)
            if video:
                return {'title': video.title, 'upload_date': video.upload_date}
            else:
                abort(404, message=f'Video {video_id} not found')

    def put(self, video_id):
        video = Video.query.get(video_id)
        if not video:
            args = parser.parse_args()
            new_video = Video(title=args['title'], upload_date=args['upload_date'])
            db.session.add(new_video)
            db.session.commit()
            return {'title': new_video.title, 'upload_date': new_video.upload_date}, 201
        else:
            abort(409, message=f'Video {video_id} already exists')

    def delete(self, video_id):
        video = Video.query.get(video_id)
        if video:
            db.session.delete(video)
            db.session.commit()
            return '', 204
        else:
            abort(404, message=f'Video {video_id} not found')


api.add_resource(VideoResource, '/videos/<video_id>')

if __name__ == '__main__':
    app.run(debug=True)
