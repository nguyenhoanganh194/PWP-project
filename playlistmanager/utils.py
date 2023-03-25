import json
from flask import Response, request, url_for
from playlistmanager.constants import *
from playlistmanager.models import *
from werkzeug.routing import BaseConverter
from werkzeug.exceptions import NotFound

def create_error_response(status_code, title, message=None):
    resource_url = request.path
    body = MasonBuilder(resource_url=resource_url)
    body.add_error(title, message)
    body.add_control("profile", href=ERROR_PROFILE)
    return Response(json.dumps(body), status_code, mimetype=MASON)


class MasonBuilder(dict):
    """
    A convenience class for managing dictionaries that represent Mason
    objects. It provides nice shorthands for inserting some of the more
    elements into the object but mostly is just a parent for the much more
    useful subclass defined next. This class is generic in the sense that it
    does not contain any application specific implementation details.
    """

    def add_error(self, title, details):
        """
        Adds an error element to the object. Should only be used for the root
        object, and only in error scenarios.
        Note: Mason allows more than one string in the @messages property (it's
        in fact an array). However we are being lazy and supporting just one
        message.
        : param str title: Short title for the error
        : param str details: Longer human-readable description
        """

        self["@error"] = {
            "@message": title,
            "@messages": [details],
        }

    def add_namespace(self, ns, uri):
        """
        Adds a namespace element to the object. A namespace defines where our
        link relations are coming from. The URI can be an address where
        developers can find information about our link relations.
        : param str ns: the namespace prefix
        : param str uri: the identifier URI of the namespace
        """

        if "@namespaces" not in self:
            self["@namespaces"] = {}

        self["@namespaces"][ns] = {
            "name": uri
        }

    def add_control(self, ctrl_name, href, **kwargs):
        """
        Adds a control property to an object. Also adds the @controls property
        if it doesn't exist on the object yet. Technically only certain
        properties are allowed for kwargs but again we're being lazy and don't
        perform any checking.
        The allowed properties can be found from here
        https://github.com/JornWildt/Mason/blob/master/Documentation/Mason-draft-2.md
        : param str ctrl_name: name of the control (including namespace if any)
        : param str href: target URI for the control
        """

        if "@controls" not in self:
            self["@controls"] = {}

        self["@controls"][ctrl_name] = kwargs
        self["@controls"][ctrl_name]["href"] = href


class RespondBodyBuilder(MasonBuilder):
    """
    A subclass to build application specific Mason objects.
    """
#region User
    def add_control_users_all(self):
        """
        Adds users-all control, which leads to the users collection.
        """

        self.add_control(
            NAMESPACE_SHORT + ":users-all",
            href=url_for("api.usercollection"),
            method="GET",
            title="List all users"
        )
    def add_control_add_user(self):
        """
        Adds add-user control, which is used to add a user into the users collection.
        """

        self.add_control(
            NAMESPACE_SHORT + ":add-user",
            href=url_for("api.usercollection"),
            method="POST",
            encoding="json",
            title="Add a new player",
            schema=User.get_schema()
        )

    def add_control_edit_user(self, user):
        """
        Adds edit control, which is used to edit user item.
        : param str user: user's user_name
        """

        self.add_control(
            NAMESPACE_SHORT + ":edit-user",
            url_for("api.useritem", user=user),
            method="PUT",
            encoding="json",
            title="Edit this user",
            schema=User.get_schema()
        )
   
#endregion
    
#region Track
    def add_control_user_tracks_of(self , user):
        """
        TODO: fill description for this
        """

        self.add_control(
            NAMESPACE_SHORT + ":tracks-of",
            href=url_for("api.trackcollection", user = user),
            method="GET",
            title="List track of users"
        )
    def add_control_add_track(self, user):
        """
        TODO: fill description for this
        """

        self.add_control(
            NAMESPACE_SHORT + ":add-track",
            href=url_for("api.trackcollection", user = user),
            method="POST",
            encoding="json",
            title="Add a new track",
            schema=Track.get_schema()
        )

    def add_control_edit_track(self, user, track):
        """
           TODO: fill description for this
        """

        self.add_control(
            NAMESPACE_SHORT + ":edit-track",
            url_for("api.trackitem", user=user, track = track),
            method="PUT",
            encoding="json",
            title="Edit this track",
            schema=Track.get_schema()
        )
#endregion
    def add_control_delete(self, href):
        """
        A generic delete function which should work for all resource types.
        : param str href: Resource's URI
        """

        self.add_control(
            NAMESPACE_SHORT + "delete",
            href=href,
            method="DELETE",
            title="Delete this resource"
        )



