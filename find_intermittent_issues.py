#!/usr/bin/python3

import json
import os
import requests

import get_data

cache_path = './haystack'

class get_env_slug:
    def __init__(self):
        self.urls = {}

    def get_env_slug(self, url):
        if url in self.urls:
            return self.urls[url]
        r = requests.get(url)
        r.raise_for_status()
        self.urls[url] = r.json()['slug']
        return r.json()['slug']

if __name__ == '__main__':
    tests_transitions = {} # Dictionary of test names and transition counts
    threshold = 2 # Find tests that have changed state more than this many times
    builds = 10 # Look through this many builds
    branch = '4.4' # Look through builds on this branch

    project_id = get_data.projects[branch]
    qareports = get_data.qareports(get_data.cache_path)
    builds_url = qareports.get_object(get_data.urljoiner(get_data.squad, 'api', 'projects', project_id))['builds']
    get_env = get_env_slug()
    for build in qareports.get_objects(builds_url):
        for testrun in qareports.get_objects(build['testruns']):
            tests = qareports.get_leaf_objects(testrun['tests'])
            for test in tests:
                if test['name'] not in tests_transitions:
                    tests_transitions[test['name']] = {}
                env_slug = get_env.get_env_slug(testrun['environment'])
                if env_slug not in tests_transitions[test['name']]:
                    tests_transitions[test['name']][env_slug] = {'count': 0, 'status': test['status']}
                    continue

                # state transition
                if test['status'] != tests_transitions[test['name']][env_slug]['status']:
                    tests_transitions[test['name']][env_slug]['count'] += 1
        builds -= 1
        if builds <= 0:
            break

    for test, envs in tests_transitions.items():
        for env, data in envs.items():
            if data['count'] > threshold:
                print(test, env, data)













