# GNU MediaGoblin -- federated, autonomous media hosting
# Copyright (C) 2011, 2012 MediaGoblin contributors.  See AUTHORS.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import six

from mediagoblin import messages
import mediagoblin.mg_globals as mg_globals

import logging

_log = logging.getLogger(__name__)

from mediagoblin.db.models import Collection
from mediagoblin.tools.federation import create_activity
from mediagoblin.tools.translate import pass_to_ugettext as _
from mediagoblin.tools.response import render_to_response, redirect
from mediagoblin.decorators import require_active_login, user_has_privilege
from mediagoblin.submit import forms as submit_forms
from mediagoblin.media_types import FileTypeNotSupported
from mediagoblin.submit.lib import \
    check_file_field, submit_media, get_upload_file_limits, \
    FileUploadLimit, UserUploadLimit, UserPastUploadLimit
from mediagoblin.user_pages.lib import add_media_to_collection


@require_active_login
@user_has_privilege(u'uploader')
def submit_start(request):
    """
    First view for submitting a file.
    """
    upload_limit, max_file_size = get_upload_file_limits(request.user)

    submit_form = submit_forms.get_submit_start_form(
        request.form,
        license=request.user.license_preference,
        max_file_size=max_file_size,
        upload_limit=upload_limit,
        uploaded=request.user.uploaded)
    users_collections = Collection.query.filter_by(
        actor=request.user.id,
        type=Collection.USER_DEFINED_TYPE
    ).order_by(Collection.title)

    # Only show the Collections dropdown if the user has some
    # collections set up
    if users_collections.count() > 0:
        submit_form.collection.query = users_collections
    else:
        del submit_form.collection

    if request.method == 'POST' and submit_form.validate():
        if not check_file_field(request, 'file'):
            submit_form.file.errors.append(
                _(u'You must provide a file.'))
        else:
            try:
                media = submit_media(
                    mg_app=request.app, user=request.user,
                    submitted_file=request.files['file'],
                    filename=request.files['file'].filename,
                    title=six.text_type(submit_form.title.data),
                    description=six.text_type(submit_form.description.data),
                    license=six.text_type(submit_form.license.data) or None,
                    tags_string=submit_form.tags.data,
                    urlgen=request.urlgen)

                if submit_form.collection and submit_form.collection.data:
                    add_media_to_collection(
                        submit_form.collection.data, media)
                    create_activity(
                        "add", media, request.user,
                        target=submit_form.collection.data)

                messages.add_message(
                    request,
                    messages.SUCCESS,
                    _('Woohoo! Submitted!'))

                return redirect(request, "mediagoblin.user_pages.user_home",
                            user=request.user.username)


            # Handle upload limit issues
            except FileUploadLimit:
                submit_form.file.errors.append(
                    _(u'Sorry, the file size is too big.'))
            except UserUploadLimit:
                submit_form.file.errors.append(
                    _('Sorry, uploading this file will put you over your'
                      ' upload limit.'))
            except UserPastUploadLimit:
                messages.add_message(
                    request,
                    messages.WARNING,
                    _('Sorry, you have reached your upload limit.'))
                return redirect(request, "mediagoblin.user_pages.user_home",
                                user=request.user.username)
            except FileTypeNotSupported as e:
                submit_form.file.errors.append(e)
            except Exception as e:
                raise

    return render_to_response(
        request,
        'mediagoblin/submit/start.html',
        {'submit_form': submit_form,
         'app_config': mg_globals.app_config})


@require_active_login
def add_collection(request, media=None):
    """
    View to create a new collection
    """
    submit_form = submit_forms.AddCollectionForm(request.form)

    if request.method == 'POST' and submit_form.validate():
        collection = request.db.Collection()

        collection.title = six.text_type(submit_form.title.data)
        collection.description = six.text_type(submit_form.description.data)
        collection.actor = request.user.id
        collection.type = request.db.Collection.USER_DEFINED_TYPE
        collection.generate_slug()

        # Make sure this user isn't duplicating an existing collection
        existing_collection = request.db.Collection.query.filter_by(
                actor=request.user.id,
                type=request.db.Collection.USER_DEFINED_TYPE,
                title=collection.title).first()

        if existing_collection:
            messages.add_message(
                request,
                messages.ERROR,
                _('You already have a collection called "%s"!') %
                    collection.title)
        else:
            collection.save()

            messages.add_message(
                request,
                messages.SUCCESS,
                _('Collection "%s" added!') % collection.title)

        return redirect(request, "mediagoblin.user_pages.user_home",
                        user=request.user.username)

    return render_to_response(
        request,
        'mediagoblin/submit/collection.html',
        {'submit_form': submit_form,
         'app_config': mg_globals.app_config})
