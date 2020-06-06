from flask_restplus import Namespace, Resource, fields
from repository.surah import Surah
from fireo.utils.utils import generateKeyFromId

api = Namespace('surah', description='Quran Surahs')

surahModel = api.model('Surah', {
    'id': fields.String(),
    'number': fields.Integer(),
    'name': fields.String(),
    'english_name': fields.String(),
    'english_name_translation': fields.String(),
    'number_of_ayahs': fields.Integer(),
    'revelation_type': fields.String(enum=['meccan', 'medinan']),
})


@api.route('/all')
class GetAllSurahs(Resource):
    @api.marshal_list_with(surahModel, envelope='items')
    def get(self):
        surahs = Surah.collection.order('number').fetch()
        return list(surahs)


@api.param('id', 'ID of surah, must be within 1-114')
@api.route('/<string:id>')
class GetSurahById(Resource):
    @api.marshal_with(surahModel)
    @api.response(404, 'No surah for this id, ID must be in 1-114')
    def get(self, id):
        surah = Surah.collection.get(key=generateKeyFromId(Surah, id))
        if surah:
            return surah
        api.abort(404, 'No surah for this id, ID must be in 1-114')


@api.param('revelation_type', 'Type of Revelation, Meccan or Medinan')
@api.route('/type/<string:revelation_type>')
class GetSurahByRevelationType(Resource):
    @api.marshal_list_with(surahModel, envelope='items')
    @api.response(404, 'Type must be Meccan or Medinan')
    def get(self, revelation_type):
        surahs = Surah.collection.filter(
            revelation_type=revelation_type).fetch()
        surah_list = list(surahs)
        if len(surah_list) > 0:
            return surah_list

        api.abort(404, 'Type must be Meccan or Medinan')
