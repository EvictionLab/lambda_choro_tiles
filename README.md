# Lambda Choropleth Tileserver

Bare-bones implementation of creating choropleth raster tiles fom existing vector tiles.
This will be extremely slow compared to traditional sources of hosting raster tiles, and in
our case is intended for generating choropleth images of a map primarily using vector tiles.

## Setup

Create a `virtualenv` with Python 2.7, activate it, and then run `pip install -r requirements.txt`.
Deploy with `zappa deploy dev`.