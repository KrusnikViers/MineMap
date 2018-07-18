worlds["Realm"] = "/build/world"
texturepath = "/build/client.jar"


def poi_filter(poi):
    if poi['id'] == 'Sign' and poi['Text4'] == '-<!>-':
        return "\n".join(map(escape, [poi['Text1'], poi['Text2'], poi['Text3']]))

renders["Day"] = {
    "world": "Realm",
    "title": "Day",
    "rendermode": smooth_lighting,
    "dimension": "overworld",
    "northdirection": "upper-right",
    "markers": [dict(name="Manual", filterFunction=poi_filter)],
}
# renders["Night"] = {
#     "world": "Realm",
#     "title": "Night",
#     "rendermode": smooth_night,
#     "dimension": "overworld",
#     "northdirection": "upper-right",
# }
# renders["Biomes"] = {
#     "world": "Realm",
#     "title": "Biomes",
#     "rendermode": [BiomeOverlay()],
#     "overlay": ["Day"],
#     "northdirection": "upper-right",
# }
# renders["Nether"] = {
#     "world": "Realm",
#     "title": "Nether",
#     "rendermode": nether_smooth_lighting,
#     "dimension": "nether",
#     "northdirection": "upper-right",
# }

outputdir = "/build/public"
