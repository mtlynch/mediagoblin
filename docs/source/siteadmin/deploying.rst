.. MediaGoblin Documentation

   Written in 2011, 2012, 2013 by MediaGoblin contributors

   To the extent possible under law, the author(s) have dedicated all
   copyright and related and neighboring rights to this software to
   the public domain worldwide. This software is distributed without
   any warranty.

   You should have received a copy of the CC0 Public Domain
   Dedication along with this software. If not, see
   <http://creativecommons.org/publicdomain/zero/1.0/>.

.. _deploying-chapter:

=====================
Deploying MediaGoblin
=====================

GNU MediaGoblin is fairly new, and so at the time of writing there aren't
easy package-manager-friendly methods to install it. However, doing a basic
install isn't too complex in and of itself. Following this deployment guide
will take you step-by-step through setting up your own instance of MediaGoblin.

Of course, when it comes to setting up web applications like MediaGoblin,
there's an almost infinite way to deploy things, so for now, we'll keep it
simple with some assumptions. We recommend a setup that combines MediaGoblin +
virtualenv + fastcgi + nginx on a .deb- or .rpm-based GNU/Linux distro.

Other deployment options (e.g., deploying on FreeBSD, Arch Linux, using
Apache, etc.) are possible, though! If you'd prefer a different deployment
approach, see our
`Deployment wiki page <http://wiki.mediagoblin.org/Deployment>`_.

.. note::

   These tools are for site administrators wanting to deploy a fresh
   install.  If you want to join in as a contributor, see our
   `Hacking HOWTO <http://wiki.mediagoblin.org/HackingHowto>`_ instead.

.. note::

    Throughout the documentation we use the ``sudo`` command to indicate that
    an instruction requires elevated user privileges to run. You can issue
    these commands as the ``root`` user if you prefer.
    
    If you need help configuring ``sudo``, see the
    `Debian wiki <https://wiki.debian.org/sudo/>`_ or the
    `Fedora Project wiki <https://fedoraproject.org/wiki/Configuring_Sudo/>`_. 


Prepare System
--------------

Dependencies
~~~~~~~~~~~~

MediaGoblin has the following core dependencies:

- Python 2.7 or Python 3.4+
- `python-lxml <http://lxml.de/>`_
- `git <http://git-scm.com/>`_
- `SQLite <http://www.sqlite.org/>`_/`PostgreSQL <http://www.postgresql.org/>`_
- `Python Imaging Library <http://www.pythonware.com/products/pil/>`_  (PIL)
- `virtualenv <http://www.virtualenv.org/>`_
- `nodejs <https://nodejs.org>`_

On a DEB-based system (e.g Debian, gNewSense, Trisquel, *buntu, and
derivatives) issue the following command::

    sudo apt-get install git-core python python-dev python-lxml \
        python-imaging python-virtualenv npm nodejs-legacy automake \
        nginx

On a RPM-based system (e.g. Fedora, RedHat, and derivatives) issue the
following command::

    sudo yum install python-paste-deploy python-paste-script \
        git-core python python-devel python-lxml python-imaging \
        python-virtualenv npm automake nginx

(Note: MediaGoblin now officially supports Python 3.  You may instead
substitute from "python" to "python3" for most package names in the
Debian instructions and this should cover dependency installation.
These instructions have not yet been tested on Fedora.)

Configure PostgreSQL
~~~~~~~~~~~~~~~~~~~~

.. note::

   MediaGoblin currently supports PostgreSQL and SQLite. The default is a
   local SQLite database. This will "just work" for small deployments.

   For medium to large deployments we recommend PostgreSQL.

   If you don't want/need postgres, skip this section.

These are the packages needed for Debian Jessie (stable)::

    sudo apt-get install postgresql postgresql-client python-psycopg2

These are the packages needed for an RPM-based system::

    sudo yum install postgresql postgresql-server python-psycopg2

An rpm-based system also requires that you initialize and start the
PostgresSQL database with a few commands. The following commands are
not needed on a Debian-based platform, however::

    sudo /usr/bin/postgresql-setup initdb
    sudo systemctl enable postgresql
    sudo systemctl start postgresql

The installation process will create a new *system* user named ``postgres``,
which will have privilegies sufficient to manage the database. We will create a
new database user with restricted privilegies and a new database owned by our
restricted database user for our MediaGoblin instance.

In this example, the database user will be ``mediagoblin`` and the database
name will be ``mediagoblin`` too.

We'll add these entities by first switching to the *postgres* account::

    sudo su - postgres

