# digitalmarketplace-search-api
API to handle interactions between the digitalmarketplace applications and search.

- Python app, based on the [Flask framework](http://flask.pocoo.org/)

## Quickstart

Install [elasticsearch](http://www.elasticsearch.org/). This must be in the 5.x series; ideally 5.4 which is what we run on live systems.
```
brew cask install java
cd /usr/local/Homebrew/Library/Taps/homebrew/homebrew-core
git fetch --unshallow
git checkout d8c57e111f1990c0a33b0d73af818eb8d442b33b Formula/elasticsearch.rb # (version: 5.4.2)
HOMEBREW_NO_AUTO_UPDATE=1 brew install elasticsearch
git reset --hard master
```

Install [Virtualenv](https://virtualenv.pypa.io/en/latest/)
```
sudo easy_install virtualenv
```

Install dependencies and run the app
```
make run-all
```

## Setup

Install [elasticsearch](http://www.elasticsearch.org/). This must be in the 5.x series; ideally 5.4 which is what we run on live systems.

```
brew update
brew install homebrew/versions/elasticsearch
```

Install [Virtualenv](https://virtualenv.pypa.io/en/latest/)

```
sudo easy_install virtualenv
```

Create a virtual environment in the checked-out repository folder

```
make virtualenv
```

### Activate the virtual environment

```
source ./venv/bin/activate
```

### Upgrade dependencies

Install Python dependencies with pip

```
make requirements-dev
```

### Run the tests

```
make test
```

### Run the development server

To run the Search API for local development you can use the convenient run
script, which sets the required environment variables for local development:
```
make run-app
```

More generally, the command to start the server is:
```
python application.py runserver
```

### Using the Search API locally

Start elasticsearch if not already running via brew (in a new console window/tab):

```bash
brew services start elasticsearch
< OR >
elasticsearch
```

The Search API runs on port 5001. Calls to the Search API require a valid bearer
token. For development environments, this defaults to `myToken`. An example request to your local search API
would therefore be:

```
curl -i -H "Authorization: Bearer myToken" 127.0.0.1:5001/g-cloud/services/search?q=email
```

### Updating application dependencies

`requirements.txt` file is generated from the `requirements-app.txt` in order to pin
versions of all nested dependecies. If `requirements-app.txt` has been changed (or
we want to update the unpinned nested dependencies) `requirements.txt` should be
regenerated with

```
make freeze-requirements
```

`requirements.txt` should be commited alongside `requirements-app.txt` changes.

### Using FeatureFlags

To use feature flags, check out the documentation in (the README of)
[digitalmarketplace-utils](https://github.com/alphagov/digitalmarketplace-utils#using-featureflags).

### Updating the index mapping

Whenever the mappings JSON file is updated, a new version value should be written to the mapping
metadata in `"_meta": {"version": VALUE}`.

Mapping can be updated by issuing a PUT request to the existing index enpoint:

```
PUT /g-cloud-index HTTP/1.1
Authorization: Bearer myToken
Content-Type: application/json

{"type": "index"}
```

If the mapping cannot be updated in-place, [zero-downtime mapping update process](https://www.elastic.co/blog/changing-mapping-with-zero-downtime) should be used instead:

1. Create a new index, using the `index-name-YYYY-MM-DD` pattern for the new index name.
   ```
   PUT /g-cloud-2015-09-29 HTTP/1.1
   Authorization: Bearer myToken
   Content-Type: application/json

   {"type": "index"}
   ```
2. Reindex documents into the new index using existing index document endpoints with the new index name
3. Once the indexing is finished, update the index alias to point to the new index:
   ```
   PUT /g-cloud HTTP/1.1
   Authorization: Bearer myToken
   Content-Type: application/json

   {"type": "alias", "target": "g-cloud-2015-09-29"}
   ```

4. Once the alias is updated the old index can be removed:
   ```
   DELETE /g-cloud-index HTTP/1.1
   Authorization: Bearer myToken
   ```
