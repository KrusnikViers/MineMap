worlds["default"] = "/rendering/world"
texturepath = "/bin/client.jar"

renders["day"] = {
    "world": "default",
    "title": "Day",
    "rendermode": smooth_lighting,
    "dimension": "overworld",
    "northdirection": "upper-right",
    "defaultzoom": "2"
}
renders["night"] = {
    "world": "default",
    "title": "Night",
    "rendermode": smooth_night,
    "dimension": "overworld",
    "northdirection": "upper-right",
    "defaultzoom": "2"
}
renders["survivalnether"] = {
    "world": "default",
    "title": "Nether",
    "rendermode": nether_smooth_lighting,
    "dimension": "nether",
    "northdirection": "upper-right",
    "defaultzoom": "2"
}

outputdir = "/rendering/new_version"