This will change your prompt to a shell prompt, such as *-bash-4.2$*. Enter
the following *createuser* and *createdb* commands at that prompt. We'll
create the *mediagoblin* database user first::

    # this command and the one that follows are run as the ``postgres`` user:
    createuser -A -D mediagoblin

Then we'll create the database where all of our MediaGoblin data will be stored::

    createdb -E UNICODE -O mediagoblin mediagoblin

where the first ``mediagoblin`` is the database owner and the second
``mediagoblin`` is the database name.

Type ``exit`` to exit from the 'postgres' user account.::

    exit

.. caution:: Where is the password?

    These steps enable you to authenticate to the database in a password-less
    manner via local UNIX authentication provided you run the MediaGoblin
    application as a user with the same name as the user you created in
    PostgreSQL.

    More on this in :ref:`Drop Privileges for MediaGoblin <drop-privileges-for-mediagoblin>`.


.. _drop-privileges-for-mediagoblin:

Drop Privileges for MediaGoblin
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

MediaGoblin does not require special permissions or elevated
access to run. As such, the preferred way to run MediaGoblin is to
create a dedicated, unprivileged system user for the sole purpose of running
MediaGoblin. Running MediaGoblin processes under an unprivileged system user
helps to keep it more secure. 

The following command (entered as root or with sudo) will create a
system account with a username of ``mediagoblin``. You may choose a different
username if you wish.

If you are using a Debian-based system, enter this command::

    sudo useradd -c "GNU MediaGoblin system account" -d /var/lib/mediagoblin -m -r -g www-data mediagoblin

If you are using an RPM-based system, enter this command::

    sudo useradd -c "GNU MediaGoblin system account" -d /var/lib/mediagoblin -m -r -g nginx mediagoblin

This will create a ``mediagoblin`` user and assign it to a group that is
associated with the web server. This will ensure that the web server can
read the media files (images, videos, etc.) that users upload.

We will also create a ``mediagoblin`` group and associate the mediagoblin
user with that group, as well::
  
    sudo groupadd mediagoblin && sudo usermod --append -G mediagoblin mediagoblin
       
No password will be assigned to this account, and you will not be able
to log in as this user. To switch to this account, enter::

    sudo su mediagoblin -s /bin/bash

To return to your regular user account after using the system account, type
``exit``.

.. _create-mediagoblin-directory:

Create a MediaGoblin Directory
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You should create a working directory for MediaGoblin. This document
assumes your local git repository will be located at 
``/srv/mediagoblin.example.org/mediagoblin/``.
Substitute your prefered local deployment path as needed.

Setting up the working directory requires that we first create the directory
with elevated priviledges, and then assign ownership of the directory
to the unprivileged system account.

To do this, enter the following command, changing the defaults to suit your
particular requirements. On a Debian-based platform you will enter this::

    sudo mkdir -p /srv/mediagoblin.example.org && sudo chown -hR mediagoblin:www-data /srv/mediagoblin.example.org

On an RPM-based distribution, enter this command::

    sudo mkdir -p /srv/mediagoblin.example.org && sudo chown -hR mediagoblin:nginx /srv/mediagoblin.example.org

.. note::

    Unless otherwise noted, the remainder of this document assumes that all
    operations are performed using this unprivileged account.


Install MediaGoblin and Virtualenv
----------------------------------

We will now switch to our 'mediagoblin' system account, and then set up
our MediaGoblin source code repository and its necessary services.
You should modify these commands to suit your own environment.

Change to the MediaGoblin directory that you just created::

    sudo su mediagoblin -s /bin/bash  # to change to the 'mediagoblin' account
    $ cd /srv/mediagoblin.example.org

Clone the MediaGoblin repository and set up the git submodules::

    $ git clone git://git.savannah.gnu.org/mediagoblin.git -b stable
    $ cd mediagoblin
    $ git submodule init && git submodule update

.. note::

   The MediaGoblin repository used to be on gitorious.org, but since
   gitorious.org shut down, we had to move.  We are presently on
   Savannah.  You may need to update your git repository location::

    $ git remote set-url origin git://git.savannah.gnu.org/mediagoblin.git

Set up the hacking environment::

    $ ./bootstrap.sh && ./configure && make

(Note that if you'd prefer to run MediaGoblin with Python 3, pass in
`--with-python3` to the `./configure` command.)

Create and set the proper permissions on the ``user_dev`` directory.
This directory will be used to store uploaded media files::

    $ mkdir user_dev && chmod 750 user_dev

Assuming you are going to deploy with FastCGI, you should also install
flup::

    $ ./bin/easy_install flup

