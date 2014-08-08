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

from mediagoblin.db.migration_tools import RegisterMigration, inspect_table

from sqlalchemy import MetaData, Column, Unicode

import json

MIGRATIONS = {}


@RegisterMigration(1, MIGRATIONS)
def add_orig_metadata_column(db_conn):
    metadata = MetaData(bind=db_conn.bind)

    vid_data = inspect_table(metadata, "video__mediadata")

    col = Column('orig_metadata', Unicode,
                 default=None, nullable=True)
    col.create(vid_data)
    db_conn.commit()


@RegisterMigration(2, MIGRATIONS)
def webm_640_to_webm_video(db):
    metadata = MetaData(bind=db.bind)

    file_keynames = inspect_table(metadata, 'core__file_keynames')

    for row in db.execute(file_keynames.select()):
        if row.name == 'webm_640':
            db.execute(
                file_keynames.update(). \
                where(file_keynames.c.id==row.id).\
                values(name='webm_video'))

    db.commit()


@RegisterMigration(3, MIGRATIONS)
def change_metadata_format(db):
    """Change orig_metadata format for multi-stream a-v"""
    db_metadata = MetaData(bind=db.bind)

    vid_data = inspect_table(db_metadata, "video__mediadata")

    for row in db.execute(vid_data.select()):
        metadata = json.loads(row.orig_metadata)

        if not metadata:
            continue

        # before this migration there was info about only one video or audio
        # stream. So, we store existing info as the first item in the list
        new_metadata = {'audio': [], 'video': [], 'common': {}}
        video_key_map = {  # old: new
                'videoheight': 'height',
                'videowidth': 'width',
                'videorate': 'rate',
                }
        audio_key_map = {  # old: new
                'audiochannels': 'channels',
                }
        common_key_map = {
                'videolength': 'length',
                }

        new_metadata['video'] = [dict((v, metadata.get(k))
                for k, v in video_key_map.items() if metadata.get(k))]
        new_metadata['audio'] = [dict((v, metadata.get(k))
                for k, v in audio_key_map.items() if metadata.get(k))]
        new_metadata['common'] = dict((v, metadata.get(k))
                for k, v in common_key_map.items() if metadata.get(k))
        
        # 'mimetype' should be in tags
        new_metadata['common']['tags'] = {'mimetype': metadata.get('mimetype')}
        if 'tags' in metadata:
            new_metadata['video'][0]['tags'] = {}
            new_metadata['audio'][0]['tags'] = {}

            tags = metadata['tags']

            video_keys = ['encoder', 'encoder-version', 'video-codec']
            audio_keys = ['audio-codec']

            for t, v in tags.items():
                if t in video_keys:
                    new_metadata['video'][0]['tags'][t] = tags[t]
                elif t in audio_keys:
                    new_metadata['audio'][0]['tags'][t] = tags[t]
                else:
                    new_metadata['common']['tags'][t] = tags[t]
        db.execute(vid_data.update()
                .where(vid_data.c.media_entry==row.media_entry)
                .values(orig_metadata=json.dumps(new_metadata)))
    db.commit()
