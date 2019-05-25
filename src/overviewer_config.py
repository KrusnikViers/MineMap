from observer import JSObserver


worlds["default"] = "/build/world"
texturepath = "/build/client.jar"


def poi_filter(poi):
    if (poi['id'] == 'Sign' or poi['id'] == 'minecraft:sign') and '-<!>-' in poi['Text4']:
        return "\n".join([poi['Text1'], poi['Text2'], poi['Text3']])

renders["day"] = {
    "world": "default",
    "title": "Overworld",
    "rendermode": "smooth_lighting",
    "dimension": "overworld",
    "northdirection": "upper-right",
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