(Note, if you're running Python 2, which you probably are at this
point in MediaGoblin's development, you'll need to run:)

    $ ./bin/easy_install flup==1.0.3.dev-20110405

The above provides an in-package install of ``virtualenv``. While this
is counter to the conventional ``virtualenv`` configuration, it is
more reliable and considerably easier to configure and illustrate. If
you're familiar with Python packaging you may consider deploying with
your preferred method.

.. note::

   What if you don't want an in-package ``virtualenv``?  Maybe you
   have your own ``virtualenv``, or you are building a MediaGoblin
   package for a distribution.  There's no need necessarily for the
   virtualenv produced by ``./configure && make`` by default other
   than attempting to simplify work for developers and people
   deploying by hiding all the virtualenv and bower complexity.

   If you want to install all of MediaGoblin's libraries
   independently, that's totally fine!  You can pass the flag
   ``--without-virtualenv`` which will skip this step.   
   But you will need to install all those libraries manually and make
   sure they are on your ``PYTHONPATH`` yourself!  (You can still use
   ``python setup.py develop`` to install some of those libraries,
   but note that no ``./bin/python`` will be set up for you via this
   method, since no virtualenv is set up for you!)

This concludes the initial configuration of the MediaGoblin 
environment. In the future, when you update your
codebase, you should also run::

    $ git submodule update && ./bin/python setup.py develop --upgrade && ./bin/gmg dbupdate

.. note::

    Note: If you are running an active site, depending on your server
    configuration, you may need to stop it first or the dbupdate command
    may hang (and it's certainly a good idea to restart it after the
    update)


Deploy MediaGoblin Services
---------------------------

Edit site configuration
~~~~~~~~~~~~~~~~~~~~~~~

A few basic properties must be set before MediaGoblin will work. First
make a copy of ``mediagoblin.ini`` and ``paste.ini`` for editing so the original
config files aren't lost (you likely won't need to edit the paste configuration,
but we'll make a local copy of it just in case)::

    $ cp -av mediagoblin.ini mediagoblin_local.ini && cp -av paste.ini paste_local.ini

Then edit mediagoblin_local.ini:
 - Set ``email_sender_address`` to the address you wish to be used as
   the sender for system-generated emails
 - Edit ``direct_remote_path``, ``base_dir``, and ``base_url`` if
   your mediagoblin directory is not the root directory of your
   vhost.


Configure MediaGoblin to use the PostgreSQL database
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you are using postgres, edit the ``[mediagoblin]`` section in your
``mediagoblin_local.ini`` and put in::

    sql_engine = postgresql:///mediagoblin

if you are running the MediaGoblin application as the same 'user' as the
database owner.


Update database data structures
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Before you start using the database, you need to run::

    $ ./bin/gmg dbupdate

to populate the database with the MediaGoblin data structures.


Test the Server
~~~~~~~~~~~~~~~

At this point MediaGoblin should be properly installed.  You can
test the deployment with the following command::

    $ ./lazyserver.sh --server-name=broadcast

You should be able to connect to the machine on port 6543 in your
browser to confirm that the service is operable.

The next series of commands will need to be run as a priviledged user. Type
exit to return to the root/sudo account.::

    exit

.. _webserver-config:


FastCGI and nginx
~~~~~~~~~~~~~~~~~

This configuration example will use nginx, however, you may
use any webserver of your choice as long as it supports the FastCGI
protocol. If you do not already have a web server, consider nginx, as
the configuration files may be more clear than the
alternatives.

