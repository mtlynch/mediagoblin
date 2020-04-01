;;; GNU MediaGoblin -- federated, autonomous media hosting
;;; Copyright © 2015, 2016 David Thompson <davet@gnu.org>
;;; Copyright © 2016 Christopher Allan Webber <cwebber@dustycloud.org>
;;; Copyright © 2019 Ben Sturmfels <ben@sturm.com.au>
;;;
;;; This program is free software: you can redistribute it and/or modify
;;; it under the terms of the GNU General Public License as published by
;;; the Free Software Foundation, either version 3 of the License, or
;;; (at your option) any later version.
;;;
;;; This program is distributed in the hope that it will be useful,
;;; but WITHOUT ANY WARRANTY; without even the implied warranty of
;;; MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
;;; GNU General Public License for more details.
;;;
;;; ========================================
;;;
;;; ... This file is also part of GNU MediaGoblin, but we're leaving it
;;; under GPLv3 for easy merge back and forth between Guix proper.  It
;;; also borrows some code directly from Guix.
;;;
;;; ========================================
;;;
;;; With `guix environment' you can use guix as kind of a universal
;;; virtualenv, except a universal virtualenv with magical time traveling
;;; properties and also, not just for Python.
;;;
;;; Ok, here's how to use this thing!  First, install Guix.
;;; Then do:
;;;   guix environment -l guix-env.scm --pure
;;;
;;; While using --pure is a robust way to ensure that other environment
;;; variables don't cause unexpected behaviour, it may trip up aspects of your
;;; development tools, such as removing reference to $EDITOR. Feel free to
;;; remove the --pure.
;;;
;;; You'll need to run the above command every time you close your terminal or
;;; restart your system, so a handy way to save having to remember is to install
;;; "direnv" an then create a ".envrc" file in your current directory containing
;;; the following and then run "direnv allow" when prompted:
;;;   use guix -l guix-env.scm
;;;
;;; To set things up for the first time, you'll also need to run:
;;;   git submodule init
;;;   git submodule update
;;;   ./bootstrap.sh
;;;   ./configure --with-python3 --without-virtualenv
;;;   make
;;;   python3 -m venv --system-site-packages . && bin/python setup.py develop  --no-deps
;;;
;;; ... wait whaaat, what's that last line!  I thought you said this
;;; was a reasonable virtualenv replacement!  Well it is and it will
;;; be, but there's a catch, and the catch is that Guix doesn't know
;;; about this directory and "setup.py dist" is technically necessary
;;; for certain things to run, so we have a virtualenv with nothing
;;; in it but this project itself.
;;;
;;; The devtools/update_extlib.sh script won't run on Guix due to missing
;;; "/usr/bin/env", so then run:
;;;   node node_modules/.bin/bower install
;;;   ./devtools/update_extlib.sh
;;;   bin/gmg dbupdate
;;;   bin/gmg adduser --username admin --password a --email admin@example.com
;;;   ./lazyserver.sh
;;;
;;; So anyway, now you can do:
;;;  PYTHONPATH="${PYTHONPATH}:$(pwd)" ./runtests.sh
;;;
;;; Now notably this is goofier looking than running a virtualenv,
;;; but soon I'll do something truly evil (I hope) that will make
;;; the virtualenv and path-hacking stuff unnecessary.
;;;
;;; Have fun!
;;;
;;; Known issues:
;;;  - currently fails to upload h264 source video: "GStreamer: missing H.264 decoder"

(use-modules (ice-9 match)
             (srfi srfi-1)
             (guix packages)
             (guix licenses)
             (guix download)
             (guix git-download)
             (guix build-system gnu)
             (guix build-system python)
             (gnu packages)
             (gnu packages autotools)
             (gnu packages base)
             (gnu packages certs)
             (gnu packages check)
             (gnu packages databases)
             (gnu packages python)
             (gnu packages python-crypto)
             (gnu packages python-web)
             (gnu packages python-xyz)
             (gnu packages sphinx)
             (gnu packages gstreamer)
             (gnu packages glib)
             (gnu packages rsync)
             (gnu packages ssh)
             (gnu packages time)
             (gnu packages version-control)
             (gnu packages xml)
             ((guix licenses) #:select (expat zlib) #:prefix license:))

;; =================================================================
;; These packages are on their way into Guix proper but haven't made
;; it in yet... or they're old versions of packages we're pinning
;; ourselves to...
;; =================================================================

(define python-pytest-forked
  (package
   (name "python-pytest-forked")
   (version "1.0.2")
   (source
    (origin
     (method url-fetch)
     (uri (pypi-uri "pytest-forked" version))
     (sha256
      (base32
       "0f4y1jhcg70xhm220pdb8r24n01knhn749aqlr14vmgbsb7allnk"))))
   (build-system python-build-system)
   (propagated-inputs
    `(("python-pytest" ,python-pytest)
      ("python-setuptools-scm" ,python-setuptools-scm)))
   (home-page
    "https://github.com/pytest-dev/pytest-forked")
   (synopsis
    "run tests in isolated forked subprocesses")
   (description
    "run tests in isolated forked subprocesses")
   (license license:expat)))

