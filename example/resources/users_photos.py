import mimetypes

import royal

from voluptuous import Schema, Required, Coerce, All, Range

from example.model import Photo
from example.resources import photos


class Collection(royal.Collection):

    index_schema = Schema({
        Required('offset', default=0): All(Coerce(int), Range(min=0)),
        Required('limit', default=20): All(Coerce(int), Range(min=1, max=50)),
    })

    @property
    def user(self):
        return self.find_item('users')

    def index(self, query_params):
        offset = query_params['offset']
        limit = query_params['limit']
        cursor = Photo.get_newests(self.root.db, offset, limit,
                                   author=self.user.name)
        documents = [
            photos.Item(str(doc._id), self.root, self.request, doc).show()
            for doc in cursor]
        result = {
            'photos': documents,
            'href': self.url(offset=offset, limit=limit),
            'first': self.url(offset=0, limit=limit),
        }
        has_previous = offset > 0
        if has_previous:
            result['previous'] = self.url(offset=max(offset - limit, 0),
                                          limit=limit)
        has_next = len(documents) == limit
        if has_next:
            result['next'] = self.url(offset=offset + limit, limit=limit)
        return result

    def create(self, params):
        fs = params['image']
        author = self.user.name
        mime_type = mimetypes.guess_extension(fs.filename)
        doc = Photo.create(self.root.db, author, fs.file, mime_type)
        return photos.Item(str(doc._id), self.root['photos'], self.request,
                           doc)
