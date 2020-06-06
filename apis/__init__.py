from flask import Blueprint
from flask_restplus import Api

from .edition_api import api as edition_api
from .surah_api import api as surah_api
from .translation_api import api as translation_api
from .ayah_api import api as ayah_api

blueprint = Blueprint('api', __name__)
api = Api(blueprint,
          doc='/docs',
          title='Quran API',
          version='1.0',
          description='A description',
          )

api.add_namespace(edition_api)
api.add_namespace(surah_api)
api.add_namespace(translation_api)
api.add_namespace(ayah_api)
