#!/bin/bash

# GNU MediaGoblin -- federated, autonomous media hosting
# Copyright (C) 2015 GNU MediaGoblin contributors.  See AUTHORS.
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

# exit if anything fails
set -e

if [ -f "./bin/pybabel" ]; then
    PYBABEL="./bin/pybabel";
else
    PYBABEL=pybabel;
fi


## This used to be a lot simpler...
##
## But now we have a Lojban translation that we can't compile
## currently.  We don't want to get rid of it because we want it... see 
## https://issues.mediagoblin.org/ticket/1070
## to track progress.

for file in `find mediagoblin/i18n/ -name "*.po"`; do
    if [ "$file" != "mediagoblin/i18n/jbo/mediagoblin.po" ] && \
       [ "$file" != "mediagoblin/i18n/templates/en/mediagoblin.po" ]; then 
        mkdir -p `dirname $file`/LC_MESSAGES/;
        $PYBABEL compile -i $file \
               -o `dirname $file`/LC_MESSAGES/mediagoblin.mo \
               -l `echo $file | awk -F / '{ print $3 }'`;
    else
        echo "Skipping $file which pybabel can't compile :("; 
    fi;
done
