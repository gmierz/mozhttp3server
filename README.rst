==========
HTTP 3 app
==========

The HTTP/3 app supports HTTP/2 and HTTP/3

To run the app, build its docker image::

    $ make docker-build

Then run it::

    $ make docker-run

Run it in the background::

    $ make docker-run-background

Verify the H/3 server with the provided client script::

    $ make verify
