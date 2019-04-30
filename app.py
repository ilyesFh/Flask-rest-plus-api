from flask import Flask, Blueprint, request
from flask_restplus import Api, Resource, fields
from marshmallow import fields as ma_field, post_load, Schema
from functools import wraps

authorizations = {
    'apiKey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'X-API-KEY'
    }

}

app = Flask(__name__)
api = Api(app, authorizations=authorizations)


# blueprint = Blueprint('api', __name__, url_prefix='/api')
# api = Api(blueprint, doc='/documentation')
# app.register_blueprint(blueprint)


def token_required(f):
    @wraps(f)
    def decoreted(*args, **kwargs):
        token = None
        if 'X-API-kEY' in request.headers:
            token = request.headers['X-API-KEY']
        if not token:
            return {'Message': 'token is missing.'}, 401
        if token != 'mytoken':
            return {'Message': 'Your token is wrong!!!.'}, 401

        print('Token: {}'.format(token))
        return f(*args, **kwargs)

    return decoreted


class TheLanguage(object):
    def __init__(self, language, framework):
        self.language = language
        self.framework = framework

    def __repr__(self):
        return ' {} is the language. {} is the framework. '.format(self.language, self.framework)


class LanguageSchema(Schema):
    language = ma_field.String()
    framework = ma_field.String()

    @post_load
    def create_language(self, data):
        return TheLanguage(**data)


languages = []
# language = {'language': 'Python', 'id': 1}
python = TheLanguage(language='Python', framework='Flask')
languages.append(python)
a_language = api.model('Language',
                       {'language': fields.String('The language.'), 'framework': fields.String('The framework')})


@api.route('/languages')
class Language(Resource):
    # @api.marshal_with(a_language, envelope='the_data')
    @api.doc(security='apiKey')
    @token_required
    def get(self):
        schema = LanguageSchema(many=True)
        return schema.dump(languages)

    @api.expect(a_language)
    def post(self):
        schema = LanguageSchema()
        new_language = schema.load(api.payload)
        languages.append(new_language)
        # languages.append(new_language)
        print(languages)

        # new_language['id'] = len(languages) + 1
        # languages.append(new_language)
        return {'result': 'language added.'}, 201


if __name__ == '__main__':
    app.run(debug=True)
