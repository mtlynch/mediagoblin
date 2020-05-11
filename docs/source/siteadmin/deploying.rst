.. MediaGoblin Documentation

   Written in 2011, 2012, 2013, 2020 by MediaGoblin contributors

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

This deployment guide will take you step-by-step through
setting up your own instance of MediaGoblin.

MediaGoblin most likely isn't yet available from your operating
system's package manage, however, a basic install isn't too complex in
and of itself. We recommend a setup that combines MediaGoblin,
virtualenv and Nginx on a .deb or .rpm-based GNU/Linux distribution.

Experts may of course choose other deployment options, including
Apache. See our `Deployment wiki page
<http://wiki.mediagoblin.org/Deployment>`_ for for more details.
Please note that we are not able to provide support for these
alternative deployment options.

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

- Python 3.4+ (Python 2.7 is supported, but not recommended)
- `python3-lxml <http://lxml.de/>`_
- `git <http://git-scm.com/>`_
- `SQLite <http://www.sqlite.org/>`_/`PostgreSQL <http://www.postgresql.org/>`_
- `Python Imaging Library <http://www.pythonware.com/products/pil/>`_  (PIL)
- `virtualenv <http://www.virtualenv.org/>`_
- `Node.js <https://nodejs.org>`_

These instructions have been tested on Debian 10, CentOS 8 and
Fedora 31. These instructions should approximately translate to recent
Debian derivatives such as Ubuntu 18.04 and Trisquel 8, and to relatives of
Fedora such as CentOS 8.

Issue the following commands:

.. code-block:: bash

    # Debian 10
    sudo apt update
    sudo apt install automake git nodejs npm python3-dev python3-gi \
    python3-gst-1.0 python3-lxml python3-pil virtualenv

    # Fedora 31
    sudo dnf install automake gcc git-core make nodejs npm python3-devel \
    python3-lxml python3-pillow virtualenv

.. note::

   MediaGoblin now uses Python 3 by default. To use Python 2, you may
   instead substitute from "python3" to "python" for most package
   names in the Debian instructions and this should cover dependency
   installation. Python 2 installation has not been tested on Fedora.

For a production deployment, you'll also need Nginx as frontend web
server and RabbitMQ to store the media processing queue::

    # Debian
    sudo apt install nginx-light rabbitmq-server

    # Fedora
    sudo dnf install nginx rabbitmq-server

..
   .. note::

      You might have to enable additional repositories under Fedora
      because rabbitmq-server might be not included in official
      repositories. That looks like this for CentOS::

        sudo dnf config-manager --set-enabled centos-rabbitmq-38
        sudo dnf config-manager --set-enabled PowerTools
        sudo dnf install rabbitmq-server
        sudo systemctl enable rabbitmq-server.service
        # TODO: Celery repeatedly disconnects from RabbitMQ on CentOS 8.

      As an alternative, you can try installing redis-server and
      configure it as celery broker.

Configure PostgreSQL
~~~~~~~~~~~~~~~~~~~~

.. note::

   MediaGoblin currently supports PostgreSQL and SQLite. The default
   is a local SQLite database. This will "just work" for small
   deployments. For medium to large deployments we recommend
   PostgreSQL. If you don't want/need PostgreSQL, skip this section.

These are the packages needed for PostgreSQL::

    # Debian
    sudo apt install postgresql python3-psycopg2

    # Fedora
    sudo dnf install postgresql postgresql-server python3-psycopg2

Fedora also requires that you initialize and start the
PostgreSQL database with a few commands. The following commands are
not needed on a Debian-based platform, however::

    # Feora
    sudo /usr/bin/postgresql-setup initdb
    sudo systemctl enable postgresql
    sudo systemctl start postgresql

The installation process will create a new *system* user named ``postgres``,
which will have privileges sufficient to manage the database. We will create a
new database user with restricted privileges and a new database owned by our
restricted database user for our MediaGoblin instance.

