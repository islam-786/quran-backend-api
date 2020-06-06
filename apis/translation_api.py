from flask_restplus import Namespace, Resource, fields, reqparse
from repository.translation import Translation
from fireo.utils.utils import generateKeyFromId

api = Namespace('translation', description='Quranic Ayahs translation')

translationModel = api.model('Translation', {
    'id': fields.String(),
    'ayah_id': fields.String(),
    'edition_id': fields.String(),
    'ayah_number': fields.Integer(),
    'text': fields.String(),
})

translationModelList = api.model('TranslationList', {
    'items': fields.List(fields.Nested(translationModel)),
    'result_count': fields.Integer(),
    'cursor': fields.String(),
})


@api.param('id', 'Translation id is combination of editionId_surahId-ayahId (e.g en.sahih_1-0)')
@api.route('/<string:id>')
class GetTranslationById(Resource):
    @api.marshal_with(translationModel)
    @api.response(404, 'No translation related to this id please check you ID')
    def get(self, id):
        translation = Translation.collection.get(
            key=generateKeyFromId(Translation, id))
        if translation:
            return translation
        api.abort(404, 'No translation related to this id please check you ID')


edition_args = reqparse.RequestParser()
edition_args.add_argument('edition', type=str, required=False, choices=[
                          'en.sahih', 'ur.maududi'], default='en.sahih')


@api.param('id', 'ID of Ayah, id can be combination of surahNumber-ayahNumberInSurah (e.g 1-1) or ayahNumber (e.g 2)')
@api.route('/ayah/<string:id>')
class GetTranslationByAyahId(Resource):
    @api.marshal_with(translationModel)
    @api.response(404, 'No translation related to this Ayah ID')
    @api.response(500, 'Not a valid ID fromat')
    @api.expect(edition_args, validate=True)
    def get(self, id):
        args = edition_args.parse_args()
        edition = args['edition']

        if "-" in id:
            # Get translation with Ayah ID
            trans_id = edition + "_" + id
            translation = Translation.collection.get(
                key=generateKeyFromId(Translation, trans_id))
            if translation:
                return translation
            api.abort(404, 'No translation related to this Ayah ID')
        else:
            # Get translation with Ayah Number
            try:
                translation = Translation.collection.filter(
                    edition_id=edition, ayah_number=int(id)).get()
                if translation:
                    return translation
                api.abort(404, 'No translation related to this Ayah ID')
            except:
                api.abort(500, 'Not a valid ID fromat')

        api.abort(500, 'Not a valid ID fromat')


pagination_args = reqparse.RequestParser()
pagination_args.add_argument(
    'cursor', type=str, required=False, help='Cursor retrieved from previous result')
pagination_args.add_argument(
    'limit', type=int, help="Number of results", default=None)


@api.param('id', 'ID of edition')
@api.route('/edition/<string:id>')
class GetTranslationByEditionId(Resource):
    @api.marshal_with(translationModelList)
    @api.response(404, 'No translation found related to this edition')
    @api.response(500, 'Internal Server Error')
    @api.expect(pagination_args, validate=True)
    def get(self, id):
        args = pagination_args.parse_args()
        print(args)

        if args['cursor']:
            translations = Translation.collection.cursor(
                args['cursor']).fetch(args['limit'])
            translations_list = list(translations)
            if len(translations_list) > 0:
                return {
                    'result_count': len(translations_list),
                    'cursor': translations.cursor,
                    'items': translations_list
                }
            api.abort(404, 'No translation found related to this edition')
        else:
            translations = Translation.collection.filter(
                edition_id=id).order('ayah_number').fetch(args['limit'])
            translations_list = list(translations)
            if len(translations_list) > 0:
                return {
                    'result_count': len(translations_list),
                    'cursor': translations.cursor,
                    'items': translations_list
                }
            api.abort(404, 'No translation found related to this edition')

        api.abort(500, 'Internal Server Error')
