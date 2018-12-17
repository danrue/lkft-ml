#!/bin/sh -e

known_issue_files="kselftests-production.yaml ltp-production.yaml libhugetlbfs-production.yaml"
for f in $known_issue_files; do
    wget -O $f https://raw.githubusercontent.com/Linaro/qa-reports-known-issues/master/${f}
done
./parse_known_issues.py -c $known_issue_files > needle_intermittent_issues.json
rm -f $known_issue_files

