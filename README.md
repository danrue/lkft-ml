# Linux Kernel Functional Testing - Machine Learning

This repository is a proof-of-concept machine learning project for
[LFKT](https://lkft.linaro.org).

## Contents

First, the needle(s) and the haystack:
- haystack: Cache of historical test result data retrieved from
  [qa-reports](https://qa-reports.linaro.org/lkft).
- needle_intermittent_issues.json: A file of needles. In this case, tests that
  have manually been identified as intermittently failing (i.e. flaky) tests.

The other supporting scripts:
- get_data.py: Populate haystack. Also serves as a library for retrieving data
  from haystack or [qa-reports](https://qa-reports.linaro.org/lkft).
- find_intermittent_issues.py: Example naive approach to finding inconsistently
  failing tests (i.e. flaky tests).
- parse_known_issues.py: Used to populate needle_intermittent_issues.json
- update.sh: Generates needle_intermittent_issues.json, using
  parse_known_issues.py.

## Design

The concept behind this project is to provide the historical LKFT data in a way
that could be used to answer questions about the data, possibly using machine
learning. All of LKFT's data is available via [qa-report's
API](https://qa-reports.linaro.org/api/), but it is costly to retrieve all of
the data over the API. In this repository, get_data.py retrieves the useful
data from the API, and stores it in accessible json files in `haystack/`.

Note that the implementation is a tad sloppy (this is a first attempt): When
using get_data.py, some urls will be retrieved from qa-reports but most should
be retrieved from the `haystack/` cache. The implementation isn't very robust,
but it is hopefully straight forward (optimized for simplicity). A more
sophisticated approach would be to use a database dump directly, or use the API
more directly along with a more correct caching implementation.

## Problem

The Linaro team behind LKFT spends a lot of time sifting through noisy test
data trying to determine when regressions actually happen. However, because
tests are run on real, embedded hardware, in real labs run by actual humans,
the data is never good enough to rely on without heavy curation.

The goal of this project is to provide meaningful signal from the data in order
to be able to provide more automated reporting, find information that mere
humans are not able to deduce, and make the data more accessible more people.

Two initial problems have been identified.

The first is identifying 'bad' tests. A bad test is one whose results cannot be
trusted. Such tests, which may fail intermittently, cause noise in the data
that may detract from actual test regressions.

The second initial problem is identifying actual regressions in the data. A
regression is a test begins failing due to an actual problem in the linux
kernel. Often these can be seen first in next, followed by mainline, and then
often backported to a stable tree. While many regressions have been discovered,
reported, and fixed - the data most certainly contains additional regressions
that nobody has noticed.

## Examples

### Intermittent Issues

The needle_intermittent_issues.json file is a json representation of actual
intermittent known issues identified and maintained by the LKFT team. These
should all be considered actual intermittent issues, but there are other
intermittent issues that are not listed in the file. Often a test has to be
quite noisy before a human bothers to add it as a known intermittent issue.

This needle file is generated using parse_known_issues.py, which retrieves the
lists of known intermittent issues from
(qa-reports-known-issues)[https://github.com/Linaro/qa-reports-known-issues].
It could also retrieve them from the qa-reports API, but this author did not
think of that at the time.

Finally, find_intermittent_issues.py is a very naive example us traversing
through the haystack to try to discover intermittent failures using hard coded
thresholds. For example, it looks at the 10 most recent builds and if any test
has changed state (from good to bad or bad to good) more than <threshold>
times, it will be reported an intermittent issue.
