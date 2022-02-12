# Flask

## Overview

This apps uses [swagger-codegen](https://github.com/swagger-api/swagger-codegen) and the [Connexion](https://github.com/zalando/connexion) library on top of Flask.

## Requirements

- Make
- [Docker Compose](https://docs.docker.com/compose/install/)

## To set up the project:

Start by setting up the git pre commit hook that will run all the tests and format your code

```
make set-pre-commit
```

## Usage

To run the server, execute the following from the root directory:

```
make build-container # this will build our custom python container
make up
```

and open your browser here:

```
http://localhost:8080/v1/ui/
```

To launch the integration tests:

```
make test
```

To connect to the database instance:

```
make mysql
```

To generate a database migration (after execute the command, restart the container to run the migration):

```
make migrate Some explanation message
```

To merge database migrations (2 or more migrations generated in different branches have the same `down_revision`)

```
make merge-migrations Some explanation message
```

To install dependencies use:

```
make pip ${package}
```

To freeze the dependencies use:

```
make freeze
```

To regenerate the source code:

```
make swagger-gen
```

Add attributes to a response object:

```
# import the mutable_response function
# This will let you create MutableRespose
from swagger_server.formatter import mutable_response

response = mutable_response(auth_response)

# Now we can call the append method as many times as we want to append new data
response.append('key', 'value').append('test', 'test_value')

then we can just return this response as it was done with any other
```

## Documentation only

### Requirements

- [grip](https://github.com/joeyespo/grip)
- [pylint](https://pylint.org/)
- [graphviz](https://graphviz.org/)

To render locally the documentation markdown we use [grip](https://github.com/joeyespo/grip)

```
grip docs/4+1_architectural_view.md
```

To generate the class diagrams and the package diagram we use a tool called `pyreverse`.

This tool comes with the package [pylint](https://pylint.org/) and requires [graphviz](https://graphviz.org/)

```
pyreverse -o png -p cms-nft-minting swagger_server
```
