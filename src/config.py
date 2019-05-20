worlds["default"] = "/build/world"
texturepath = "/build/client.jar"


def poi_filter(poi):
    if poi['id'] == 'Sign' and poi['Text4'] == '-<!>-':
        return "\n".join(map(escape, [poi['Text1'], poi['Text2'], poi['Text3']]))

renders["day"] = {
    "world": "default",
    "title": "Day",
    "rendermode": smooth_lighting,
    "dimension": "overworld",
    "northdirection": "upper-right",
    "markers": [dict(name="Manual", filterFunction=poi_filter)],
}
# TODO(Viers): Add more renders.

outputdir = "/public"
