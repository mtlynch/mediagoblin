.. MediaGoblin Documentation

   Written in 2020 by MediaGoblin contributors

   To the extent possible under law, the author(s) have dedicated all
   copyright and related and neighboring rights to this software to
   the public domain worldwide. This software is distributed without
   any warranty.

   You should have received a copy of the CC0 Public Domain
   Dedication along with this software. If not, see
   <http://creativecommons.org/publicdomain/zero/1.0/>.

======================
 Upgrading MediaGoblin
======================

Updating to a new release of MediaGoblin
----------------------------------------

Preparation
~~~~~~~~~~~

*ALWAYS* do backups before upgrading, especially before running migrations! That
way if something goes wrong, we can fix things!

And be sure to shut down your current MediaGoblin/Celery processes before
upgrading!


Upgrade (already on Python 3)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Update to the latest release.  In your ``mediagoblin`` directory, run:
   ``git fetch && git checkout -q v0.10.0 && git submodule update``
2. Remove your existing installation:
   ``rm -rf bin include lib lib64 node_modules``
3. Install MediaGoblin:
   ``./bootstrap.sh && ./configure && make``
4. Update the database:
   ``./bin/gmg dbupdate``
5. Restart MediaGoblin


Upgrade (upgrading to Python 3)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Refer to the "Dependences" and "Configure PostgreSQL" sections of
   ":doc:`deploying`" to install the necessary Python 3 dependencies.
2. Update to the latest release.  In your ``mediagoblin`` directory, run:
   ``git fetch && git checkout -q stable && git submodule update``
3. Remove your existing installation:
   ``rm -rf bin include lib lib64 node_modules``
4. Install MediaGoblin:
   ``./bootstrap.sh && ./configure && make``
5. Update the database:
   ``./bin/gmg dbupdate``
6. Restart MediaGoblin


Upgrade (remaining on Python 2 - not recommended)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Update to the latest release.  In your ``mediagoblin`` directory, run:
   ``git fetch && git checkout -q stable && git submodule update``
2. Remove your existing installation:
   ``rm -rf bin include lib lib64 node_modules``
3. Install MediaGoblin:
   ``./bootstrap.sh && ./configure --without-python3 && make``
4. Update the database:
   ``./bin/gmg dbupdate``
5. Restart MediaGoblin


Updating your system Python
---------------------------

Upgrading your operating system or installing a new version of
Python may break MediaGoblin. This typically occurs because Python virtual
environment is referring to a copy of Python that no longer exists. To fix this:

1. In your ``mediagoblin`` directory, remove your existing installation:
   ``rm -rf bin include lib lib64 node_modules``
2. Install MediaGoblin:
   ``./bootstrap.sh && ./configure && make``
3. Update the database:
   ``./bin/gmg dbupdate``
4. Restart MediaGoblin
