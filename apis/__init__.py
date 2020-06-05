from flask_restplus import Api

from .edition_api import api as edition_api

api = Api(
    title='My Title',
    version='1.0',
    description='A description',
)

api.add_namespace(edition_api)
