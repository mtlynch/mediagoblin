# GNU MediaGoblin -- federated, autonomous media hosting
# Copyright (C) 2016 MediaGoblin contributors.  See AUTHORS.
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

from datetime import datetime

from itsdangerous import BadSignature
from werkzeug.exceptions import Forbidden
from werkzeug.utils import secure_filename

from mediagoblin import messages
from mediagoblin import mg_globals

from mediagoblin.plugins.subtitles import forms
from mediagoblin.decorators import (require_active_login, active_user_from_url,
                            get_media_entry_by_id, user_may_delete_media)
from mediagoblin.tools.metadata import (compact_and_validate, DEFAULT_CHECKER,
                                        DEFAULT_SCHEMA)
from mediagoblin.tools.response import (render_to_response,
                                        redirect, redirect_obj, render_404)

import mimetypes

from mediagoblin.plugins.subtitles.tools import open_subtitle,save_subtitle

UNSAFE_MIMETYPES = [
        'text/html',
        'text/svg+xml']

@get_media_entry_by_id
@user_may_delete_media
@require_active_login
def edit_subtitles(request, media):
    # This was originally quite a long list of allowed extensions, but as far as
    # I understand, Video.js only supports WebVTT format subtitles:
    # https://docs.videojs.com/docs/guides/text-tracks.html
    allowed_extensions = ['vtt']
    form = forms.EditSubtitlesForm(request.form)

    # Add any subtitles
    if 'subtitle_file' in request.files \
        and request.files['subtitle_file']:
        if mimetypes.guess_type(
                request.files['subtitle_file'].filename)[0] in \
                UNSAFE_MIMETYPES:
            public_filename = secure_filename('{0}.notsafe'.format(
                request.files['subtitle_file'].filename))
        else:
            public_filename = secure_filename(
                    request.files['subtitle_file'].filename)
        filepath = request.files['subtitle_file'].filename
        if filepath.split('.')[-1] not in allowed_extensions :
            messages.add_message(
            request,
            messages.ERROR,
            ("Invalid subtitle file"))

            return redirect(request,
                            location=media.url_for_self(request.urlgen))
        subtitle_public_filepath = mg_globals.public_store.get_unique_filepath(
            ['media_entries', six.text_type(media.id), 'subtitle',
             public_filename])

        with mg_globals.public_store.get_file(
            subtitle_public_filepath, 'wb') as subtitle_public_file:
            subtitle_public_file.write(
                request.files['subtitle_file'].stream.read())
        request.files['subtitle_file'].stream.close()

        media.subtitle_files.append(dict(
                name=form.subtitle_language.data \
                    or request.files['subtitle_file'].filename,
                filepath=subtitle_public_filepath,
                created=datetime.utcnow(),
                ))

        media.save()

        messages.add_message(
            request,
            messages.SUCCESS,
            ("You added the subtitle %s!") %
                (form.subtitle_language.data or
                 request.files['subtitle_file'].filename))

        return redirect(request,
                        location=media.url_for_self(request.urlgen))
    return render_to_response(
        request,
        'mediagoblin/plugins/subtitles/subtitles.html',
        {'media': media,
         'form': form})


@require_active_login
@get_media_entry_by_id
@user_may_delete_media
def custom_subtitles(request,media,id=None):
    id = request.matchdict['id']
    path = ""
    for subtitle in media.subtitle_files:
        if subtitle["id"] == id:
            path = subtitle["filepath"]
    text = ""
    value = open_subtitle(path)
    text, status = value[0], value[1]
    if status == True :
        form = forms.CustomizeSubtitlesForm(request.form,
                                             subtitle=text)
        if request.method == 'POST' and form.validate():
            subtitle_data = form.subtitle.data
            status = save_subtitle(path,subtitle_data)
            if status == True:
                messages.add_message(
                    request,
                    messages.SUCCESS,
                    ("Subtitle file changed!!!"))
                return redirect(request,
                                    location=media.url_for_self(request.urlgen))
            else :
                messages.add_message(
                    request,
                    messages.ERROR,
                    ("Couldn't edit the subtitles!!!"))
                return redirect(request,
                                    location=media.url_for_self(request.urlgen))

        return render_to_response(
            request,
            "mediagoblin/plugins/subtitles/custom_subtitles.html",
            {"id": id,
             "media": media,
             "form": form })
    else:
        index = 0
        for subtitle in media.subtitle_files:
            if subtitle["id"] == id:
                delete_container = index
                media.subtitle_files.pop(delete_container)
                media.save()
                break
            index += 1
        messages.add_message(
            request,
            messages.ERROR,
            ("File link broken! Upload the subtitle again"))
        return redirect(request,
                            location=media.url_for_self(request.urlgen))


@require_active_login
@get_media_entry_by_id
@user_may_delete_media
def delete_subtitles(request,media):
    id = request.matchdict['id']
    delete_container = None
    index = 0
    for subtitle in media.subtitle_files:
        if subtitle["id"] == id:
            path = subtitle["filepath"]
            mg_globals.public_store.delete_file(path)
            delete_container = index
            media.subtitle_files.pop(delete_container)
            media.save()
            break
        index += 1

    messages.add_message(
        request,
        messages.SUCCESS,
        ("Subtitle file deleted!!!"))

    return redirect(request,
                        location=media.url_for_self(request.urlgen))
