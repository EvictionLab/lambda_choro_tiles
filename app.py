from flask import Flask, send_file
from flask import make_response
from io import BytesIO
from PIL import Image
import requests
import mapbox_vector_tile
from shapely.geometry import shape, MultiPolygon

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
from matplotlib.colors import Normalize
from palettable.colorbrewer.sequential import YlGnBu_9
from descartes import PolygonPatch


app = Flask(__name__)

BASE_S3_URL = 'https://s3.us-east-2.amazonaws.com/eviction-lab-tilesets/fake'


@app.route('/<tiles>/<int:z>/<int:x>/<int:y>.png')
def serve_tile(tiles, z, x, y):
    res = requests.get('{}/{}/{}/{}/{}.pbf'.format(BASE_S3_URL, tiles, z, x, y))
    vector_data = mapbox_vector_tile.decode(res.content)
    mp = MultiPolygon(
        [shape(f['geometry']) for f in vector_data['cities']['features']]
    )
    # TODO: Make the data property a parameter
    data_vals = [f['properties']['population-2010'] for f in vector_data['cities']['features']]
    cmap = YlGnBu_9.mpl_colormap
    norm = Normalize(vmin=min(data_vals), vmax=max(data_vals))

    patches = []
    for idx, p in enumerate(mp):
        data = vector_data['cities']['features'][idx]['properties']['population-2010']
        if isinstance(data, str):
            color = '#000000'
        else:
            color = cmap(norm(data))
        patches.append(PolygonPatch(
            p, fc=color, ec='#555555', alpha=1., zorder=1, linewidth=0)
        )

    fig = plt.figure()
    ax = fig.add_subplot(111)
    # Setting bounds based on vector tile coordinates
    ax.set_xlim(0, 4096)
    ax.set_ylim(0, 4096)
    ax.set_aspect(1)

    ax.add_collection(PatchCollection(patches, match_original=True))
    ax.set_xticks([])
    ax.set_yticks([])
    ax.axis('off')

    buf = BytesIO()
    # TODO: Remove slight border edge, in here or with cropping
    plt.savefig(
        buf, bbox_inches='tight', pad_inches=0, transparent=True, dpi=450, format='png'
    )
    buf.seek(0)
    size = 256, 256

    im = Image.open(buf)
    im.thumbnail(size)

    im_buf = BytesIO()
    im.save(im_buf, 'PNG')

    response = make_response(im_buf.getvalue())
    response.headers['Content-Type'] = 'image/png'
    return response


if __name__ == '__main__':
    app.run()
