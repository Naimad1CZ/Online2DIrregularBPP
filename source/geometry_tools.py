from operator import itemgetter

from nfp_interface.libnfporb_interface import genNFP
from nfp_interface.libnfporb_interface import genIFP
from drawing import show_in_pyplot

from shapely.geometry import Polygon, LineString, LinearRing, Point, MultiPolygon
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
from shapely.ops import substring
import shapely.affinity as affinity

import random
import math
import time


# those variables should be set in DamiansPlacer.run
DEBUG = True
EPSILON = 0.000000000001
translate_number = 11


def log(*s):
    if DEBUG:
        print(*s)


def cord(poly):
    return list(poly.exterior.coords)


def rotate_around_first_point(p: Polygon, angle: int):
    return affinity.rotate(p, angle, origin=p.exterior.coords[0])


def regular_polygon(radius, n):
    one_segment = math.pi * 2 / n

    points = [
        (math.sin(one_segment * (i + 0.5)) * radius,
         math.cos(one_segment * (i + 0.5)) * radius)
        for i in range(n)]
    return Polygon(points)


def translate_where_point_has_x_y(sh, point, x, y):
    translation_x = x - point[0]
    translation_y = y - point[1]
    return affinity.translate(sh, translation_x, translation_y)


def get_basic_geometry_coords(geometry):
    coords = []
    g_type = type(geometry)
    if g_type is Point or g_type is LineString or g_type is LinearRing:
        coords.append(list(geometry.coords))
    elif g_type is Polygon:
        coords.append(list(geometry.exterior.coords))
        for hole in geometry.interiors:
            coords.append(list(hole.coords))
    else:
        print('alaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaarm in basic_geometry_coords')
        log(geometry)

    return coords


def get_geometry_points(geometry):
    coords = []
    g_type = type(geometry)
    if g_type is Polygon or g_type is Point or g_type is LineString or g_type is LinearRing:
        coords = get_basic_geometry_coords(geometry)
    else:
        for simple_geometry in geometry:
            coords.extend(get_basic_geometry_coords(simple_geometry))
    return coords


def shuffle_and_translate_coords_by_epsilon(coords, translation_amount, shuffle):
    new_coords = []
    for c in coords:
        if shuffle:
            rand1 = random.random() - 0.5
            rand1 = rand1 * 100 * EPSILON
            rand2 = random.random() - 0.5
            rand2 = rand2 * 100 * EPSILON
            new_coords.append((round(c[0] + translation_amount, 10) + rand1, round(c[1] + translation_amount, 10) + rand2))
        else:
            new_coords.append((round(c[0] + translation_amount, 10), round(c[1] + translation_amount, 10)))
    return new_coords


def compute_IPF_return_geometry(container: Polygon, polygon: Polygon):
    # log('start IPF')

    cont = orient(container, -1.0)
    pol = orient(polygon, 1.0)

    cont2 = affinity.translate(cont, translate_number, translate_number)
    pol2 = affinity.translate(pol, translate_number, translate_number)

    cont_coords = cord(cont2)
    pol_coords = cord(pol2)
    ifps = genIFP(cont_coords, pol_coords)

    # some case with rectangle container
    if len(ifps) == 0:
        if len(cont_coords) == 5:
            if cont_coords[0][0] == cont_coords[1][0] and cont_coords[2][0] == cont_coords[3][0] and cont_coords[0][1] == cont_coords[3][1] and cont_coords[1][1] == cont_coords[2][1]:
                max_x = max(pol_coords, key=itemgetter(0))[0]
                min_x = min(pol_coords, key=itemgetter(0))[0]
                max_y = max(pol_coords, key=itemgetter(1))[1]
                min_y = min(pol_coords, key=itemgetter(1))[1]
                max_x_diff = max_x - pol_coords[0][0]
                min_x_diff = pol_coords[0][0] - min_x
                max_y_diff = max_y - pol_coords[0][1]
                min_y_diff = pol_coords[0][1] - min_y
                result = [(cont_coords[0][0] + min_x_diff, cont_coords[0][1] + min_y_diff),
                          (cont_coords[1][0] + min_x_diff, cont_coords[1][1] - max_y_diff),
                          (cont_coords[2][0] - max_x_diff, cont_coords[2][1] - max_y_diff),
                          (cont_coords[3][0] - max_x_diff, cont_coords[3][1] + min_y_diff)]
                ifps.append(result)


    ifps_translated_back = [[(point[0] - translate_number, point[1] - translate_number) for point in geometry] for geometry in ifps]


    polys = [Polygon(x) for x in ifps_translated_back if len(x) > 2]
    lines = [LineString(x) if len(x) > 1 else Point(x) for x in ifps_translated_back if len(x) < 3]

    polys.extend(lines)
    res = unary_union(polys)
    return res


def compute_NPF(around_shape: Polygon, polygon: Polygon):
    cont = orient(around_shape, 1.0)
    pol = orient(polygon, 1.0)

    cont2 = affinity.translate(cont, translate_number, translate_number)
    pol2 = affinity.translate(pol, translate_number, translate_number)

    cont_coords = cord(cont2)
    pol_coords = cord(pol2)

    try_count = 0
    nfp = None

    while nfp is None:
        try:
            nfp = genNFP(cont_coords, pol_coords)
        except:
            if try_count > 2:
                log('exception in NFP :(', try_count)

            pol_coords = shuffle_and_translate_coords_by_epsilon(pol_coords, 24.3813317, try_count > 1)
            try_count += 1
        if try_count > 20:
            return -1

    nfps_translated_back = [[(point[0] - translate_number, point[1] - translate_number) for point in geometry] for geometry in nfp]

    polys = [Polygon(x) for x in nfps_translated_back if len(x) > 2]
    lines = [LineString(x) if len(x) > 1 else Point(x) for x in nfps_translated_back if len(x) < 3]

    polys.extend(lines)
    for i in range(len(polys)):
        if not polys[i].is_valid:
            print('ooooh!')
            polys[i] = polys[i].convex_hull
    res = unary_union(polys)

    # shrink around_shape a little bit so the unary_union of NFPs can contain degenerated cases
    res = res.buffer(-120 * EPSILON, 1, join_style=2)

    return res


