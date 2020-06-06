from flask_restplus import Namespace, Resource, fields
from repository.edition import Edition
from fireo.utils.utils import generateKeyFromId

api = Namespace('edition', description='Available editions for Quran')

editionModel = api.model('Edition', {
    'id': fields.String(),
    'language': fields.String(),
    'name': fields.String(),
    'translator': fields.String(),
})


@api.route('/all')
class GetAllEditions(Resource):
    @api.marshal_list_with(editionModel)
    def get(self):
        editions = Edition.collection.fetch()
        return list(editions)


@api.param('id', 'ID of the Edition')
@api.route('/<string:id>')
class GetEditionById(Resource):
    @api.response(404, 'No edition found related to this id')
    @api.marshal_with(editionModel)
    def get(self, id):
        edition = Edition.collection.get(key=generateKeyFromId(Edition, id))
        if edition:
            return edition
        api.abort(404, "No edition found related to this id")
