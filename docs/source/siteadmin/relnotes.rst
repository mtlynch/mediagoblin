.. MediaGoblin Documentation

   Written in 2012 by MediaGoblin contributors

   To the extent possible under law, the author(s) have dedicated all
   copyright and related and neighboring rights to this software to
   the public domain worldwide. This software is distributed without
   any warranty.

   You should have received a copy of the CC0 Public Domain
   Dedication along with this software. If not, see
   <http://creativecommons.org/publicdomain/zero/1.0/>.

.. _release-notes:

=============
Release Notes
=============

This chapter has important information for releases in it.
If you're upgrading from a previous release, please read it
carefully, or at least skim over it.

.. note::

   ALWAYS do backups before upgrading, especially before
   running migrations!  That way if something goes wrong, we can fix
   things!

   And be sure to shut down your current MediaGoblin/Celery processes
   before upgrading!


0.10.0
======

This release includes video subtitles and multiple video qualities and a swathe
of smaller improvements and bug-fixes listed below.

Python 3 is now the default when you install MediaGoblin and is strongly
recommended. Python 2 installation is still supported in this release with
`./configure --without-python3`, but support will likely be removed in the next
release.

FastCGI support has now been deprecated and removed from the documentation as
our dependency `flup` does not support Python 3.

**Upgrade (already on Python 3):**

0. Update to the latest release.  In your ``mediagoblin`` directory, run:
   ``git fetch && git checkout -q v0.10.0``
1. Upgrade MediaGoblin:
   ``./bootstrap.sh && ./configure && make``
2. Update the database:
   ``./bin/python setup.py develop --upgrade && ./bin/gmg dbupdate``
3. Restart MediaGoblin

**Upgrade (upgrading to Python 3):**

0. Refer to the "Dependences" and "Configure PostgreSQL" sections of
   ":doc:`deploying`" to install the necessary Python 3 dependencies.
1. Update to the latest release.  In your ``mediagoblin`` directory, run:
   ``git fetch && git checkout -q v0.10.0``
2. Remove your existing installation:
   ``rm -rf bin include lib lib64``
3. Upgrade MediaGoblin:
   ``./bootstrap.sh && ./configure && make``
4. Update the database:
   ``./bin/gmg dbupdate``
5. Restart MediaGoblin

**Upgrade (remaining on Python 2 - not recommended):**

0. Update to the latest release.  In your ``mediagoblin`` directory, run:
   ``git fetch && git checkout -q v0.10.0``
1. Update the database:
   ``./bin/python setup.py develop --upgrade && ./bin/gmg dbupdate``
2. Restart MediaGoblin

For detailed instructions on installing MediaGoblin, see ":doc:`deploying`". If
you have any problems, please drop in to the `#mediagoblin IRC chat
<https://webchat.freenode.net/#mediagoblin>`_, report an issue on our `issue
tracker <https://issues.mediagoblin.org/>`_ or drop us an email to
`mediagoblin-devel@gnu.org <mailto:mediagoblin-devel@gnu.org>`_.

**Highlights:**

- New video subtitles plugin (Saksham Agrawal)
- Multiple video qualities (Vijeth Aradhya)
   
**Smaller improvements:**