In this example, the database user will be ``mediagoblin`` and the database
name will be ``mediagoblin`` too. We'll first at the user::

    sudo --login --user=postgres createuser --no-createdb mediagoblin

Then we'll create the database where all of our MediaGoblin data will be stored::

    sudo --login --user=postgres createdb --encoding=UTF8 --owner=mediagoblin mediagoblin

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

The following command will create a system account with a username of
``mediagoblin``.

If you are using a Debian-based system, enter this command::

    # Debian
    sudo useradd --system --create-home --home-dir /var/lib/qmediagoblin \
    --group www-data --comment 'GNU MediaGoblin system account' mediagoblin

    # Fedora
    sudo useradd --system --create-home --home-dir /var/lib/mediagoblin \
    --group nginx --comment 'GNU MediaGoblin system account' mediagoblin

This will create a ``mediagoblin`` user and assign it to a group that is
associated with the web server. This will ensure that the web server can
read the media files that users upload (images, videos, etc.)

Many operating systems will automatically create a group
``mediagoblin`` to go with the new user ``mediagoblin``, but just to
be sure::
  
    sudo groupadd --force mediagoblin
    sudo usermod --append --groups mediagoblin mediagoblin
       
No password will be assigned to this account, and you will not be able
to log in as this user. To switch to this account, enter::

    sudo su mediagoblin --shell=/bin/bash

To return to your regular user account after using the system account, type
``exit`` or ``Ctrl-d``.

.. _create-mediagoblin-directory:

Create a MediaGoblin Directory
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You should create a working directory for MediaGoblin. This document
assumes your local git repository will be located at 
``/srv/mediagoblin.example.org/mediagoblin/``.
Substitute your preferred local deployment path as needed.

Setting up the working directory requires that we first create the directory
with elevated privileges, and then assign ownership of the directory
to the unprivileged system account.

To do this, enter the following commands, changing the defaults to suit your
particular requirements::

    # Debian
    sudo mkdir --parents /srv/mediagoblin.example.org
    sudo chown --no-dereference --recursive mediagoblin:www-data /srv/mediagoblin.example.org

    # Fedora
    sudo mkdir --parents /srv/mediagoblin.example.org
    sudo chown --no-dereference --recursive mediagoblin:nginx /srv/mediagoblin.example.org


Install MediaGoblin and Virtualenv
----------------------------------

We will now switch to our 'mediagoblin' system account, and then set up
our MediaGoblin source code repository and its necessary services.
You should modify these commands to suit your own environment.

Switch to the ``mediagoblin`` unprivileged user and change to the
MediaGoblin directory that you just created::

    sudo su mediagoblin --shell=/bin/bash
    $ cd /srv/mediagoblin.example.org

.. note::

    Unless otherwise noted, the remainder of this document assumes that all
    operations are performed using the unprivileged ``mediagoblin``
    account, indicated by the ``$`` prefix.

Clone the MediaGoblin repository and set up the git submodules::

    $ git clone --depth=1 https://git.savannah.gnu.org/git/mediagoblin.git \
      --branch stable --recursive
    $ cd mediagoblin

Set up the environment::

    $ ./bootstrap.sh
    $ VIRTUALENV_FLAGS='--system-site-packages' ./configure
    $ make

.. note::

   If you'd prefer to run MediaGoblin with Python 2, pass in
   ``--without-python3`` to the ``./configure`` command.

Create and set the proper permissions on the ``user_dev`` directory.
This directory will be used to store uploaded media files::

    $ mkdir --mode=2750 user_dev

This concludes the initial configuration of the MediaGoblin
environment. In the future, you can upgrade MediaGoblin according to
the ":doc:`upgrading`" documentation.


Configure Mediagoblin
---------------------

Edit site configuration
~~~~~~~~~~~~~~~~~~~~~~~

Edit ``mediagoblin.ini`` and update ``email_sender_address`` to the
address you wish to be used as the sender for system-generated emails.
You'll find more details in ":doc:`configuration`".

