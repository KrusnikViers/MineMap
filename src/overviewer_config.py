worlds["default"] = "/build/world"
texturepath = "/build/client.jar"

renders["day"] = {
    "world": "default",
    "title": "Day",
    "rendermode": smooth_lighting,
    "dimension": "overworld",
    "northdirection": "upper-right",
}
renders["night"] = {
    "world": "default",
    "title": "Night",
    "rendermode": smooth_night,
    "dimension": "overworld",
    "northdirection": "upper-right",
}
renders["biomes"] = {
    "world": "default",
    "title": "Biomes",
    "rendermode": [BiomeOverlay()],
    "dimension": "overworld",
    "overlay": ["day"],
    "northdirection": "upper-right",
}
renders["nether"] = {
    "world": "default",
    "title": "Nether",
    "rendermode": nether_smooth_lighting,
    "dimension": "nether",
    "northdirection": "upper-right",
}

outputdir = "/build/public"
