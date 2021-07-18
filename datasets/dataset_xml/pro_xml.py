from xml.etree import ElementTree as ET
import xml.dom.minidom
from dxfwrite import DXFEngine as dxf


dom = xml.dom.minidom.parse('albano/albano.xml')
root = dom.documentElement
polygons = root.getElementsByTagName("polygons")[0].getElementsByTagName("polygon")
print(polygons)
for ploygon in polygons:
    ploy = []
    name = ploygon.getAttribute("id")

    if name.startswith('nfp') or name.startswith('ifp'):
        continue
    print('name:', name)
    lines = ploygon.getElementsByTagName("lines")[0]
    dots = lines.getElementsByTagName("segment")
    # print(len(dots))
    for dot in dots :
        t = (dot.getAttribute("x0"),dot.getAttribute("y0"))
        ploy.append(t)
    ploy.append(ploy[0])
    for p in ploy:
        print('p', p)
    drawing = dxf.drawing(name + ".dxf")
    drawing.add(dxf.polyline(points = ploy))
    drawing.save()