.. note::

   If you're changing the MediaGoblin directories or URL prefix, you
   may need to edit ``direct_remote_path``, ``base_dir``, and
   ``base_url``.



Configure MediaGoblin to use the PostgreSQL database
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you are using PostgreSQL, edit the ``[mediagoblin]`` section in your
``mediagoblin.ini`` and remove the ``#`` prefix on the line containing::

    sql_engine = postgresql:///mediagoblin

This assumes you are running the MediaGoblin application under the
same system account and database account; both ``mediagoblin``.


Update database data structures
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Before you start using the database, you need to run::

    $ ./bin/gmg dbupdate

to populate the database with the MediaGoblin data structures.


Create an admin account
~~~~~~~~~~~~~~~~~~~~~~~

Create a MediaGoblin account with full administration access. Provide
your own email address and enter a secure password when prompted::

    $ ./bin/gmg adduser --username you --email you@example.com
    $ ./bin/gmg makeadmin you


Test the Server
~~~~~~~~~~~~~~~

At this point MediaGoblin should be properly installed.  You can
test the deployment with the following command::

    $ ./lazyserver.sh --server-name=broadcast

You should be able to connect to the machine on port 6543 in your
browser to confirm that the service is operable. You should also be
able to log in with the admin username and password.

Type ``Ctrl-c`` to exit the above server test.

The next series of commands will need to be run as a privileged user.
To return to your regular user account after using the system account,
type ``exit`` or ``Ctrl-d``.


Deploy MediaGoblin
------------------

The configuration described below is sufficient for development and
smaller deployments. However, for larger production deployments with
larger processing requirements, see the
":doc:`production-deployments`" documentation.

.. _webserver-config:

Nginx as a reverse-proxy
~~~~~~~~~~~~~~~~~~~~~~~~

This configuration example will use Nginx, however, you may use any
webserver of your choice. If you do not already have a web server,
consider Nginx, as the configuration files may be more clear than the
alternatives.