- Make the user panel default to open and remember preference in local storage (Matt Deal)
- Use OSM tiles in Geolocation plugin (Olivier Mehani)
- Add thumbnail image to Atom feed (Ben Sturmfels)
- Add links in site-admin documentation foreword (Alexandre Franke)
- Add media_titleinfo template hook (Andrew Browning)
- Add video icon to collection thumbnail (Andrew Browning)
- Use AJAX for posting comments (Vijeth Aradhya)
- Show transcoding progress (Vijeth Aradhya)
- Add collection option to 'addmedia' cli uploading (Stéphane Péchard)
- Add creator to filter collections (Stéphane Péchard)
- Add ARIA attributes to audio player (Boris Bobrov)
- Remove tinymce from dependencies (Boris Bobrov)
- Add register_captcha template hook (Andrew Browning)
- Switch to rabbitmq by default and in docs (Boris Bobrov)
- Log IP address for failed login (Andrew Browning)
- Handle collection in batchaddmedia command (Simen Heggestøyl)
- Allow API upload filename to be provided using custom header (Romain Porte)
- Add tags in API (view them and edit them) (Romain Porte)
- Remove use of mediagoblin_local.ini (Boris Bobrov)
- EXIF rotation to make the image portrait on demand (chrysn)
- Add moderation panel thumbnail header [#5563] (Andrew Browning)
- Add Creative Commons 4.0 licenses [#955] (Dpg)
- Add Python 2 & 3 Docker files for MediaGoblin hacking (Ben Sturmfels)
- Add Python 3 docker-compose recipe for MediaGoblin hacking (Ben Sturmfels)
- Add basic duplicate detection/prevention for batchaddmedia (Ben Sturmfels)
- Add datetime_format config option (Olivier Mehani)
- Extend install instructions for raven plugin (Ben Sturmfels)
- Add visual feedback on link hover (Muto)
- Document SSL/TLS SMTP options (Ben Sturmfels)
- Remove flup and fastcgi from documentation  (Michael Lynch)
- Switch to Python 3 by default (Ben Sturmfels)
- Add Python 2 deprecation warning [#5598] (Ben Sturmfels)
- Review and update the deploment docs for Debian 10 and CentOS 8 [#5593] (Ben Sturmfels)

**Bug fixes:**

- Pass test paths to py.test via tox (Boris Bobrov)
- Length check for login form (Jonathan Sandoval)
- Add padding around form field labels (Josh Crompton)
- Fix unhelpful SMTP error (Johnathan Sandoval)
- Fix the blog_delete page for admins (宋文武)
- Fix add_message inconsistencies [#5451] (Andrew Browning)
- Handle no mail server configured (Jonathan Sandoval)
- Fixed 'older' and 'newer' arrows for rtl locales (Leah Velleman)
- Prevent erroring out in some cases of checking video metadata (Christopher Allan Webber)
- Cleanup to avoid duplicated get_upload_file_limits [#928] (Loic Dachary)
- Attempt to change email without login [#5462] (Andrew Browning)
- Fix text wrapping on thumbnail (Matt Deal)
- Modify setup.py version syntax to address #5464 (Andrew Browning)
- Fix Python 3 support in pagination (Ben Sturmfels)
- Fix typo in user processing panel (Andrew Browning)
- Fix text overflow in media headings [#664] (Andrew Browning)
- Removed line breaks around the verifier code (vijeth-aradhya)
- Fix UnicodeEncodeError in atom feed [#5500] (Andrew Browning)
- Commit session after alembic updates have finished (Boris Bobrov)
- Add cascade to blog mediatype [#5308] (Robert Smith)
- Remove mongodb-related stuff (Boris Bobrov)
- Remove exif from blog posts [#830] (Andrew Browning)
- Can't delete blog post drafts [#5513] (ayleph)
- Fix add to Collection causes server error [#5514] (ayleph)
- Fix zero division error in exif.py [#5524] (Andrew Browning)
- Support Unicode characters in configuration values (Simen Heggestøyl)
- Make admin panel headers readable in Airy theme (Simen Heggestøyl)
- Port batchaddmedia command to Python 3 (Simen Heggestøyl)
- Fix location of host-meta.xml file [#5543] (Andrew Browning)
- Replaced /bin/celeryd by /bin/celery in lazycelery (Romain Porte)
- Prevent video plugin from processing svg [#934] (Andrew Browning)
- Process videos with incorrect date tags [#5409] (Andrew Browning)
- Fix 2 errors in editor views (ĎÚβĨŐÚŚ Dod)
- Fix server crash on blog about page [#5572] (Andrew Browning)
- Fix default gmg help message (Boris Bobrov)
- Remove requirement for the file to be with single dot in name (Boris Bobrov)
- Fix auth error and simplify url and email checks (Boris Bobrov)
- Finally fix url validator (Boris Bobrov)
- Always guess the same filetype (Boris Bobrov)
- Fix bulkupload documentation example (Ben Sturmfels)
- Fix URL-based importing with batchaddmedia command (Ben Sturmfels)
- Update metadata_display plugin for Python 3 (Ben Sturmfels)
- Various Guix-related installation fixes/updates (Ben Sturmfels)
- Even up top/bottom margins around header dropdown button (Ben Sturmfels)
- Prevent warning when importing GstPbutils (Ben Sturmfels)
- Pin werkzeug < 1.0.0, handle moved SharedDataMiddleware in werkzeug >= 0.15.0 (Ben Sturmfels)
- Remove audio spectrograms due to instability and lack of Python 3 support (Ben Sturmfels)
- Decode request.query_string before use (Ben Sturmfels)
- Pin jinja2<3.0.0 due to use of f-strings (Ben Sturmfels)
- Fix "KeyError: 'No such transport: sqlite.  Did you mean sqla?'" in tests (Ben Sturmfels)
- Unmute videos by default (Ben Sturmfels)
- Properly quote --without-python3 in docs (#5596) (Ben Sturmfels)
- Pin all Python 2 dependencies allowing patch version upgrades [#5595] (Ben Sturmfels)

   

0.9.0
=====

This release has a number of improvements, but is also a major
"plumbing upgrade" release to MediaGoblin.  Notably, we now support
Python 3, which is pretty cool!

**Do this to upgrade**

0. If you haven't already, switch the git remote URL:
   ``git remote set-url origin https://git.savannah.gnu.org/git/mediagoblin.git``
1. Update to the latest release.  If checked out from git, run:
   ``git fetch && git checkout -q v0.9.0``
2. Run
   ``./bootstrap.sh && ./configure && make``
3. Also run
   ``./bin/python setup.py develop --upgrade && ./bin/gmg dbupdate``

**Bugfixes/improvements:**

- Python 3 is now a first class citizen!  We now support both
  Python 2.7 and Python 3.4 or later.
- Major updates to internal tooling to pave the way for federation.

  - Massive overhaul to the database layout (particularly in
    permitting generic relations)
  - OAuth updates
  - Updating how we handle collections
  - Add a "graveyard" system with tombstones for keeping information
    about removed objects
  - Large overhaul to how "comments" work.  In federation, many things
    can reply to many things, so we had to loosen the model.

- If your user has some collections available, these will be presented
  as a dropdown option while submitting media.
- Begin using Alembic for migrations
- Lots of bugfixes and etc
  - Many fixes to typos
  - Some fixes to the blog system
  - Switch to waitress for development
  - And more...!


0.8.1
=====

This release is a security and bugfix release.  We recommend you upgrade as
soon as possible.

**Do this to upgrade**

0. If you haven't already, switch the git remote URL:
   ``git remote set-url origin https://git.savannah.gnu.org/git/mediagoblin.git``
1. Update to the latest release.  If checked out from git, run:
   ``git fetch && git checkout -q v0.8.1``
2. Run
   ``./bootstrap.sh && ./configure && make``
3. Also run
   ``./bin/python setup.py develop --upgrade && ./bin/gmg dbupdate``

(Please check intermediate release steps as well if not upgrading from
0.8.0)

**Bugfixes/improvements:**

Most importantly, there is an **important security fix**:

Quoting here a portion of the
`release blogpost <http://mediagoblin.org/news/mediagoblin-0.8.1-security-release.html>`_::

  We have had a security problem in our OAuth implementation reported to
  us privately and have taken steps to address it. The security problem
  affects all versions of GNU MediaGoblin since 0.5.0. I have created a patch
  for this and released a minor version 0.8.1. It's strongly advised
  that everyone upgrade as soon as they can.

  In order to exploit the security issue, an attacker must have had
  access to a logged in session to your GNU MediaGoblin account. If you
  have kept your username and password secret, logging in only over
  HTTPS and you've not left yourself logged in on publicly accessible
  computers, you should be safe.  However it's still advised all users
  take the following precautions, listed below.

  Users should check their authorized clients. Any client which looks
  unfamiliar to you, you should deauthorize. To check this:

  1) Log in to the GNU MediaGoblin instance
  2) Click the drop down arrow in the upper right
  3) Click "Change account settings"
  4) At the bottom click the "Deauthorize applications" link

  If you are unsure of any of these, click "Deauthorize".

There are other bugfixes, but they are fairly minor.


0.8.0
=====

This release has a number of changes related to the way we recommend
building MediaGoblin; upgrade steps are below, but if you run into
trouble, consider pinging the MediaGoblin list or IRC channel.

**Do this to upgrade**

0. If you haven't already, switch the git remote URL:
   ``git remote set-url origin https://git.savannah.gnu.org/git/mediagoblin.git``
1. If you don't have node.js installed, you'll need it for handling
   MediaGoblin's static web dependencies.  Install this via your
   distribution!  (In the glorious future MediaGoblin will be simply
   packaged for your distribution so you won't have to worry about
   this!)
2. Update to the latest release.  If checked out from git, run:
   ``git fetch && git checkout -q v0.8.0``
3. Run
   ``./bootstrap.sh && ./configure && make``
4. Also run
   ``./bin/python setup.py develop --upgrade && ./bin/gmg dbupdate``

Please note the important steps of 0 and 2, which have not appeared in
prior upgrade guides!

Additionally:

- Are you using audio or video media types?  In that case, you'll need
  to update your GStreamer instance to 1.0.
- The Pump API needs some data passed through to the WSGI application,
  so if you are using Apache with mod_wsgi you should be sure to make
  sure to add "WSGIPassAuthorization On" to your config.  (Using the
  default MediaGoblin documentation and config, things should work
  as-is.)


**Bugfixes/improvements:**

- Preliminary / experimental support for Python 3!
- Footer forced to the bottom of page
- Massive improvements to Pump API support

  - Able to run on multiple existing Pump clients!  Including Pumpa
    and Dianara!

- much cleaner ./configure && make support; it's now the default
- Clearer documentation on permissions and installation
- Switched from Transifex, which had become proprietary, to an
  instance of Pootle hosted for GNU
- Moved to GStreamer 1.0!  This also adds a new thumbnailer which
  gives much better results in
- Removed terrible check-JavaScript-dependencies-into-your-application
  setup, now using Bower for dependency tracking
- Put some scaffolding in place for Alembic, which will be used for
  future migration work
- Automatically create a fresh mediagoblin.ini from
  mediagoblin.ini.example
- no more need for mediagoblin_local.ini (though it's still supported)
- Fix lowercasing of username in auth steps
- Slowly moving towards removing global state (a source of many bugs)

0.7.1
=====

This is a purely bugfix release.  Important changes happened since
0.7.0; if running MediaGoblin 0.7.0, an upgrade is highly recommended;
see below.  This release is especially useful if you have been running
PostgreSQL and have been receiving seemingly random database transaction
errors.

**Do this to upgrade**

1. Update to the latest release.  If checked out from git, run:
   ``git fetch && git checkout -q v0.7.1 && git submodule init && git submodule update``
2. Make sure to run
   ``./bin/python setup.py develop --upgrade && ./bin/gmg dbupdate``

That's it, probably!  If you run into problems, don't hesitate to
`contact us <http://mediagoblin.org/pages/join.html>`_
(IRC is often best).

**Bugfixes/improvements:**

- The *MOST IMPORTANT* change in this release:
  Disabling a couple of non-critical features that were causing
  database transaction issues.  (These should be back by 0.8.0.)

  + Disabled the "checking if the database is up to date at
    MediaGoblin startup" feature
  + Disabled the garbage collection stuff by default for now
    (You can set garbage_collection under the config MediaGoblin
    header to something other than 0 to turn it back on for now, but
    it's potentially risky for the moment.)

- Some fixes to the 0.7.0 docs
- Fixed Sandy 70s speedboat navbar by updating git submodule
- Added support for cr2 files in raw_image media type
- Added a description to setup.py
- Collection and CollectionItem objects now have nicer in-python representations
- Fixed Unicode error with raw image mediatype logging
- Fixed #945 "Host metadata does not confirm to spec (/.well-known/meta-data)"

  + Add XRD+XML formatting for /.well-known/host-meta
  + Add /.well-known/webfinger API to lookup user hrefs

- deleteuser gmg subcommand now fails gracefully
- Removed a false download link from setup.py

0.7.0
=====

**Do this to upgrade**

1. Update to the latest release.  If checked out from git, run:
   ``git fetch && git checkout -q v0.7.0 && git submodule init && git submodule update``
2. Make sure to run
   ``./bin/python setup.py develop --upgrade && ./bin/gmg dbupdate``

(NOTE: earlier versions of the 0.7.0 release instructions left out the
``git submodule init`` step!  If you did an upgrade earlier based on
these instructions and your theme looks weirdly aligned, try running
the following:)

  ``git submodule init && git submodule update``

That's it, probably!  If you run into problems, don't hesitate to
`contact us <http://mediagoblin.org/pages/join.html>`_
(IRC is often best).

**New features:**

- New mobile upload API making use of the
  `Pump API <https://github.com/e14n/pump.io/blob/master/API.md>`_
  (which will be the foundation for MediaGoblin's federation)
- New theme: Sandy 70s Speedboat!

- Metadata features!  We also now have a JSON-LD context. 

- Many improvements for archival institutions, including metadata
  support and featuring items on the homepage.  With the (new!)
  archivalook plugin enabled, featuring media is possible.
  Additionally, metadata about the particular media item will show up
  in the sidebar.

  In the future these plugins may be separated, but for now they have
  come together as part of the same plugin.

- There is a new gmg subcommand called batchaddmedia that allows for
  uploading many files at once.  This is aimed to be useful for
  archival institutions and groups where there is an already existing
  and large set of available media that needs to be included.
- Speaking of, the call to PostgreSQL in the makefile is fixed.
- We have a new, generic media-page context hook that allows for
  adding context depending on the type of media.
- Tired of video thumbnails breaking during processing all the time?
  Good news, everyone!  Video thumbnail generation should not fail
  frequently anymore.  (We think...)
- You can now set default permissions for new users in the config.

- bootstrap.sh / gnu configuration stuff still exists, but moves to be
  experimental-bootstrap.sh so as to not confuse newcomers.  There are
  some problems currently with the autoconf stuff that we need to work
  out... we still have interest in supporting it, though help is
  welcome.

- MediaGoblin now checks whether or not the database is up to date
  when starting.
- Switched to `Skeleton <http://www.getskeleton.com/>`_ as a system for
  graphic design.
- New gmg subcommands for administrators:
  - A "deletemedia" command
  - A "deleteuser" command
- We now have a blogging media type... it's very experimental,
  however.  Use with caution!
- We have switched to exifread as an external library for reading EXIF
  data.  It's basically the same thing as before, but packaged
  separately from MediaGoblin.
- Many improvements to internationalization.  Also (still rudimentary,
  but existent!) RTL language support!

**Known issues:**
 - The host-meta is now JSON by default; in the spec it should be XML by
   default.  We have done this because of compatibility with the pump
   API.  We are checking with upstream to see if there is a way to
   resolve this discrepancy.


0.6.1
=====

This is a short, bugfix release.

**Do this to upgrade**

1. Update to the latest release.  If checked out from git, run:
   ``git fetch && git checkout -q v0.6.1``
2. Make sure to run
   ``./bin/python setup.py develop --upgrade && ./bin/gmg dbupdate``

This release switches the default terms of service to be off by
default and corrects some mistakes in the default terms of service.

Turning the terms of service on is very easy, just set ``show_tos`` in
the ``[mediagoblin]`` section of your config to ``true``.


0.6.0
=====

**Do this to upgrade**

1. Update to the latest release.  If checked out from git, run:
   ``git fetch && git checkout -q v0.6.0``
2. Make sure to run
   ``./bin/python setup.py develop --upgrade && ./bin/gmg dbupdate``

That's it, probably!  If you run into problems, don't hesitate to
`contact us <http://mediagoblin.org/pages/join.html>`_
(IRC is often best).

This tool has a lot of new tools for administrators, hence the
nickname "Lore of the Admin"!

**New features:**

- New tools to control how much users can upload, both as a general
  user limit, or per file.

  You can set this with the following options in your MediaGoblin
  config file: `upload_limit` and `max_file_size`.  Both are integers
  in megabytes.

  There is an option to control how much each individual user can
  upload too, though an interface for this is not yet exposed.  See
  the "uploaded" field on the core__users table.

- MediaGoblin now contains an authentication plugin for LDAP!  You
  can turn on the mediagoblin.plugins.ldap plugin to make use of
  this.  See the documentation: :ref:`ldap-plugin`

- There's a new command line upload tool!  At long last!  See
  `./bin/gmg addmedia --help` for info on how to use this.

- There's now a terms of service document included in MediaGoblin.
  It's turned on by default, but you can turn it off if you prefer,
  just set the configuration option of `show_tos` in the [mediagoblin]
  section of your config to false.

  Alternately, you can override the template for the terms of service
  document to set up your own.

- We have a lot of new administrative tooling features!

  - There's a built-in privileges/permissions system now.
    Administrators are given access to modifying these parameters
    from a user administration panel.
  - Users can submit reports about other problematic users or media
    and administrators are given tools to resolve said reports and
    ban/unban users if needed.

- New version of video.js is included with MediaGoblin.  Slight
  amount of skinning to match the MediaGoblin look, otherwise also
  uses the new default skin.

Developer-oriented changes:

- New developer tool for quickly setting up a development environment
  in `devtools/make_example_database.sh`.  Requires doing a checkout
  of our other tool `mg_dev_environments <https://gitorious.org/mediagoblin/mg-dev-environments/>`_
  (probably in the parent Directory) though!
- A "foundations" framework has entered into the codebase.
  This is mostly just relevant to coders, but it does mean that it's
  much easier to add database structures that need some entries filled
  automatically by default.
- Refactoring to the authentication code and the reprocessing code


0.5.1
=====

v0.5.1 is a bugfix release... the steps are the same as for 0.5.1.

**Bugfixes:**

- python 2.6 compatibility restored
- Fixed last release's release notes ;)


0.5.0
=====

**NOTE:** If using the API is important to you, we're in a state of
transition towards a new API via the Pump API.  As such, though the old
API still probably works, some changes have happened to the way OAuth
works to make it more Pump-compatible.  If you're heavily using
clients using the old API, you may wish to hold off on upgrading for
now.  Otherwise, jump in and have fun! :)

**Do this to upgrade**

1. Make sure to run
   ``./bin/python setup.py develop --upgrade && ./bin/gmg dbupdate``
   after upgrading.

.. mention something about new, experimental configure && make support

2. Note that a couple of things have changed with ``mediagoblin.ini``. First
   we have a new Authentication System. You need to add 
   ``[[mediagoblin.plugins.basic_auth]]`` under the ``[plugins]`` section of 
   your config file. Second, media types are now plugins, so you need to add
   each media type under the ``[plugins]`` section of your config file.


3. We have made a script to transition your ``mediagoblin_local.ini`` file for
   you. This script can be found at:
   
   http://mediagoblin.org/download/0.5.0_config_converter.py

If you run into problems, don't hesitate to
`contact us <http://mediagoblin.org/pages/join.html>`_
(IRC is often best).

**New features**

* As mentioned above, we now have a plugable Authentication system. You can
  use any combination of the multiple authentication systems 
  (:ref:`basic_auth-chapter`, :ref:`persona-chapter`, :ref:`openid-chapter`)
  or write your own!
* Media types are now plugins!  This means that new media types will
  be able to do new, fancy things they couldn't in the future.
* We now have notification support! This allows you to subscribe to media
  comments and to be notified when someone comments on your media.
* New reprocessing framework! You can now reprocess failed uploads, and
  send already processed media back to processing to re-transcode or resize
  media.
* Comment preview!
* Users now have the ability to change their email associated with their
  account.
* New OAuth code as we move closer to federation support.
* Experimental pyconfigure support for GNU-style configure and makefile
  deployment.
* Database foundations! You can now pre-populate the database models.
* Way faster unit test run-time via in-memory database.
* All mongokit stuff has been cleaned up.
* Fixes for non-ASCII filenames.
* The option to stay logged in.
* MediaGoblin has been upgraded to use the latest `Celery <http://celeryproject.org/>`_
  version.
* You can now add jinja2 extensions to your config file to use in custom
  templates.
* Fixed video permission issues.
* MediaGoblin docs are now hosted with multiple versions.
* We removed redundant tooltips from the STL media display.
* We are now using itsdangerous for verification tokens.


0.4.1
=====

This is a bugfix release for 0.4.0.  This only implements one major
fix in the newly released document support which prevented the
"conversion via libreoffice" feature.

If you were running 0.4.0 you can upgrade to v0.4.1 via a simple
switch and restarting MediaGoblin/Celery with no other actions.

Otherwise, follow 0.4.0 instructions.


0.4.0
=====

**Do this to upgrade**

1. Make sure to run
   ``./bin/python setup.py develop --upgrade && ./bin/gmg dbupdate``
   after upgrading.
2. See "For Theme authors" if you have a custom theme.
3. Note that ``./bin/gmg theme assetlink`` is now just
   ``./bin/gmg assetlink`` and covers both plugins and assets.
   Keep on reading to hear more about new plugin features.
4. If you want to take advantage of new plugins that have statically
   served assets, you are going to need to add the new "plugin_static"
   section to your Nginx config.  Basically the following for Nginx::

     # Plugin static files (usually symlinked in)
     location /plugin_static/ {
        alias /srv/mediagoblin.example.org/mediagoblin/user_dev/plugin_static/;
     }

   Similarly, if you've got a modified paste config, you may want to
   borrow the app:plugin_static section from the default paste.ini
   file.
5. We now use itsdangerous for sessions; if you had any references to
   beaker in your paste config you can remove them.  Again, see the
   default paste.ini config
6. We also now use git submodules.  Please do:
   ``git submodule init && git submodule update``
   You will need to do this to use the new PDF support.

**For theme authors**

If you have your own theme or you have any "user modified templates",
please note the following:

* mediagoblin/bits/ files above-content.html, body-end.html,
  body-start.html now are renamed... they have underscores instead of
  dashes in the filenames now :)
* There's a new file: ``mediagoblin/bits/frontpage_welcome.html``.
  You can easily customize this to give a welcome page appropriate to
  your site.


**New features**

* PDF media type!
* Improved plugin system.  More flexible, better documented, with a
  new plugin authoring section of the docs.
* itsdangerous based sessions.  No more beaker!
* New, experimental Piwigo-based API.  This means you should be able
  to use MediaGoblin with something like Shotwell.  (Again, a word of
  caution: this is *very experimental*!)
* Human readable timestamps, and the option to display the original
  date of an image when available (available as the
  "original_date_visible" variable)
* Moved unit testing system from nosetests to py.test so we can better
  handle issues with SQLAlchemy exploding with different database
  configurations.  Long story :)
* You can now disable the ability to post comments.
* Tags now can be up to length 255 characters by default.


0.3.3
=====

**Do this to upgrade**

1. Make sure to run ``bin/gmg dbupdate`` after upgrading.
2. OpenStreetMap is now a plugin, so if you want to use it, add the
   following to your config file:

   .. code-block:: ini

    [plugins]
    [[mediagoblin.plugins.geolocation]]

If you have your own theme, you may need to make some adjustments to
it as some theme related things may have changed in this release.  If
you run into problems, don't hesitate to
`contact us <http://mediagoblin.org/pages/join.html>`_
(IRC is often best).

**New features**

* New dropdown menu for accessing various features.

* Significantly improved URL generation.  Now MediaGoblin won't give
  up on making a slug if it looks like there will be a duplicate;
  it'll try extra hard to generate a meaningful one instead.

  Similarly, linking to an id no longer can possibly conflict with
  linking to a slug; /u/username/m/id:35/ is the kind of reference we
  now use to linking to entries with ids.  However, old links with
  entries that linked to ids should work just fine with our migration.
  The only URLs that might break in this release are ones using colons
  or equal signs.

* New template hooks for plugin authoring.

* As a demonstration of new template hooks for plugin authoring,
  OpenStreetMap support now moved to a plugin!

* Method to add media to collections switched from icon of paperclip
  to button with "add to collection" text.

* Bug where videos often failed to produce a proper thumbnail fixed!

* Copying around files in MediaGoblin now much more efficient, doesn't
  waste gobs of memory.

* Video transcoding now optional for videos that meet certain
  criteria.  By default, MediaGoblin will not transcode WebM videos
  that are smaller in resolution than the MediaGoblin defaults, and
  MediaGoblin can also be configured to allow Theora files to not be
  transcoded as well.

* Per-user license preference option; always want your uploads to be
  BY-SA and tired of changing that field?  You can now set your
  license preference in your user settings.

* Video player now responsive; better for mobile!

* You can now delete your account from the user preferences page if
  you so wish.

**Other changes**

* Plugin writers: Internal restructuring led to mediagoblin.db.sql* be
  mediagoblin.db.* starting from 0.3.3

* Dependency list has been reduced not requiring the "webob" package anymore.

* And many small fixes/improvements, too numerous to list!


0.3.2
=====

This will be the last release that is capable of converting from an earlier
MongoDB-based MediaGoblin instance to the newer SQL-based system.

**Do this to upgrade**

    # directory of your MediaGoblin install
    cd /srv/mediagoblin.example.org

    # copy source for this release
    git fetch
    git checkout tags/v0.3.2

    # perform any needed database updates
    bin/gmg dbupdate
    
    # restart your servers however you do that, e.g.,
    sudo service mediagoblin-paster restart
    sudo service mediagoblin-celeryd restart


**New features**

* **3d model support!**

  You can now upload STL and OBJ files and display them in
  MediaGoblin.  Requires a recent Blender; for details see:
  :ref:`deploying-chapter`

* **trim_whitespace**

  We bundle the optional plugin trim_whitespace which reduces the size
  of the delivered HTML output by reducing redundant whitespace.

  See :ref:`core-plugin-section` for plugin documentation

* **A new API!**

  It isn't well documented yet but we do have an API.  There is an
  `android application in progress <https://gitorious.org/mediagoblin/mediagoblin-android>`_
  which makes use of it, and there are some demo applications between
  `automgtic <https://github.com/jwandborg/automgtic>`_, an
  automatic media uploader for your desktop
  and `OMGMG <https://github.com/jwandborg/omgmg>`_, an example of
  a web application hooking up to the API.

  This is a plugin, so you have to enable it in your MediaGoblin
  config file by adding a section under [plugins] like::

    [plugins]
    [[mediagoblin.plugins.api]]

  Note that the API works but is not nailed down... the way it is
  called may change in future releases.

* **OAuth login support**

  For applications that use OAuth to connect to the API.

  This is a plugin, so you have to enable it in your MediaGoblin
  config file by adding a section under [plugins] like::

    [plugins]
    [[mediagoblin.plugins.oauth]]

* **Collections**

  We now have user-curated collections support.  These are arbitrary
  galleries that are customizable by users.  You can add media to
  these by clicking on the paperclip icon when logged in and looking
  at a media entry.

* **OpenStreetMap licensing display improvements**

  More accurate display of OSM licensing, and less disruptive: you
  click to "expand" the display of said licensing.

  Geolocation is also now on by default.

* **Miscellaneous visual improvements**

  We've made a number of small visual improvements including newer and
  nicer looking thumbnails and improved checkbox placement.



0.3.1
=====

**Do this to upgrade**

1. Make sure to run ``bin/gmg dbuptdate`` after upgrading.

2. If you set up your server config with an older version of
   MediaGoblin and the MediaGoblin docs, it's possible you don't
   have the "theme static files" alias, so double check to make
   sure that section is there if you are having problems.



**New features**

* **theming support**

  MediaGoblin now also includes theming support, which you can
  read about in the section :ref:`theming-chapter`.

* **flatpages**

  MediaGoblin has a flatpages plugin allowing you to add pages that
  are aren't media-related like "About this site...", "Terms of
  service...", etc.

  See :ref:`core-plugin-section` for plugin documentation


0.3.0
=====

This release has one important change. You need to act when
upgrading from a previous version!

This release changes the database system from MongoDB to
SQL(alchemy). If you want to setup a fresh instance, just
follow the instructions in the deployment chapter. If on
the other hand you want to continue to use one instance,
read on.

To convert your data from MongoDB to SQL(alchemy), you need
to follow these steps:

1. Make sure your MongoDB is still running and has your
   data, it's needed for the conversion.

2. Configure the ``sql_engine`` URI in the config to represent
   your target database (see: :ref:`deploying-chapter`)

3. You need an empty database.

4. Then run the following command::

       bin/gmg [-cf mediagoblin_config.ini] convert_mongo_to_sql

5. Start your server and investigate.

6. That's it.
