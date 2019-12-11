#!/usr/bin/python3 -u

import json
import os
import os.path
import requests
import time

squad = 'https://qa-reports.linaro.org'
api = 'api'
cache_path = './haystack'
projects = {
    '4.4': '40',
    '4.9': '23',
#    '4.14': '58',
#    '4.19': '135',
#    'mainline': '22',
}

def urljoiner(*args):
    '''
    Joins given arguments into an url. Trailing but not leading slashes are
    stripped for each argument.
    '''
    return "/".join(map(lambda x: str(x).rstrip('/'), args))

def url_to_fs(url):
    ''' Given a squad api url, return a filesystem path '''
    return url.split(urljoiner(squad, api)+'/')[1].rstrip('/') + '.json'

class qareports:
    def __init__(self, cache_path):
        self.cache_path = cache_path

    def cache_file_from_url(self, url):
        return os.path.join(os.path.realpath(self.cache_path), url_to_fs(url))

    def read_from_cache(self, url):
        cache_file = self.cache_file_from_url(url)
        if not os.path.exists(cache_file):
            return None

        print(cache_file)
        with open(cache_file, 'r') as f:
            return json.load(f)

    def save_to_cache(self, url, data):
        cache_file = self.cache_file_from_url(url)
        if not os.path.exists(os.path.dirname(cache_file)):
            os.makedirs(os.path.dirname(cache_file))
        with open(cache_file, 'w') as f:
            json.dump(data, f, indent=2)

    def get_url(self, url, retries=3):
        print(url)
        r = requests.get(url)
        try:
            r.raise_for_status()
        except:
            if retries <= 0:
                raise
            print("Retrying {}".format(url))
            time.sleep(30)
            return self.get_url(url, retries=retries-1)
        return r

    def get_object(self, url, cache=True):
        '''
        Retrieve a url. If it is cached, serve from cache. If not, save to cache
        '''

        result = self.read_from_cache(url)
        if result is not None:
            return result

        result = self.get_url(url).json()
        self.save_to_cache(url, result)

        return result

    def get_objects(self, url):
        '''
        Retrieve all objects

        Expects a url with 'count', 'next', 'results' fields.
        '''
        r = self.get_url(url)
        for obj in r.json()['results']:
            yield self.get_object(obj['url'])
        if r.json()['next'] is not None:
            yield from self.get_objects(r.json()['next'])

    def get_leaf_objects(self, url):
        '''
        Retrieve objects which are paged and collapse into a single list.
        '''

        result = self.read_from_cache(url)
        if result is not None:
            return result

        results = []
        r = self.get_url(url)
        for obj in r.json()['results']:
            results.append(obj)
        while r.json()['next'] is not None:
            r = self.get_url(r.json()['next'])
            for obj in r.json()['results']:
                results.append(obj)

        self.save_to_cache(url, results)
        return results


if __name__ == '__main__':
    client = qareports(cache_path)
    for project, project_number in projects.items():
        result = client.get_object(urljoiner(squad, api, 'projects', project_number))
        for build in client.get_objects(result['builds']):
            if not build.get('finished', False):
                continue
            status = client.get_object(build['status'])
            metadata = client.get_object(build['metadata'])
            for testrun in client.get_objects(build['testruns']):
                # We could capture the _files too, but they're not json
                # so we'd need to modify get_object to handle non-json.
                #tests_file = client.get_object(testrun['tests_file'])
                #metrics_file = client.get_object(testrun['metrics_file'])
                #log_file = client.get_object(testrun['log_file'])
                tests = client.get_leaf_objects(testrun['tests'])
                metrics = client.get_leaf_objects(testrun['metrics'])
            for testjob in client.get_objects(build['testjobs']):
                pass