Create a configuration file at
``/srv/mediagoblin.example.org/nginx.conf`` and create a symbolic link
into a directory that will be included in your ``nginx`` configuration
(e.g. "``/etc/nginx/sites-enabled`` or ``/etc/nginx/conf.d``) with the
following commands::

    # Debian
    sudo ln --symbolic /srv/mediagoblin.example.org/nginx.conf /etc/nginx/sites-enabled/mediagoblin.conf
    sudo rm --force /etc/nginx/sites-enabled/default
    sudo systemctl enable nginx

    # Fedora
    sudo ln -s /srv/mediagoblin.example.org/nginx.conf /etc/nginx/conf.d/mediagoblin.conf
    sudo systemctl enable nginx

You can modify these commands and locations depending on your
preferences and the existing configuration of your Nginx instance. The
contents of this ``/srv/mediagoblin.example.org/nginx.conf`` file
should be modeled on the following::

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

     # Forward requests to the MediaGoblin app server.
     location / {
        proxy_pass http://127.0.0.1:6543;
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

    sudo nginx -t

If you encounter any errors, review your Nginx configuration files, and try to
resolve them. If you do not encounter any errors, you can start your Nginx
server (may vary depending on your operating system)::

    sudo systemctl restart nginx

Now start MediaGoblin to test your Nginx configuration::

    sudo su mediagoblin --shell=/bin/bash
    $ cd /srv/mediagoblin.example.org/mediagoblin/
    $ ./lazyserver.sh --server-name=main

You should be able to connect to the machine on port 80 in your
browser to confirm that the service is operable. If this is the
machine in front of you, visit <http://localhost/> or if it is a
remote server visit the URL or IP address provided to you by your
hosting provider. You should see MediaGoblin; this time via Nginx!

Try logging in and uploading an image. If after uploading you see any
"Forbidden" errors from Nginx or your image doesn't show up, you may
need to update the permissions on the new directories MediaGoblin has
created::

    # Debian
    sudo chown --no-dereference --recursive mediagoblin:www-data /srv/mediagoblin.example.org

    # Fedora
    sudo chown --no-dereference --recursive mediagoblin:nginx /srv/mediagoblin.example.org

.. note::
   
   If you see an Nginx placeholder page, you may need to remove the
   Nginx default configuration, or explictly set a ``server_name``
   directive in the Nginx config.

Type ``Ctrl-c`` to exit the above server test and ``exit`` or
``Ctrl-d`` to exit the mediagoblin shell.


.. _systemd-service-files:

Run MediaGoblin as a system service
-----------------------------------

To ensure MediaGoblin is automatically started and restarted in case of
problems, we need to run it as a system service. If your operating system uses
Systemd, you can use Systemd ``service files`` to manage both the Celery and
Paste processes.

In the Systemd configuration below, MediaGoblin log files are kept in
the ``/var/log/mediagoblin`` directory. Create the directory and give
it the proper permissions::

    sudo mkdir --parents /var/log/mediagoblin
    sudo chown --no-dereference --recursive mediagoblin:mediagoblin /var/log/mediagoblin

Place the following service files in the ``/etc/systemd/system/``
directory. The first file should be named
``mediagoblin-celeryd.service``. Be sure to modify it to suit your
environment's setup:

.. code-block:: bash

    # Set the WorkingDirectory and Environment values to match your environment.
    [Unit]
    Description=MediaGoblin Celeryd

    [Service]
    User=mediagoblin
    Group=mediagoblin
    Type=simple
    WorkingDirectory=/srv/mediagoblin.example.org/mediagoblin
    Environment=MEDIAGOBLIN_CONFIG=/srv/mediagoblin.example.org/mediagoblin/mediagoblin.ini \
                CELERY_CONFIG_MODULE=mediagoblin.init.celery.from_celery
    ExecStart=/srv/mediagoblin.example.org/mediagoblin/bin/celery worker \
                --logfile=/var/log/mediagoblin/celery.log \
                --loglevel=INFO

    [Install]
    WantedBy=multi-user.target


The second file should be named ``mediagoblin-paster.service``:

.. code-block:: bash

    # Set the WorkingDirectory and Environment values to match your environment.
    [Unit]
    Description=Mediagoblin

    [Service]
    Type=simple
    User=mediagoblin
    Group=mediagoblin
    Environment=CELERY_ALWAYS_EAGER=false
    WorkingDirectory=/srv/mediagoblin.example.org/mediagoblin
    ExecStart=/srv/mediagoblin.example.org/mediagoblin/bin/paster serve \
                /srv/mediagoblin.example.org/mediagoblin/paste.ini \
                --log-file=/var/log/mediagoblin/mediagoblin.log \
                --server-name=main

    [Install]
    WantedBy=multi-user.target


Enable these processes to start at boot by entering::

    sudo systemctl enable mediagoblin-celeryd.service && sudo systemctl enable mediagoblin-paster.service


Start the processes for the current session with::

    sudo systemctl start mediagoblin-celeryd.service
    sudo systemctl start mediagoblin-paster.service


If either command above gives you an error, you can investigate the cause of
the error by entering either of::

    sudo systemctl status mediagoblin-celeryd.service
    sudo systemctl status mediagoblin-paster.service

The above ``systemctl status`` command is also useful if you ever want to
confirm that a process is still running. If you make any changes to the service
files, you can reload the service files by entering::

    sudo systemctl daemon-reload

After entering that command, you can attempt to start the Celery or Paste
processes again using ``restart`` instead of ``start``.

Assuming the above was successful, you should now have a MediaGoblin
server that will continue to operate, even after being restarted.
Great job!


What next?
----------

This configuration supports upload of images only, but MediaGoblin
also supports other types of media, such as audio, video, PDFs and 3D
models. For details, see the ":doc:`media-types`" documentation.

..
   Local variables:
   fill-column: 70
   End:
