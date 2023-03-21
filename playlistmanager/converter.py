from werkzeug.routing import BaseConverter
from werkzeug.exceptions import NotFound
from playlistmanager.models import *

class UserConverter(BaseConverter):
    """
    Converter for user resource
    """
    def to_python(self, value):
        user = User.query.filter_by(user_name=value).first()
        if user is None:
            raise NotFound
        return user

    def to_url(self, user):
        return str(user.user_name)