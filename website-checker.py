import hashlib
import json
import os
import re
import time
from urllib.request import urlopen
from urllib.parse import urlparse
import argparse


REGEX_FOR_URL = re.compile(
    r'^(?:http|ftp)s?://' # http:// or https://
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
    r'localhost|' #localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
    r'(?::\d+)?' # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE
)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("url", nargs='+', help="List of url to analyse. Wrong urls will be ignored.")
    args = parser.parse_args()
    valid_urls = [an_url for an_url in args.url if all([getattr(urlparse(an_url), qualifying_attr) for qualifying_attr in ('scheme', 'netloc')])]

    print(f"Kept valid urls : {valid_urls}")
    # reading the changes DB in order to take them in account if we already scanned the url.
    with open(os.path.join(os.path.dirname(__file__), "output", "changes_db.json"), "r") as readable:
        changes = json.load(readable)

    for url in valid_urls:
        # request url
        content = urlopen(url=url).read()

        md5_res = hashlib.md5(content)
        sha256_res = hashlib.sha256(content)
        current_time = time.time()
        # so the format inside the json is {url->{_time->(md5,sha256)}}
        if url not in changes:
            changes[url] = {}

        #changes[url].append(current_time)
        changes[url][current_time] = {"md5": md5_res.hexdigest(), "sha256": sha256_res.hexdigest()}

    # writing the data back in the file
    with open(os.path.join(os.path.dirname(__file__), "output", "changes_db.json"), "w+") as open_file:
        changes = json.dump(changes, open_file, indent=4)