;; =================================================================

(define mediagoblin
  (package
    (name "mediagoblin")
    (version "0.8.1")
    (source
     (origin
       (method url-fetch)
       (uri (pypi-uri "mediagoblin" version))
       (sha256
        (base32
         "0p2gj4z351166d1zqmmd8wc9bzb69w0fjm8qq1fs8dw2yhcg2wwv"))))
    (build-system python-build-system)
    (arguments
     ;; Complains about missing gunicorn. Not sure where that comes from.
     '(#:tests? #f))
    (native-inputs
     `(("python-pytest" ,python-pytest)
       ("nss-certs" ,nss-certs)))
    (propagated-inputs
     `(("python-alembic" ,python-alembic)
       ("python-pytest-xdist" ,python-pytest-xdist)
       ("python-pytest-forked" ,python-pytest-forked)
       ("python-celery" ,python-celery)
       ("python-kombu" ,python-kombu)
       ("python-webtest" ,python-webtest)
       ("python-pastedeploy" ,python-pastedeploy)
       ("python-paste" ,python-paste)
       ("python-pastescript" ,python-pastescript)
       ("python-translitcodec" ,python-translitcodec)
       ("python-babel" ,python-babel)
       ("python-configobj" ,python-configobj)
       ("python-dateutil" ,python-dateutil)
       ("python-itsdangerous" ,python-itsdangerous)
       ("python-jinja2" ,python-jinja2)
       ("python-jsonschema" ,python-jsonschema)
       ("python-lxml" ,python-lxml)
       ("python-markdown" ,python-markdown)
       ("python-oauthlib" ,python-oauthlib)
       ("python-pillow" ,python-pillow)
       ("python-py-bcrypt" ,python-py-bcrypt)
       ("python-pyld" ,python-pyld)
       ("python-pytz" ,python-pytz)
       ("python-requests" ,python-requests)
       ("python-setuptools" ,python-setuptools)
       ("python-six" ,python-six)
       ("python-sphinx" ,python-sphinx)
       ("python-docutils" ,python-docutils)
       ("python-sqlalchemy" ,python-sqlalchemy)
       ("python-unidecode" ,python-unidecode)
       ("python-werkzeug" ,python-werkzeug)  ; Broken due to missing werkzeug.contrib.atom in 1.0.0.
       ("python-exif-read" ,python-exif-read)
       ("python-wtforms" ,python-wtforms)))
    (home-page "http://mediagoblin.org/")
    (synopsis "Web application for media publishing")
    (description "MediaGoblin is a web application for publishing all kinds of
media.")
    (license agpl3+)))

(package
  (inherit mediagoblin)
  (name "mediagoblin-hackenv")
  (version "git")
  (inputs
   `(;;; audio/video stuff
     ("gstreamer" ,gstreamer)
     ("gst-libav" ,gst-plugins-base)
     ("gst-plugins-base" ,gst-plugins-base)
     ("gst-plugins-good" ,gst-plugins-good)
     ("gst-plugins-bad" ,gst-plugins-bad)
     ("gst-plugins-ugly" ,gst-plugins-ugly)
     ("gobject-introspection" ,gobject-introspection)
     ;; useful to have!
     ("coreutils" ,coreutils)
     ;; used by runtests.sh!
     ("which" ,which)
     ("git" ,git)
     ("automake" ,automake)
     ("autoconf" ,autoconf)
     ,@(package-inputs mediagoblin)))
  (propagated-inputs
   `(("python" ,python)
     ("python-virtualenv" ,python-virtualenv)
     ("python-pygobject" ,python-pygobject)
     ("python-gst" ,python-gst)
     ;; Needs python-gst in order for all tests to pass
     ("python-numpy" ,python-numpy)  ; this pulls in texlive...
                                     ; and texlive-texmf is very large...
     ("python-chardet", python-chardet)
     ("python-psycopg2" ,python-psycopg2)
     ;; For developing
     ("openssh" ,openssh)
     ("git" ,git)
     ("rsync" ,rsync)
     ,@(package-propagated-inputs mediagoblin))))
