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

import argparse
import os

from alembic import config
from sqlalchemy.orm import sessionmaker

from mediagoblin.db.open import setup_connection_and_db_from_config
from mediagoblin.init import setup_global_and_app_config


class FudgedCommandLine(config.CommandLine):
    def main(self, args, db):
        options = self.parser.parse_args(args.args_for_alembic)
        if not hasattr(options, "cmd"):
            print(
                "* Only use this command if you know what you are doing! *\n"
                "If not, use the 'gmg dbupdate' command instead.\n\n"
                "Alembic help:\n")
            self.parser.print_help()
            return
        else:
            Session = sessionmaker(bind=db.engine)

            root_dir = os.path.abspath(os.path.dirname(os.path.dirname(
                os.path.dirname(__file__))))
            alembic_cfg_path = os.path.join(root_dir, 'alembic.ini')
            cfg = config.Config(alembic_cfg_path,
                                cmd_opts=options)
            cfg.attributes["session"] = Session()
            self.run_cmd(cfg, options)
        
def parser_setup(subparser):
    subparser.add_argument("args_for_alembic", nargs=argparse.REMAINDER)

def raw_alembic_cli(args):
    global_config, app_config = setup_global_and_app_config(args.conf_file)
    db = setup_connection_and_db_from_config(app_config, migrations=False)
    FudgedCommandLine().main(args, db)
