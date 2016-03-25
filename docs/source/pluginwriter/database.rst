.. MediaGoblin Documentation

   Written in 2013 by MediaGoblin contributors

   To the extent possible under law, the author(s) have dedicated all
   copyright and related and neighboring rights to this software to
   the public domain worldwide. This software is distributed without
   any warranty.

   You should have received a copy of the CC0 Public Domain
   Dedication along with this software. If not, see
   <http://creativecommons.org/publicdomain/zero/1.0/>.


.. _plugin-database-chapter:


===========================
Database models for plugins
===========================


Accessing Existing Data
=======================

If your plugin wants to access existing data, this is quite
straight forward. Just import the appropiate models and use
the full power of SQLAlchemy. Take a look at the (upcoming)
database section in the Developer's Chapter.


Creating new Tables
===================

If your plugin needs some new space to store data, you
should create a new table.  Please do not modify core
tables.  Not doing so might seem inefficient and possibly
is.  It will help keep things sane and easier to upgrade
versions later.

So if you create a new plugin and need new tables, create a
file named ``models.py`` in your plugin directory. You
might take a look at the core's db.models for some ideas.
Here's a simple one:

.. code-block:: python

    from mediagoblin.db.base import Base
    from sqlalchemy import Column, Integer, Unicode, ForeignKey

    class MediaSecurity(Base):
        __tablename__ = "yourplugin__media_security"

        # The primary key *and* reference to the main media_entry
        media_entry = Column(Integer, ForeignKey('core__media_entries.id'),
            primary_key=True)
        get_media_entry = relationship("MediaEntry",
            backref=backref("security_rating", cascade="all, delete-orphan"))

        rating = Column(Unicode)

    MODELS = [MediaSecurity]

Next, you need to make an initial migration.  MediaGoblin uses
`Alembic's branching model <http://alembic.readthedocs.org/en/latest/branches.html>`_
to handle plugins adding their own content.  As such, when you are
adding a new plugin, you need to add an initial migration adding
the existing models, and migrate from there.

You'll need to make a `migrations` subdirectory for migrations and put
your migrations there.  If you want to look at some example
migrations, look at `mediagoblin/media_types/image/migrations/`,
especially the "initial" migration.  (Plugin authors with plugins that
existed prior to the alembic switchover: you might notice how it
checks for the table and skips the migration if it already exists.
Plugin authors writing brand new plugins, post-Alembic migration
switchover, do not need to do this.)

Unfortunately, these migrations are a bit tedious to write.
Fortunately, Alembic can do much of the work for us!  After adding the
models.py file, run this command (switching out YOUR_PLUGIN_NAME of
course)::

  ./bin/gmg alembic --with-plugins revision \
       --splice --autogenerate \
       --branch-label YOUR_PLUGIN_NAME_plugin \
       -m "YOUR_PLUGIN_NAME plugin initial migration"

(Note that `--with-plugins` *must* come before any alembic subcommand...
this is a quirk related to the way we handle alembic command dispatching
with the gmg subcommand!)

This will dump your migration into "the wrong place" (it'll dump it
into the MediaGoblin core migrations directory), so you should move it
to your plugin's migrations directory.  Open the file and make adjustments
accordingly!

Some notes:

* Make sure all your ``__tablename__`` start with your
  plugin's name so the tables of various plugins can't
  conflict in the database. (Conflicts in python naming are
  much easier to fix later).
* Try to get your database design as good as possible in
  the first attempt.  Changing the database design later,
  when people already have data using the old design, is
  possible (see next chapter), but it's not easy.


Changing the Database Schema Later
==================================

If your plugin is in use and instances use it to store some data,
changing the database design is tricky and must be done with care,
but is not impossible.

Luckily, Alembic can once again help with autogenerating what is
probably very close to the migration you want.  First you will need to
find out what the revision id of your plugin's most recent migrations
is.  There are two ways to do this: look in your plugin's migrations/
directory and figure it out with the hope that it's "obvious" in some
way.  The second path: let Alembic give that info for you.

Assuming you've already done the latest dbupdate with your plugin
enabled, do the following:

  ./bin/gmg alembic --with-plugins heads

You should see the latest migration id for your plugin's label.

Make changes to your
plugin's models.py and then run::

  ./bin/gmg alembic --with-plugins revision \
       --head REVISION_HERE \
       --autogenerate \
       -m "YOUR_PLUGIN_NAME: Change explaination here."

Once again, this will dump the migration into the wrong place, so move
to your plugin's migrations directory.  Open the file, adjust
accordingly, and read carefully!  Now you should also test your
migration with some real data.  Be sure to test it both on sqlite
*AND* on postgresql!

One last *very critical* note: you must never, never modify core
tables with your plugin.  To do that is to put you and all your users
in a dangerous situation.  Add data to the database by adding new tables
under the control of your plugin, but never ever modify anyone else's!

Whew, you made it!  Get yourself a cookie to celebrate!