Create a configuration file at
``/srv/mediagoblin.example.org/nginx.conf`` and create a symbolic link
into a directory that will be included in your ``nginx`` configuration
(e.g. "``/etc/nginx/sites-enabled`` or ``/etc/nginx/conf.d``) with
one of the following commands.

On a DEB-based system (e.g Debian, gNewSense, Trisquel, *buntu, and
derivatives) issue the following commands::

    sudo ln -s /srv/mediagoblin.example.org/nginx.conf /etc/nginx/sites-enabled/
    sudo systemctl enable nginx

On a RPM-based system (e.g. Fedora, RedHat, and derivatives) issue the
following commands::

    sudo ln -s /srv/mediagoblin.example.org/nginx.conf /etc/nginx/conf.d/
    sudo systemctl enable nginx

You can modify these commands and locations depending on your preferences and
the existing configuration of your nginx instance. The contents of
this ``nginx.conf`` file should be modeled on the following::

    server {
     #################################################
     # Stock useful config options, but ignore them :)
     #################################################
     include /etc/nginx/mime.types;

     autoindex off;
     default_type  application/octet-stream;
     sendfile on;

     # Gzip
     gzip on;
     gzip_min_length 1024;
     gzip_buffers 4 32k;
     gzip_types text/plain application/x-javascript text/javascript text/xml text/css;

     #####################################
     # Mounting MediaGoblin stuff
     # This is the section you should read
     #####################################

     # Change this to update the upload size limit for your users
     client_max_body_size 8m;

     # prevent attacks (someone uploading a .txt file that the browser
     # interprets as an HTML file, etc.)
     add_header X-Content-Type-Options nosniff;

     server_name mediagoblin.example.org www.mediagoblin.example.org;
     access_log /var/log/nginx/mediagoblin.example.access.log;
     error_log /var/log/nginx/mediagoblin.example.error.log;

     # MediaGoblin's stock static files: CSS, JS, etc.
     location /mgoblin_static/ {
        alias /srv/mediagoblin.example.org/mediagoblin/mediagoblin/static/;
     }

     # Instance specific media:
     location /mgoblin_media/ {
        alias /srv/mediagoblin.example.org/mediagoblin/user_dev/media/public/;
     }

     # Theme static files (usually symlinked in)
     location /theme_static/ {
        alias /srv/mediagoblin.example.org/mediagoblin/user_dev/theme_static/;
     }

     # Plugin static files (usually symlinked in)
     location /plugin_static/ {
        alias /srv/mediagoblin.example.org/mediagoblin/user_dev/plugin_static/;
     }

     # Mounting MediaGoblin itself via FastCGI.
     location / {
        fastcgi_pass 127.0.0.1:26543;
        include /etc/nginx/fastcgi_params;

        # our understanding vs nginx's handling of script_name vs
        # path_info don't match :)
        fastcgi_param PATH_INFO $fastcgi_script_name;
        fastcgi_param SCRIPT_NAME "";
     }
    }

The first four ``location`` directives instruct Nginx to serve the
static and uploaded files directly rather than through the MediaGoblin
process. This approach is faster and requires less memory.

.. note::

   The user who owns the Nginx process, normally ``www-data`` or ``nginx``,
   requires execute permission on the directories ``static``,
   ``public``, ``theme_static`` and ``plugin_static`` plus all their
   parent directories. This user also requires read permission on all
   the files within these directories. This is normally the default.

Nginx is now configured to serve the MediaGoblin application. Perform a quick
test to ensure that this configuration works::

    nginx -t

If you encounter any errors, review your nginx configuration files, and try to
resolve them. If you do not encounter any errors, you can start your nginx
server with one of the following commands (depending on your environment)::

    sudo /etc/init.d/nginx restart
    sudo /etc/rc.d/nginx restart
    sudo systemctl restart nginx

Now start MediaGoblin. Use the following command sequence as an
example::

    cd /srv/mediagoblin.example.org/mediagoblin/
    su mediagoblin -s /bin/bash
    ./lazyserver.sh --server-name=fcgi fcgi_host=127.0.0.1 fcgi_port=26543

Visit the site you've set up in your browser by visiting
<http://mediagoblin.example.org>. You should see MediaGoblin!

.. note::

   The configuration described above is sufficient for development and
   smaller deployments. However, for larger production deployments
   with larger processing requirements, see the
   ":doc:`production-deployments`" documentation.
   

Apache
~~~~~~

Instructions and scripts for running MediaGoblin on an Apache server
can be found on the `MediaGoblin wiki <http://wiki.mediagoblin.org/Deployment>`_.


Should I Keep Open Registration Enabled?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Unfortunately, in this current release of MediaGoblin we are suffering
from spammers registering to public instances en masse.  As such, you
may want to either:

a) Disable registration on your instance and just make
   accounts for people you know and trust (eg via the `gmg adduser`
   command).  You can disable registration in your mediagoblin.ini
   like so::

     [mediagoblin]
     allow_registration = false

b) Enable a captcha plugin.  But unfortunately, though some captcha
   plugins exist, for various reasons we do not have any general
   recommendations we can make at this point.

We hope to have a better solution to this situation shortly.  We
apologize for the inconvenience in the meanwhile.


Security Considerations
~~~~~~~~~~~~~~~~~~~~~~~

.. warning::

   The directory ``user_dev/crypto/`` contains some very
   sensitive files.
   Especially the ``itsdangeroussecret.bin`` is very important
   for session security. Make sure not to leak its contents anywhere.
   If the contents gets leaked nevertheless, delete your file
   and restart the server, so that it creates a new secret key.
   All previous sessions will be invalidated.

..
   Local variables:
   fill-column: 70
   End:
