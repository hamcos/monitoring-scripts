# encoding: utf-8
# Common functions used in the hamcos Monitoring appliance.
#
# @author Robin Schneider <robin.schneider@hamcos.de>
# @company hamcos IT Service GmbH http://www.hamcos.de
# @license GPL-2.0 <https://www.gnu.org/licenses/gpl-2.0.html>

import os
import re
import sys

criticality = {
    'critical': ['GK', 'Business critical', 0],
    'prod': ['PS', 'Productive system', 1],
    'test': ['TS', 'Test system', 2],
}


def exit_if_hosttag():
    hosttags = ' {} '.format(os.environ['NOTIFY_HOSTTAGS'])
    if os.environ.get('NOTIFY_PARAMETERS'):
        for tag in os.environ['NOTIFY_PARAMETERS'].split():
            match = re.search(r'\A!(.*)', tag)
            if match:  # this tag must not exist in NOTIFY_HOSTTAGS or we exit
                print('Tag: {} must not exist in HOSTTAGS'.format(
                    match.group(1),
                ))
                if re.search(r'\s%s\s' % match.group(1), hosttags):
                    os._exit(0)
            else:  # this tag must exist in NOTIFY_HOSTTAGS or we exit
                print('Tag: {} must exist in HOSTTAGS'.format(tag))
                if not re.search(r'\s%s\s' % tag, hosttags):
                    os._exit(0)


def get_criticality_for_id(id_number):
    for key, value in criticality.items():
        if value[2] == id_number:
            return value

    return None


def get_criticality_for_tags(tags):
    """ Returns list with acronym and expanded form """
    for tag in tags.split():
        if tag in criticality:
            return criticality[tag]


def get_criticality():
    """ Returns list with acronym and expanded form """

    return os.environ['NOTIFY_HOSTTAGS'].split()


def return_criti():
    """ Legacy """
    return get_criticality()


def read_contexts(bulk_mode):
    """
    Abstraction layer for different argument passing formats of Check_MK.
    """

    if bulk_mode:
        parameters, contexts = read_bulk_contexts()
    else:
        contexts = [
            dict([
                (var[7:], value)
                for (var, value)
                in os.environ.items()
                if var.startswith("NOTIFY_")
            ]),
        ]
        parameters = dict(
            [
                (var[7:], value)
                for (var, value)
                in os.environ.items()
                if var.startswith("NOTIFY_PARAMETER")
            ]
        )
    return parameters, contexts


# From the mail script. {{{


def read_bulk_contexts():
    parameters = {}
    contexts = []
    in_params = True
    context = {}

    # First comes a section with global variables
    for line in sys.stdin:
        line = line.strip()
        if line:
            key, value = line.split("=", 1)
            value = value.replace("\1", "\n")
            if in_params:
                parameters[key] = value
            else:
                context[key] = value

        else:
            in_params = False
            context = {}
            contexts.append(context)

    return parameters, contexts


def substitute_context(template, context):
    # First replace all known variables
    for varname, value in context.items():
        template = template.replace('$'+varname+'$', value)

    # Remove the rest of the variables and make them empty
    template = re.sub("\$[A-Z_][A-Z_0-9]*\$", "", template)
    return template

# }}}
