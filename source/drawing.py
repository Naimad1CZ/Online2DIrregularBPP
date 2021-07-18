from matplotlib import pyplot as plt
from shapely.geometry import *
from descartes.patch import PolygonPatch
import os

pyplot_radius = 11  # set this from outside to get the needed size of pyplot figures
ret = False  # set to True to disable drawing pyplot figures

counter = 0
_internal_counter = 0
drawing_name = ''

def show_in_pyplot(polygons, lines=[], points=[], last_polygon=None, radius=None, save=True, dpi=150, grid=False, really_ret=True, mode=1, total_placed_shapes=None):
    global _internal_counter
    if _internal_counter == 0:
        if not os.path.exists('../drawings'):
            os.makedirs('../drawings')

    if radius is None:
        radius = pyplot_radius

    if ret and really_ret:
        return

    f = plt.figure()
    ax = f.gca()
    ax.set_aspect(1)
    for p in polygons:
        if type(p) is MultiPolygon:
            for m in p:
                patch = PolygonPatch(m, alpha=0.5, zorder=2)
                ax.add_patch(patch)
        elif type(p) is Polygon:
            patch = PolygonPatch(p, alpha=0.5, zorder=2)
            ax.add_patch(patch)
        else:
            print("don't yet implemented showing in pyplot the type", type(p))
            print(p)

    for l in lines:
        xs, ys = zip(*(l.coords))  # zip to x and y
        if mode == 1 or mode == 2:
            plt.plot(xs, ys, color='black', alpha=0.7)
        else:
            plt.plot(xs, ys, color='red', marker="o")

    if last_polygon is not None:
        patch = PolygonPatch(last_polygon, alpha=0.5, color='red', zorder=2)
        ax.add_patch(patch)


    plt.xlim(-0.5 - radius, radius + 0.5)
    plt.ylim(-0.5 - radius, radius + 0.5)

    if grid:
        plt.grid()

    if save:
        # save the figure to file
        global counter
        counter += 1
        _internal_counter += 1
        # creating video afterwards
        if mode == 2:
            plt.savefig('../drawings/' + str(_internal_counter) + '.png', bbox_inches='tight', dpi=dpi)
            pass
        else:
            if total_placed_shapes is not None:
                plt.savefig('../drawings/' + drawing_name + str(total_placed_shapes) + '.png', bbox_inches='tight', dpi=dpi)
            else:
                plt.savefig('../drawings/' + drawing_name + str(counter) + '.png', bbox_inches='tight', dpi=dpi)
        plt.close()
    else:
        plt.show()
