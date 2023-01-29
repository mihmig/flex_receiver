import geopy.distance

coords_1 = (57.695241, 39.791827)
coords_2 = (57.602581, 39.576598)
print(geopy.distance.geodesic(coords_1, coords_2).m)