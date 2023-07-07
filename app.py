import os

import werkzeug
from flask import Flask
from flask_restful import Resource, Api, reqparse, abort
from flask_sqlalchemy import SQLAlchemy
import boto3

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://Tony:uniquepassword123@localhost/flask_restfull_api'
db = SQLAlchemy(app)
api = Api(app)

s3 = boto3.client(
    's3',
    aws_access_key_id=os.environ['YOUR_AWS_ACCESS_KEY_ID'],
    aws_secret_access_key=os.environ['YOUR_AWS_SECRET_ACCESS_KEY']
)
bucket_name = 'ajp3s-bucket-1'

parser = reqparse.RequestParser()
parser.add_argument('title', required=True)
parser.add_argument('upload_date', type=int, required=False)
parser.add_argument('file', type=werkzeug.datastructures.FileStorage, location='files')


class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    upload_date = db.Column(db.Integer)
    url = db.Column(db.String(250))

    def __init__(self, title, upload_date):
        self.title = title
        self.upload_date = upload_date


class ImageResource(Resource):
    def get(self, video_id):
        with app.app_context():
            image = Image.query.get(video_id)
            if image:
                return {'title': image.title, 'upload_date': image.upload_date, 'video_url': image.video_url}
            else:
                abort(404, message=f'Video {video_id} not found')

    def post(self, image_id):
        with app.app_context():
            image = Image.query.get(image_id)
            if not image:
                args = parser.parse_args()
                new_image = Image(title=args['title'], upload_date=args['upload_date'])
                db.session.add(new_image)
                db.session.commit()
                file = args['file']
                if file:
                    filename = f"{image_id}_{file.filename}"
                    s3.upload_fileobj(file.stream, bucket_name, filename)
                    image_url = f"https://{bucket_name}.s3.amazonaws.com/{filename}"
                    new_image.url = image_url
                    db.session.commit()

                    return {'title': new_image.title, 'upload_date': new_image.upload_date, 'image_url': image_url}, 201
                else:
                    return {'title': new_image.title, 'upload_date': new_image.upload_date}, 201
            else:
                abort(409, message=f'Video {image_id} already exists')

    def delete(self, image_id):
        with app.app_context():
            image = Image.query.get(image_id)
            if image:
                db.session.delete(image)
                db.session.commit()
                if image.file_url:
                    file_key = image.file_url.split('/')[-1]
                    s3.delete_object(Bucket=bucket_name, Key=file_key)

                return '', 204
            else:
                abort(404, message=f'image {image_id} not found')


api.add_resource(ImageResource, '/images/<image_id>')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
