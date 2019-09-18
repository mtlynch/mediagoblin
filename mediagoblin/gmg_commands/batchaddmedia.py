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

from __future__ import print_function, unicode_literals

import csv
import os
import shutil
import tempfile

import requests
import six
from six.moves.urllib.parse import urlparse

from mediagoblin.db.models import LocalUser, MediaEntry
from mediagoblin.gmg_commands import util as commands_util
from mediagoblin.submit.lib import (
    submit_media, FileUploadLimit, UserUploadLimit, UserPastUploadLimit)
from mediagoblin.tools.metadata import compact_and_validate
from mediagoblin.tools.translate import pass_to_ugettext as _
from jsonschema.exceptions import ValidationError


def parser_setup(subparser):
    subparser.description = """\
This command allows the administrator to upload many media files at once."""
    subparser.epilog = _("""For more information about how to properly run this
script (and how to format the metadata csv file), read the MediaGoblin
documentation page on command line uploading
<http://docs.mediagoblin.org/siteadmin/commandline-upload.html>""")
    subparser.add_argument(
        'username',
        help=_("Name of user these media entries belong to"))
    subparser.add_argument(
        'metadata_path',
        help=_(
"""Path to the csv file containing metadata information."""))
    subparser.add_argument(
        '--celery',
        action='store_true',
        help=_("Don't process eagerly, pass off to celery"))


def batchaddmedia(args):
    # Run eagerly unless explicetly set not to
    if not args.celery:
        os.environ['CELERY_ALWAYS_EAGER'] = 'true'

    app = commands_util.setup_app(args)

    files_uploaded, files_attempted = 0, 0

    # get the user
    user = app.db.LocalUser.query.filter(
        LocalUser.username==args.username.lower()
    ).first()
    if user is None:
        print(_("Sorry, no user by username '{username}' exists".format(
                    username=args.username)))
        return

    if os.path.isfile(args.metadata_path):
        metadata_path = args.metadata_path

    else:
        error = _('File at {path} not found, use -h flag for help'.format(
                    path=args.metadata_path))
        print(error)
        return

    abs_metadata_filename = os.path.abspath(metadata_path)
    abs_metadata_dir = os.path.dirname(abs_metadata_filename)

    all_metadata = open(abs_metadata_filename, 'r')
    media_metadata = csv.DictReader(all_metadata)
    for index, file_metadata in enumerate(media_metadata):
        if six.PY2:
            file_metadata = {k.decode('utf-8'): v.decode('utf-8') for k, v in file_metadata.items()}

        files_attempted += 1
        # In case the metadata was not uploaded initialize an empty dictionary.
        json_ld_metadata = compact_and_validate({})

        # Get all metadata entries starting with 'media' as variables and then
        # delete them because those are for internal use only.
        original_location = file_metadata['location']

        ### Pull the important media information for mediagoblin from the
        ### metadata, if it is provided.
        slug = file_metadata.get('slug')
        title = file_metadata.get('title') or file_metadata.get('dc:title')
        description = (file_metadata.get('description') or
            file_metadata.get('dc:description'))
        collection_slug = file_metadata.get('collection-slug')

        license = file_metadata.get('license')
        try:
            json_ld_metadata = compact_and_validate(file_metadata)
        except ValidationError as exc:
            media_id = file_metadata.get('id') or index
            error = _("""Error with media '{media_id}' value '{error_path}': {error_msg}
Metadata was not uploaded.""".format(
                media_id=media_id,
                error_path=exc.path[0],
                error_msg=exc.message))
            print(error)
            continue

        if slug and MediaEntry.query.filter_by(actor=user.id, slug=slug).count():
            # Avoid re-importing media from a previous batch run. Note that this
            # check isn't quite robust enough, since it requires that a slug is
            # specified. Probably needs to be based on "location" since this is
            # the only required field.
            error = '{}: {}'.format(
                slug, _('An entry with that slug already exists for this user.'))
            print(error)
            continue

        url = urlparse(original_location)
        filename = url.path.split()[-1]

        if url.scheme.startswith('http'):
            res = requests.get(url.geturl(), stream=True)
            if res.headers.get('content-encoding'):
                # The requests library's "raw" method does not deal with content
                # encoding. Alternative could be to use iter_content(), and
                # write chunks to the temporary file.
                raise NotImplementedError('URL-based media with content-encoding (eg. gzip) are not currently supported.')

            # To avoid loading the media into memory all at once, we write it to
            # a file before importing. This currently requires free space up to
            # twice the size of the media file. Memory use can be tested by
            # running something like `ulimit -Sv 200000` before running
            # `batchaddmedia` to upload a file larger than 200MB.
            media_file = tempfile.TemporaryFile()
            shutil.copyfileobj(res.raw, media_file)
            if six.PY2:
                media_file.seek(0)

        elif url.scheme == '':
            path = url.path
            if os.path.isabs(path):
                file_abs_path = os.path.abspath(path)
            else:
                file_path = os.path.join(abs_metadata_dir, path)
                file_abs_path = os.path.abspath(file_path)
            try:
                media_file = open(file_abs_path, 'rb')
            except IOError:
                print(_("""\
FAIL: Local file {filename} could not be accessed.
{filename} will not be uploaded.""".format(filename=filename)))
                continue
        try:
            entry = submit_media(
                mg_app=app,
                user=user,
                submitted_file=media_file,
                filename=filename,
                title=title,
                description=description,
                collection_slug=collection_slug,
                license=license,
                metadata=json_ld_metadata,
                tags_string="")
            if slug:
                # Slug is automatically set by submit_media, so overwrite it
                # with the desired slug.
                entry.slug = slug
                entry.save()
            print(_("""Successfully submitted {filename}!
Be sure to look at the Media Processing Panel on your website to be sure it
uploaded successfully.""".format(filename=filename)))
            files_uploaded += 1
        except FileUploadLimit:
            print(_(
"FAIL: This file is larger than the upload limits for this site."))
        except UserUploadLimit:
            print(_(
"FAIL: This file will put this user past their upload limits."))
        except UserPastUploadLimit:
            print(_("FAIL: This user is already past their upload limits."))
        finally:
            media_file.close()
    print(_(
"{files_uploaded} out of {files_attempted} files successfully submitted".format(
        files_uploaded=files_uploaded,
        files_attempted=files_attempted)))
