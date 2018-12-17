#!/usr/bin/env python3

import argparse
import json
import yaml


def parse_files(config_files):
    config_data = {}
    for f in config_files:
        with open(f, 'r') as stream:
            loaded_config = yaml.load(stream)
            for project in loaded_config.get('projects'):
                config_data.update({project['name']: project})
    return config_data


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("-c",
                        "--config-files",
                        nargs="+",
                        required=True,
                        help="Instance config files")

    args = parser.parse_args()
    config_data = parse_files(args.config_files)

    intermittent_issues = []
    for _, project in config_data.items():
        for known_issue in project['known_issues']:
            if known_issue['intermittent']:
                intermittent_issues.append(known_issue)

    print(json.dumps(intermittent_issues, indent=2))


if __name__ == '__main__':
    main()
