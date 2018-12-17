#!/usr/bin/python3

import json
import os
import requests

import get_data

cache_path = './haystack'

def get_all_test_names(cache_path):
    ''' Read all tests.json files, and gather a list of all tests '''
    tests = []
    for entry in os.listdir(os.path.join(cache_path, 'testruns')):
        if not os.path.isdir(os.path.join(cache_path, 'testruns', entry)):
            continue
        with open(os.path.join(cache_path, 'testruns', entry, 'tests.json')) as f:
            results = json.load(f)
        for result in results:
            if result['name'] not in tests:
                tests.append(result['name'])
    tests.sort()
    return tests

def get_builds_from_branch(branch, cache_path):
    ''' Read all tests.json files, and gather a list of all tests '''
    builds = []
    for entry in os.listdir(os.path.join(cache_path, 'builds')):
        if not os.path.isdir(os.path.join(cache_path, 'testruns', entry)):
            continue
        with open(os.path.join(cache_path, 'testruns', entry, 'tests.json')) as f:
            results = json.load(f)
        for result in results:
            if result['name'] not in tests:
                tests.append(result['name'])
    tests.sort()
    return tests


def find_intermittent_failures_on_mainline(branch, cache_path, transition_threshold=3):
    '''
    On mainline, read the test data for the last 30 builds and find tests which
    have transitioned (from fail to pass or from pass to fail) more than 3
    times. Such tests can be said to be intermittent.
    '''
    builds = []

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

    project_id = get_data.projects['4.4']
    qareports = get_data.qareports(get_data.cache_path)
    builds_url = qareports.get_object(get_data.urljoiner(get_data.squad, 'api', 'projects', project_id))['builds']
    get_env = get_env_slug()
    count = 10
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
        count -= 1
        if count <= 0:
            break

    threshold = 1
    for test, envs in tests_transitions.items():
        for env, data in envs.items():
            if data['count'] > threshold:
                print(test, env, data)













