.. MediaGoblin Documentation

   Written in 2011, 2012 by MediaGoblin contributors

   To the extent possible under law, the author(s) have dedicated all
   copyright and related and neighboring rights to this software to
   the public domain worldwide. This software is distributed without
   any warranty.

   You should have received a copy of the CC0 Public Domain
   Dedication along with this software. If not, see
   <http://creativecommons.org/publicdomain/zero/1.0/>.

==========
Migrations
==========

So, about migrations.  Every time we change the way the database
structure works, we need to add a migration so that people running
older codebases can have their databases updated to the new structure
when they run `./bin/gmg dbupdate`.

The first time `./bin/gmg dbupdate` is run by a user, it creates the
tables at the current state that they're defined in models.py and sets
the migration number to the current migration... after all, migrations
only exist to get things to the current state of the db.  After that,
every migration is run with dbupdate.

There's a few things you need to know:

- We use `Alembic <https://bitbucket.org/zzzeek/alembic>`_ to run
  migrations.  We also make heavy use of the
  `branching model <http://alembic.readthedocs.org/en/latest/branches.html>`_
  for our plugins.  Every plugin gets its own migration branc.
- We used to use `sqlalchemy-migrate
  <http://code.google.com/p/sqlalchemy-migrate/>`_.
  See `their docs <https://sqlalchemy-migrate.readthedocs.org/>`_.
  sqlalchemy-migrate is now only kept around for legacy migrations;
  don't add any more!  But some users are still using older databases,
  and we need to provide the intermediary "old" migrations for a while.
- SQLAlchemy has two parts to it, the ORM and the "core" interface.
  We DO NOT use the ORM when running migrations.  Think about it: the
  ORM is set up with an expectation that the models already reflect a
  certain pattern.  But if a person is moving from their old patern
  and are running tools to *get to* the current pattern, of course
  their current database structure doesn't match the state of the ORM!
  Anyway, Alembic has its own conventions for migrations; follow those.
- Alembic's documentation is pretty good; you don't need to worry about
  setting up the migration environment or the config file so you can
  skip those parts.  You can start at the
  `Create a Migration Script <http://alembic.readthedocs.org/en/latest/tutorial.html#create-a-migration-script>`_
  section.
- *Users* should only use `./bin/gmg dbupdate`.  However, *developers*
  may wish to use the `./bin/gmg alembic` subcommand, which wraps
  alembic's own command line interface.  Alembic has some tools for
  `autogenerating migrations <http://alembic.readthedocs.org/en/latest/autogenerate.html>`_,
  and they aren't perfect, but they are helpful.  (You can pass in
  `./bin/gmg alembic --with-plugins revision --autogenerate` if you need
  to include plugins in the generated output; see the
  :ref:`plugin database chapter <plugin-database-chapter>` for more info.)

That's it for now!  Good luck!
