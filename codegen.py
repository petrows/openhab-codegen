#!/usr/bin/env python3
"""
    This script provides OpenHab codegen functionality.
    Purpose: generate repeating items config.
"""

from codegen import codegen
import os
import logging
import argparse
import numpy as np
import yaml
from pathlib import Path

logging.basicConfig(level=logging.DEBUG)

ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


def device_groups(item, typ):
    if 'groups' in item and typ in item['groups']:
        return ' (' + ','.join(item['groups'][typ])+')'
    return ''


def device_short_id(id):
    return id[-4:]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Openhab codegen')
    parser.add_argument(
        'config_path',
        type=Path,
        help='Devices configs folder for codegen, should contain /conf and /devices folders to traverse',
    )
    parser.add_argument(
        'openhab_path',
        type=Path,
        help='Path to openhab userdata (has items, rules, things, ... folders)',
    )
    parser.add_argument(
        '--write',
        action='store_true',
        help='Write config files to FS',
    )

    args = parser.parse_args()

    codegen = codegen.codegen(
        write=args.write,
        openhab_path=args.openhab_path,
    )
    codegen.load_config_yaml(args.config_path)
    logging.info("Loaded config from %s", args.config_path)
    codegen.run()
