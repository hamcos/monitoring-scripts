#!/usr/bin/env python3
# encoding: utf-8
# @author Robin Schneider <robin.schneider@hamcos.de>
# @company hamcos IT Service GmbH http://www.hamcos.de
# @license AGPLv3 <https://www.gnu.org/licenses/agpl-3.0.html>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, version 3 of the
# License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# Rewrite of
# http://git.mathias-kettner.de/git/?p=check_mk.git;a=blob;f=doc/treasures/wato_import.py
# to allow more flexibility and have a nicer code base.

"""
Read CSV host list and create the hosts in Check_MK WATO.
"""

__version__ = '0.7'

# modules {{{
# std {{{
import os
import logging
import csv
import re
# }}}
# }}}


class CsvToCheckMkConverter:
    CMK_TAG_SEPARATOR = '|'
    DEFAULT_HOST_TAGS = CMK_TAG_SEPARATOR.join(('wato', '/\' + FOLDER_PATH + \'/'))
    KEYS_IN_HOST_ATTRIBUTES = [
        'alias',
        'ipaddress'
    ]

    def __init__(
        self,
        csv_file,
        wato_default_folder=None,
        hostname_suffix='',
        host_tags='',
    ):

        self._csv_file = csv_file
        self._wato_default_folder = wato_default_folder
        self._hostname_suffix = hostname_suffix

        if host_tags:
            self._host_tags = self.CMK_TAG_SEPARATOR.join((host_tags, self.DEFAULT_HOST_TAGS))
        else:
            self._host_tags = self.DEFAULT_HOST_TAGS

        self._folders = {}

        self._csv_fh = open(self._csv_file, newline='')

        sample = self._csv_fh.read(1024)
        if not csv.Sniffer().has_header(sample):
            raise Exception("No header line in CSV file found. Example header: hostname;ip;description")
        self._csv_fh.seek(0)  # rewind

        # FIXME might use sniffer for delimiter detection.
        # logger.debug(csv.Sniffer().sniff(sample))
        if sample.find(','):
            self._csv_delimiter = ';'
        elif sample.find(';'):
            self._csv_delimiter = ';'
        else:
            raise Exception("Unknown CSV delimiter.")

    def parse(self):
        for self.__row in csv.DictReader(
                filter(lambda row: row[0] != '#', self._csv_fh),
                delimiter=self._csv_delimiter
        ):

            if re.match(r'\s*$', self.__row['hostname']):
                continue

            self._parse_row()

    def _parse_row(self):
        logger.debug("Parsing row: \"{0}\"".format(self.__row))

        host_properties = {
            'hostname':   self.__row['hostname'] + self._hostname_suffix,
            'host_alias': self.__get_host_property('host_alias'),
            'ipaddress':  self.__get_host_property('ipaddress'),
            'host_tags':  self.__get_host_property('host_tags', default=''),
        }

        if self._host_tags:
            if host_properties['host_tags']:
                host_properties['host_tags'] += self.CMK_TAG_SEPARATOR + self._host_tags
            else:
                host_properties['host_tags'] = self._host_tags

        if not host_properties['ipaddress']:
            host_properties['ipaddress'] = self.__get_host_property('ip')

        wato_foldername = self._wato_default_folder
        if 'wato_foldername' is self.__row and self.__row['wato_foldername']:
            wato_foldername = self.__row['wato_foldername']
        elif not wato_foldername:
            raise Exception(
                "Column wato_foldername not given."
                " Either specify it in the CSV file or use the parameter "
            )

        if not host_properties['ipaddress'] or host_properties['ipaddress'].lower() == "None".lower():
            host_properties['ipaddress'] = False

        self._folders.setdefault(wato_foldername, []).append(host_properties)

    def __get_host_property(self, host_property, prefix='', suffix='', default=None):
        if host_property in self.__row:
            return prefix + self.__row[host_property].strip() + suffix
        elif type(default) is str:
            return prefix + default + suffix
        else:
            return default

    def _get_host_attributes_string(self, host_properties):
        host_attributes = ''
        for host_property in self.KEYS_IN_HOST_ATTRIBUTES:
            if host_property in host_properties and host_properties[host_property]:
                    # host_attributes += "\t'{}': {{'alias' : u'{}', 'ipaddress' : '{}' }},\n".format(
                host_attributes += "'{}': u'{}', ".format(host_property, host_properties[host_property])

        if host_attributes:
            return "\t'{}': {{ {}}},\n".format(
                host_properties['hostname'],
                host_attributes,
            )
        else:
            return ''

    def write_configuration(self, export_dir):
        for wato_foldername in self._folders:
            path = os.path.join(export_dir, wato_foldername)
            try:
                os.makedirs(path)
            except os.error:
                pass
                # logger.debug("Could not create directory for {}: {}".format(wato_foldername, err))
            all_hosts = ""
            host_attributes = ""
            ips = ""
            for host_properties in self._folders[wato_foldername]:
                all_hosts += "\t'{}{}',\n".format(
                    host_properties['hostname'],
                    self.CMK_TAG_SEPARATOR + host_properties['host_tags'] if host_properties['host_tags'] else '',
                )
                host_attributes += self._get_host_attributes_string(host_properties)
                if host_properties['ipaddress']:
                    ips += "\t'{}': '{}',\n".format(host_properties['hostname'], host_properties['ipaddress'])

            config_file = os.path.join(export_dir, wato_foldername, 'hosts.mk')
            logger.info("Writing configuration file: {}".format(config_file))
            target_file = open(config_file, 'w')
            target_file.write('# Written by {}\n'.format(os.path.basename(__file__)))
            target_file.write('# encoding: utf-8\n')

            target_file.write('all_hosts += [\n')
            target_file.write(all_hosts)
            target_file.write(']\n\n')

            target_file.write('host_attributes.update({\n')
            target_file.write(host_attributes)
            target_file.write('})\n\n')

            if len(ips) > 0:
                target_file.write('ipaddresses.update({\n')
                target_file.write(ips)
                target_file.write('})\n')

            target_file.close()


