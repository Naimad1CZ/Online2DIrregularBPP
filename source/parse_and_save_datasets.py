import pandas as pd
import json
import math

from generator_placer_base import ShapeGenerator
from shape_generators import SG1, SG2, SG3, SG4, SG5, SG6, SG7

from shapely.geometry import Polygon

from xml.dom import minidom
from svg.path import parse_path
from svg.path.path import Line
from dxfwrite import DXFEngine as dxf


def norm_data(poly, num):
    for ver in poly:
        ver[0] = round(ver[0] * num, 10)
        ver[1] = round(ver[1] * num, 10)


def translate_poly(poly, x, y):
    for i in range(len(poly)):
        poly[i][0] += x
        poly[i][1] += y


def get_polygons_from_generators(generator: ShapeGenerator, number_of_shapes):
    return generator._get_first_n_shapes(number_of_shapes)


def parse_polygons_from_seanys_csv(filename: str, scale):
    dataset = pd.read_csv(filename + ".csv")
    polygons = []
    for i in range(0, dataset.shape[0]):
        for j in range(0, dataset['num'][i]):
            poly = json.loads(dataset['polygon'][i])
            norm_data(poly, scale)
            poly.append(poly[0].copy())
            polygons.append(poly)
    return polygons


def create_polygons_real_svg(filename, polygons):
    with open('../datasets/' + 'DeepNest_' + filename + '.svg', 'w') as f:
        print('''<?xml version="1.0" encoding="utf-8"?>
<!-- Generator: Adobe Illustrator 15.1.0, SVG Export Plug-In . SVG Version: 6.00 Build 0)  -->
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px" width="50000px"
	 height="50000px" viewBox="0 0 50000 50000" xml:space="preserve">
<g id="Grid" display="none">
</g>
<g id="Layer_1">
</g>
<g id="Desktop">
</g>
<g id="Guides">
</g>
<g id="Page_1">
	<g id="Layer_1_1_">
	''', file=f)

        for i in range(len(polygons)):
            poly = polygons[i]
            print('poly is:', poly)
            print('          ', end='')
            print('<polygon fill="none" stroke="#231F20" stroke-width="0.001" points="', end='', file=f)
            for j in range(len(poly) - 2):
                print('{0},{1} '.format(poly[j][0] + 1000 * ((i + 1) % 49), poly[j][1] + 1000 * ((i // 49) + 1)), end='', file=f)
                print(poly[j], end='')
            print('{0},{1}'.format(poly[len(poly) - 2][0] + 1000 * ((i + 1) % 49), poly[len(poly) - 2][1] + 1000 * ((i // 49) + 1)), end='', file=f)
            print(poly[len(poly) - 2])
            print('" />', file=f)

        print('''    </g>
</g>
</svg>
''', file=f)

    print('ahoj')


def print_polygons_csv2(filename, polygons):
    with open('../datasets/' + filename + '.csv', 'w') as f:
        print('num,polygon', file=f)
        for i in range(len(polygons)):
            print('1,"[', end='', file=f)
            poly = polygons[i]
            #for k in range(len(poly)):
            #    poly[k] = (poly[k][0] + 100, poly[k][1] + 100)

            for j in range(len(poly) - 1):
                print('[' + str(round(poly[j][0], 6)) + ', ' + str(round(poly[j][1], 6)) + '], ', end='', file=f)
            print('[' + str(round(poly[len(poly) - 1][0], 6)) + ', ' + str(round(poly[len(poly) - 1][1], 6)) + ']]"', file=f)


def create_dataset_from_SG():
    filename = 'SG7'
    no_polygons = 330
    scale_factor = 5
    gen = SG7()

    polys = get_polygons_from_generators(gen, no_polygons)
    polys = [[[x[0], x[1]] for x in pol] for pol in polys]
    for p in polys:
        print('p', p)
        norm_data(p, scale_factor)
        print('q', p)
    print_polygons_csv2(filename, polys)

def create_sorted_dataset(filename):
    items = parse_polygons_from_seanys_csv('../datasets/' + filename, 1)
    polys = [Polygon(i) for i in items]
    polys.sort(key=lambda x: x.area, reverse=True)
    for p in polys:
        print(p.area)

    polygons = [p.exterior.coords for p in polys]

    print_polygons_csv2('sorted/' + filename + '_sorted', polygons)

def calculate_deepnest_area_ratio(filename, scaled_width, scaled_heigth):
    doc = minidom.parse('../datasets/' + filename)
    coords = [path.getAttribute('points') for path in doc.getElementsByTagName('polygon')]
    doc.unlink()
    float_coords = []
    for p in coords:
        print(p)
        res = []
        tokens = p.split()
        for i in range(len(tokens)):
            if i % 2 == 1:
                res.append((float(tokens[i-1]), float(tokens[i])))
        float_coords.append(res)

    polygons = []
    area = 0

    for f in float_coords:
        print(f)
        pol = Polygon(f)
        polygons.append(pol)
        area += pol.area
        print('ar', area)

    print('total:', len(float_coords))

    real_contianer_area = scaled_width * scaled_heigth
    res_area = real_contianer_area * 0.5453697211 * (3.24 / math.pi)
    print(res_area)
    ratio = area / res_area
    print('ratio', ratio)


def calculate_area_from_packaide_svg(filename, scaled_width, scaled_heigth):
    doc = minidom.parse('../datasets/' + filename)
    path_strings = [path.getAttribute('d') for path
                    in doc.getElementsByTagName('path')]
    doc.unlink()

    polygons = []
    area = 0
    # print the line draw commands
    for path_string in path_strings:
        path = parse_path(path_string)
        poly = []
        first = path[0]
        poly.append([first.start.real, first.start.imag])
        for i in range(1, len(path)):
            if isinstance(path[i], Line):
                x1 = path[i].end.real
                y1 = path[i].end.imag
                poly.append([x1, y1])
        pol = Polygon(poly)
        polygons.append(pol)
        area += pol.area

    print('total:', len(polygons))

    real_contianer_area = scaled_width * scaled_heigth
    res_area = real_contianer_area
    print(area)
    print(res_area)
    ratio = area / res_area
    print('ratio', ratio)


def create_dxf(filename, polygons):
    drawing = dxf.drawing("../datasets/" + filename + ".dxf")
    for i in range(len(polygons)):
        translate_poly(polygons[i], 1000 * ((i + 1) % 49), 1000 * ((i // 49) + 1))

        drawing.add(dxf.polyline(points=polygons[i]))
    drawing.save()


def print_polygons_svg_for_packaide(polygons):
    for i in range(len(polygons)):
        print('<polygon points="', end='')
        for j in range(len(polygons[i]) - 2):
            #print('{0},{1} '.format(polygons[i][j][0], polygons[i][j][1]), end='')
            print('{0},{1} '.format(polygons[i][j][0] + 1000 * ((i + 1) % 49), polygons[i][j][1] + 1000 * ((i // 49) + 1)), end='')
        #print('{0},{1}'.format(polygons[i][len(polygons[i]) - 2][0], polygons[i][len(polygons[i]) - 2][1]), end='')
        print('{0},{1}'.format(polygons[i][len(polygons[i]) - 2][0] + 1000 * ((i + 1) % 49), polygons[i][len(polygons[i]) - 2][1] + 1000 * ((i // 49) + 1)), end='')
        print('" />')


def print_polygons_Svanda(polygons):
    for p in polygons:
        pol = [(x[0], x[1]) for x in p]
        print("[" + str(pol[:]) + "]")


def print_Dalsoo(polygons):
    for i in range(len(polygons)):
        print('protos[' + str(i) + '] = new double[][] { ', end='')
        poly = polygons[i]
        for k in range(len(poly)):
            poly[k] = (poly[k][0], poly[k][1])

        for j in range(len(poly) - 2):
            print('{', round(poly[j][0], 4), ',', round(poly[j][1], 4), '}, ', end='')
        print('{', round(poly[len(poly) - 2][0], 4), ',', round(poly[len(poly) - 2][1], 4), '}', end='')
        print(' };')


if __name__ == "__main__":
    filename = 'SG6'
    sc_width = 900
    sc_height = 900

    scale = 10

    polys = parse_polygons_from_seanys_csv('../datasets/' + filename, scale)

    box = [[0, 0], [sc_width, 0], [sc_width, sc_height], [0, sc_height], [0, 0]]

    polys.append(box)
    create_polygons_real_svg(filename, polys)