IFP_time = 0
NFP_time = 0
NFP_unary_union_time = 0
difference_time = 0
get_geom_points_time = 0


def get_CFR_candidate_points(container, already_placed_shapes, shape, CFR_mode):
    start = time.time()

    ifp = compute_IPF_return_geometry(container, shape)

    end = time.time()
    global IFP_time
    IFP_time += end - start
    start = time.time()

    nfps = []

    for s in already_placed_shapes:
        nfp = compute_NPF(s, shape)
        if nfp != -1:
            nfps.append(nfp)

    end = time.time()
    global NFP_time
    NFP_time += end - start
    start = time.time()

    nfp_merged = unary_union(nfps)

    # buffer it a little because individual NFPs were shrinked (this value is because others may cause some other numerical instability or something)
    nfp_merged = nfp_merged.buffer(105 * EPSILON, 1, join_style=2)

    end = time.time()
    global NFP_unary_union_time
    NFP_unary_union_time += end - start
    start = time.time()

    if not nfp_merged.is_valid:
        print('------------------')
        print('alaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaarm!!!!!!!!!!!!!!!!')
        show_in_pyplot([nfp_merged], radius=15, last_polygon=shape, dpi=1000, save=True, really_ret=False)
        log(nfp_merged)

        nfp_merged = MultiPolygon([pol for pol in nfp_merged if pol.area > 0.001])
        log(nfp_merged)
        print('after removing small parts - is valid?', nfp_merged.is_valid)
        show_in_pyplot([nfp_merged], radius=15, dpi=1000, save=True, really_ret=False)
        log('------------------')

        if not nfp_merged.is_valid:
            nfp_merged = nfp_merged.convex_hull
            log(nfp_merged)
            print('after convex hull - is valid?', nfp_merged.is_valid)
            show_in_pyplot([nfp_merged], radius=15, last_polygon=shape, dpi=1000, save=True, really_ret=False)
            log('------------------')

    if len(nfps) == 0:
        collision_free_area = ifp
    else:
        collision_free_area = ifp.difference(nfp_merged)

    end = time.time()
    global difference_time
    difference_time += end - start
    start = time.time()

    lists = get_geometry_points(collision_free_area)
    lists = [x for x in lists if len(x) > 0]

    end = time.time()
    global get_geom_points_time
    get_geom_points_time += end - start

    # CFR_mode 0 - normal
    # CFR_mode 1 - reduce - remove vertices that aren't in the convex hull of individual regions of CRFs
    # CFR_mode 2 - extend - pick all vertices of CFRs and add points on edges of CFRs
    if CFR_mode == 1:
        reduced = []
        log('lists length:', len(lists))
        for l in lists:
            try:
                log('llen', len(l))
                p = Polygon(l)
                red = list(orient(p.convex_hull, 1.0).exterior.coords)
                red = [r for r in red if r in l]
                log('rlen', len(red))
                reduced.append(red)
            except:
                log('huuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuu')
                reduced.append(l)
        log('afterward lists length:', len(lists))
        lists = reduced

    elif CFR_mode == 2:
        if len(lists) > 0:
            longest_edge_length = 0
            edge_count = 0
            total_edge_length = 0
            for l in lists:
                edge_count += len(l) - 1
                for i in range(len(l) - 1):
                    length = math.sqrt((l[i][0] - l[i + 1][0]) * (l[i][0] - l[i + 1][0]) + (l[i][1] - l[i + 1][1]) * (l[i][1] - l[i + 1][1]))
                    edge_count += 1
                    total_edge_length += length
                    if length > longest_edge_length:
                        longest_edge_length = length
            avg_edge_length_over_3 = (total_edge_length / edge_count) / 3
            res = []
            for l in lists:
                tmp = []
                for i in range(len(l) - 1):
                    length = math.sqrt((l[i][0] - l[i + 1][0]) * (l[i][0] - l[i + 1][0]) + (l[i][1] - l[i + 1][1]) * (l[i][1] - l[i + 1][1]))
                    segment = LineString([(l[i][0], l[i][1]), (l[i + 1][0], l[i + 1][1])])
                    no_points = max(int(length // avg_edge_length_over_3), 1)
                    for j in range(no_points):
                        point = substring(segment, j / no_points, j / no_points, normalized=True)
                        point_coords = list(point.coords)[0]
                        tmp.append(point_coords)
                res.append(tmp)
            lists = res

    areas = []
    for i in range(len(lists)):
        try:
            pol = Polygon(lists[i])
            areas.append(pol.area)
        except:
            # it's line or point
            areas.append(0)

    # remove duplicate candidates
    for i in range(len(lists)):
        if lists[i][0] == lists[i][-1]:
            lists[i] = lists[i][:-1]

    candidates = create_candidates_from_points(lists, shape)

    return candidates, lists, areas


def create_candidates_from_points(lists, shape):
    shape_start = shape.exterior.coords[0]
    candidates = [[translate_where_point_has_x_y(shape, shape_start, p[0], p[1]) for p in sh] for sh in lists]

    return candidates
