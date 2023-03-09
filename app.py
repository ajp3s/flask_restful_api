from flask import Flask
from flask_restful import Resource, Api, reqparse, abort

app = Flask("VideoApi")
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('title', required=True)
parser.add_argument('upload date', type=int, required=False)

videos = {
    "video1": {"title": "Tony's adventures with flask", "upload date": 220221},
    "video2": {"title": "It' not all that complicated", "upload date": 270221},
    "video3": {"title": "You all can do it too", "upload date": 220223}
}


class Video(Resource):

    def get(self, video_id):
        if video_id == 'all':
            return videos
        else:
            return videos[video_id]

    def put(self, video_id):
        if video_id not in videos.keys():
            args = parser.parse_args()
            new_video = {'title': args['title']}
            videos[video_id] = new_video
            return {video_id: videos[video_id]}, 201
        else:
            abort(409, message=f'Video with title: {video_id} already exists')

    def delete(self, video_id):
        if video_id in videos:
            del videos[video_id]
            return '', 204

        else:
            abort(404, message=f'Video {video_id} not found')


class VideoSchedule(Resource):
    def get(self):
        return videos

    def post(self):
        args = parser.parse_args()
        new_video = {'title': args['title']}
        video_id = max(int(x.lstrip("video")) for x in videos.keys()) + 1
        video_id = f"video{video_id}"
        videos[video_id] = new_video
        return videos[video_id], 201

    def delete(self, video_id):
        if video_id in videos:
            del videos[video_id]
            return '', 204

        else:
            abort(404, message=f'Video {video_id} not found')


api.add_resource(Video, '/videos/<video_id>')
api.add_resource(VideoSchedule, '/videos')


if __name__ == '__main__':
    app.run()
