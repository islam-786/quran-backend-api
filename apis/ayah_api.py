from flask_restplus import Namespace, Resource, fields, reqparse
from repository.ayah import Ayah
from repository.surah import Surah
from repository.translation import Translation
from repository.edition import Edition
from fireo.utils.utils import generateKeyFromId

api = Namespace('ayah', description='Ayah of Quran')

ayahModel = api.model('Ayah', {
    'id': fields.String(),
    'surah_id': fields.String(),
    'number': fields.Integer(),
    'number_in_surah': fields.Integer(),
    'arabic': fields.String(),
})

ayahModelList = api.model('AyahList', {
    'items': fields.List(fields.Nested(ayahModel)),
    'result_count': fields.Integer(),
    'cursor': fields.String(),
})


@api.param('id', 'ID of Ayah, id can be combination of surahNumber-ayahNumberInSurah (e.g 1-1) or ayahNumber (e.g 2)')
@api.route('/<string:id>')
class GetAyahById(Resource):
    @api.marshal_with(ayahModel)
    @api.response(404, 'No Ayah related to this ID')
    @api.response(500, 'Not a valid ID format')
    def get(self, id):

        if "-" in id:
            # Get Ayah with ID
            ayah = Ayah.collection.get(key=generateKeyFromId(Ayah, id))
            if ayah:
                return ayah
            api.abort(404, 'No Ayah related to this ID')
        else:
            # Get Ayah by Ayah number
            try:
                ayah = Ayah.collection.filter(number=int(id)).get()
                if ayah:
                    return ayah
                api.abort(404, 'No Ayah related to this ID')
            except:
                api.abort(500, 'Not a valid ID format')

        api.abort(500, 'Not a valid ID format')


edition_args = reqparse.RequestParser()
edition_args.add_argument('edition', type=str, required=False, choices=[
                          'en.sahih', 'ur.maududi'], default='en.sahih')


@api.param('id', 'ID of Ayah, id can be combination of surahNumber-ayahNumberInSurah (e.g 1-1) or ayahNumber (e.g 2)')
@api.route('/detail/<string:id>')
class GetAyahDetail(Resource):
    @api.response(404, 'No Ayah related to this ID')
    @api.response(500, 'Not a valid ID format')
    @api.expect(edition_args, validate=True)
    def get(self, id):

        args = edition_args.parse_args()
        edition = args['edition']

        if "-" in id:
            # Get Ayah with ID
            ayah = Ayah.collection.get(key=generateKeyFromId(Ayah, id))
            if ayah:
                return self._get_detail(ayah, edition)
            api.abort(404, 'No Ayah related to this ID')
        else:
            # Get Ayah by Ayah number
            try:
                ayah = Ayah.collection.filter(number=int(id)).get()
                if ayah:
                    return self._get_detail(ayah, edition)
                api.abort(404, 'No Ayah related to this ID')
            except:
                api.abort(500, 'Not a valid ID format')

        api.abort(500, 'Not a valid ID format')

    def _get_detail(self, ayah, edition_id):
        surah = Surah.collection.get(
            key=generateKeyFromId(Surah, ayah.surah_id))
        edition = Edition.collection.get(
            key=generateKeyFromId(Edition, edition_id))

        trans_id = edition_id + "_" + ayah.id
        translation = Translation.collection.get(
            key=generateKeyFromId(Translation, trans_id))

        return {
            'ayah': ayah.to_dict(),
            'translation': translation.to_dict(),
            'surah': surah.to_dict(),
            'edition': edition.to_dict()
        }


pagination_args = reqparse.RequestParser()
pagination_args.add_argument(
    'cursor', type=str, required=False, help='Cursor retrieved from previous result')
pagination_args.add_argument(
    'limit', type=int, help="Number of results", default=None)


@api.param('id', 'ID of surah')
@api.route('/surah/<string:id>')
class GetAyahBySurahId(Resource):
    @api.marshal_with(ayahModelList)
    @api.response(404, 'No Ayah found related to this surah')
    @api.response(500, 'Internal Server Error')
    @api.expect(pagination_args, validate=True)
    def get(self, id):
        args = pagination_args.parse_args()

        if args['cursor']:
            ayahs = Ayah.collection.cursor(
                args['cursor']).fetch(args['limit'])
            ayah_list = list(ayahs)
            if len(ayah_list) > 0:
                return {
                    'result_count': len(ayah_list),
                    'cursor': ayahs.cursor,
                    'items': ayah_list
                }
            api.abort(404, 'No Ayah found related to this surah')
        else:
            ayahs = Ayah.collection.filter(
                surah_id=id).order('number_in_surah').fetch(args['limit'])
            ayah_list = list(ayahs)
            if len(ayah_list) > 0:
                return {
                    'result_count': len(ayah_list),
                    'cursor': ayahs.cursor,
                    'items': ayah_list
                }
            api.abort(404, 'No Ayah found related to this surah')

        api.abort(500, 'Internal Server Error')
