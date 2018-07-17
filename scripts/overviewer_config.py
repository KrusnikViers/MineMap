worlds["Current"] = "/minemap/rendering/world"
texturepath = "/minemap/rendering/client.jar"

renders["day"] = {
    "world": "Current",
    "title": "Day",
    "rendermode": smooth_lighting,
    "dimension": "overworld",
    "northdirection": "upper-right",
}
renders["night"] = {
    "world": "Current",
    "title": "Night",
    "rendermode": smooth_night,
    "dimension": "overworld",
    "northdirection": "upper-right",
}
renders["survivalnether"] = {
    "world": "Current",
    "title": "Nether",
    "rendermode": nether_smooth_lighting,
    "dimension": "nether",
    "northdirection": "upper-right",
}

outputdir = "/minemap/rendering/public"
