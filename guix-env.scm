;;; GNU MediaGoblin -- federated, autonomous media hosting
;;; Copyright © 2015, 2016 David Thompson <davet@gnu.org>
;;; Copyright © 2016 Christopher Allan Webber <cwebber@dustycloud.org>
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
;;; And the first time you use it:
;;;   ./bootstrap.sh
;;;   ./configure --with-python3 --without-virtualenv
;;;   make
;;;   virtualenv . && ./bin/python setup.py develop  --no-deps
;;;
;;; ... wait whaaat, what's that last line!  I thought you said this
;;; was a reasonable virtualenv replacement!  Well it is and it will
;;; be, but there's a catch, and the catch is that Guix doesn't know
;;; about this directory and "setup.py dist" is technically necessary
;;; for certain things to run, so we have a virtualenv with nothing
;;; in it but this project itself.
;;;
;;; So anyway, now you can do:
;;;  PYTHONPATH="${PYTHONPATH}:$(pwd)" ./runtests.sh
;;;
;;; Now notably this is goofier looking than running a virtualenv,
;;; but soon I'll do something truly evil (I hope) that will make
;;; the virtualenv and path-hacking stuff unnecessary.
;;;
;;; Have fun!

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
             (gnu packages python)
             (gnu packages gstreamer)
             (gnu packages glib)
             (gnu packages rsync)
             (gnu packages ssh)
             (gnu packages version-control)
             ((guix licenses) #:select (expat zlib) #:prefix license:))

;; =================================================================
;; These packages are on their way into Guix proper but haven't made
;; it in yet... or they're old versions of packages we're pinning
;; ourselves to...
;; =================================================================

(define python-sqlalchemy-0.9.10
  (package
    (inherit python-sqlalchemy)
    (version "0.9.10")
    (source
     (origin
       (method url-fetch)
       (uri (string-append "https://pypi.python.org/packages/source/S/"
                           "SQLAlchemy/SQLAlchemy-" version ".tar.gz"))
       (sha256
        (base32
         "0fqnssf7pxvc7dvd5l83vnqz2wfvpq7y01kcl1537f9nbqnvlp24"))))

    ;; Temporarily skipping tests.  It's the stuff that got fixed in
    ;; the recent sqlalchemy release we struggled with on-list.  The
    ;; patch would have to be backported here to 0.9.10.
    (arguments
     '(#:tests? #f))))

(define python-alembic-0.6.6
  (package
    (inherit python-alembic)
    (version "0.6.6")
    (source
     (origin
       (method url-fetch)
       (uri (pypi-uri "alembic" version))
       (sha256
        (base32
         "0i3nic56blq079vj1iskkmllwjp980vnvvx898d3bm5qa416crcn"))))
    (native-inputs
     `(("python-nose" ,python-nose)
       ,@(package-native-inputs python-alembic)))
    (propagated-inputs
     `(("python-sqlalchemy" ,python-sqlalchemy-0.9.10)
       ("python-mako" ,python-mako)
       ("python-editor" ,python-editor)))))

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
    (native-inputs
     `(("python-pytest" ,python-pytest)))
    (propagated-inputs
     `(("python-alembic" ,python-alembic)
       ("python-pytest-xdist" ,python-pytest-xdist)
       ("python-celery" ,python-celery)
       ("python-kombu" ,python-kombu)
       ("python-webtest" ,python-webtest)
       ("python-pastedeploy" ,python-pastedeploy)
       ("python-paste" ,python-paste)
       ("python-pastescript" ,python-pastescript)
       ("python-translitcodec" ,python-translitcodec)
       ("python-babel" ,python-babel)
       ("python-configobj" ,python-configobj)
       ("python-dateutil-2" ,python-dateutil-2)
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
       ("python-werkzeug" ,python-werkzeug)
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
     ("gst-plugins-base" ,gst-plugins-base)
     ("gst-plugins-good" ,gst-plugins-good)
     ("gst-plugins-ugly" ,gst-plugins-ugly)
     ("gobject-introspection" ,gobject-introspection)
     ;; useful to have!
     ("coreutils" ,coreutils)
     ;; used by runtests.sh!
     ("which" ,which)
     ("git" ,git)
     ("automake" ,automake)
     ("autoconf" ,(autoconf-wrapper))
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
