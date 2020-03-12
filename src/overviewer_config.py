from .observer import JSObserver

worlds["default"] = "/build/world"
texturepath = "/build/client.jar"


def poi_filter(poi):
    allowed_icons = [
        'anvil',
        'anvil_red',
        'factory',
        'factory_red',
        'hoe',
        'hoe_red',
        'mine',
        'mine_red',
        'ship',
        'ship_red',
        'tower',
        'tower_red',
        'town',
        'town_red',
    ]
    if (poi['id'] == 'Sign' or poi['id'] == 'minecraft:sign') and \
            poi['Text4'].startswith('-<') and poi['Text4'].endswith('>-'):
        marker_icon = poi['Text4'][2:-2]
        if marker_icon in allowed_icons:
            poi['icon'] = 'icons/marker_{}.png'.format(marker_icon)
            return " ".join([poi['Text1'], poi['Text2'], poi['Text3']])


renders["day-SE"] = {
    "world": "default south-east",
    "title": "Overworld",
    "rendermode": "smooth_lighting",
    "dimension": "overworld",
    "northdirection": "upper-right",
    "markers": [dict(name="Manual", filterFunction=poi_filter)],
}

renders["day-NE"] = {
    "world": "default north-east",
    "title": "Overworld",
    "rendermode": "smooth_lighting",
    "dimension": "overworld",
    "northdirection": "lower-right",
    "markers": [dict(name="Manual", filterFunction=poi_filter)],
}

renders["day-NW"] = {
    "world": "default north-west",
    "title": "Overworld",
    "rendermode": "smooth_lighting",
    "dimension": "overworld",
    "northdirection": "lower-left",
    "markers": [dict(name="Manual", filterFunction=poi_filter)],
}

renders["day-SW"] = {
    "world": "default south-west",
    "title": "Overworld",
    "rendermode": "smooth_lighting",
    "dimension": "overworld",
    "northdirection": "upper-left",
    "markers": [dict(name="Manual", filterFunction=poi_filter)],
}

renders["nether"] = {
    "world": "default",
    "title": "Nether",
    "rendermode": [Base(), EdgeLines(), Nether(), SmoothLighting(strength=0.4)],
    "dimension": "nether",
    "northdirection": "upper-right",
    "markers": [dict(name="Manual", filterFunction=poi_filter)],
}

renders["end"] = {
    "world": "default",
    "title": "The End",
    "rendermode": [Base(), EdgeLines(), SmoothLighting(strength=0.5)],
    "dimension": "end",
    "northdirection": "upper-right",
    "markers": [dict(name="Manual", filterFunction=poi_filter)],
}

outputdir = "/public"

observer = JSObserver(outputdir, 30, {'totalTiles': 'Rendering %d tiles...',
                                      'renderCompleted': 'Rendered in %02d:%02d:%02d',
                                      'renderProgress': 'Rendering %d of %d tiles (%d%%, ~%s left)'})