# main {{{
if __name__ == '__main__':
    from argparse import ArgumentParser, RawTextHelpFormatter

    args_parser = ArgumentParser(
        description=__doc__,
        formatter_class=RawTextHelpFormatter,
        epilog="CSV example:\n\t" +
        '\n\t'.join(
            [
                "wato_foldername;hostname;host_alias;ipaddress;host_tags",
                "production;main.domain.tld;main;;own_tag",
            ]
        )
    )
    args_parser.add_argument(
        '-V', '--version',
        action='version',
        version='%(prog)s {version}'.format(version=__version__),
    )
    args_parser.add_argument(
        '-d', '--debug',
        help="Print lots of debugging statements",
        action="store_const", dest="loglevel", const=logging.DEBUG,
        default=logging.WARNING,
    )
    args_parser.add_argument(
        '-v', '--verbose',
        help="Be verbose",
        action="store_const", dest="loglevel", const=logging.INFO,
    )
    args_parser.add_argument(
        'csv_file',
        help=u"CSV host list file to import.",
    )
    args_parser.add_argument(
        '-e', '--export-dir',
        help="Check_MK WATO directory path where the generated configuration should be written to"
        " (default: %(default)s).",
        default='/etc/check_mk/conf.d/wato',
    )
    args_parser.add_argument(
        '-w', '--wato-default-folder',
        help="Set a WATO default folder if non was specified for a given host.",
    )
    args_parser.add_argument(
        '-s', '--hostname-suffix',
        help="Append this suffix to all hostnames.",
        default='',
    )
    args_parser.add_argument(
        '-t', '--host-tags',
        help="Append these tags to all hostnames. Use a pipe „{}“ as tag separator.".format(
            CsvToCheckMkConverter.CMK_TAG_SEPARATOR
        ),
        default='',
    )

    args = args_parser.parse_args()
    logger = logging.getLogger(__file__)
    logging.basicConfig(
        format='%(levelname)s: %(message)s',
        level=args.loglevel,
        # level=logging.DEBUG,
        # level=logging.INFO,
    )

    parser = CsvToCheckMkConverter(
        args.csv_file,
        wato_default_folder=args.wato_default_folder,
        hostname_suffix=args.hostname_suffix,
        host_tags=args.host_tags,
    )

    parser.parse()
    parser.write_configuration(args.export_dir)

# }}}
