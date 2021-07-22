from generator_placer_base import ShapeGenerator, Placer, Symmetry
from shape_generators import RandomShapeGenerator
from geometry_tools import get_CFR_candidate_points, rotate_around_first_point, regular_polygon,\
    translate_where_point_has_x_y
import geometry_tools
import drawing

from shapely.geometry import Polygon, MultiPolygon, box
from shapely.ops import unary_union

import itertools
import datetime
import time
from math import sqrt


# manually change those 2
drawing_return = True
DEBUG = False

# don't change EPSILON if possible
EPSILON = 0.000000000001
# you can change it because of performance reasons (smaller = faster)
number_of_vertices_of_circle = 120


def log(*s, severity=4):
    if severity < 4:
        print(*s)
    elif DEBUG:
        print(*s)


class DamiansPlacer(Placer):
    # container should be either Polygon or list of tuples - coordinates x, y, or None - indicates circle container
    def __init__(self, sg: ShapeGenerator, container=None):
        super().__init__(sg)
        # _radius is just approximate (doesn't need to be exact) number how big is "radius" of polygon container;
        # for circle containers it's the exact size of radius of circle;
        # _radius is also used as pyplot radius
        self._radius = sg._radius
        self._rotations = int(sg._rotations)
        if container is None:
            self._curr_pol = regular_polygon(self._radius, number_of_vertices_of_circle)
            self._container = regular_polygon(self._radius, number_of_vertices_of_circle)
        else:
            self._curr_pol = Polygon(container)
            self._container = Polygon(container)
        self._all_placed_shapes = []
        self._count_of_placed = 0
        self._smallest_shape_area = self._radius * self._radius * 1000
        self._surr_waste_plus_time = 0
        self._surr_waste_plus_intersection_time = 0

    def can_place_shape(self, to_place: Polygon, where_place: Polygon):
        return to_place.difference(where_place).area <= 10000 * EPSILON

    def picking_policy_bottom_left(self, clear_candidates, clear_points):
        min_y = min(clear_points, key=lambda t: t[1])[1]
        index = 0
        min_x = self._radius * 10000000
        for i in range(len(clear_points)):
            if clear_points[i][1] == min_y:
                if clear_points[i][0] < min_x:
                    min_x = clear_points[i][0]
                    index = i

        return clear_candidates[index]

    def picking_policy_minimal_convex_hull(self, clear_candidates):
        if self._count_of_placed == 0:
            differences = []
            for m in range(len(clear_candidates)):
                difference = self._curr_pol.difference(clear_candidates[m].buffer(20000 * EPSILON, 1, join_style=2))
                differences.append(difference.length)
            idx = differences.index(min(differences))
            return clear_candidates[idx]

        minimum_convex_hull_area = self._radius * self._radius * 1000
        winner = None
        already_placed_shapes = unary_union(self._all_placed_shapes)
        for cand in clear_candidates:
            tmp = already_placed_shapes.union(cand).convex_hull.area
            if tmp < minimum_convex_hull_area:
                minimum_convex_hull_area = tmp
                winner = cand

        return winner

    def picking_policy_minimal_surround_waste(self, clear_candidates, shap):
        if self._count_of_placed == 0:
            self.total_shapes_sqrt_area = 0

        # adds a square root of the area of current shape
        self.total_shapes_sqrt_area += sqrt(shap.area)
        average_sqrt = self.total_shapes_sqrt_area / (self._count_of_placed + 1)
        buffer_distance = average_sqrt / 10

        # will be counted including the area of candidate, but it's the same for every candidate
        minimum_waste_around = self._radius * self._radius * 1000
        winner = None

        for cand in clear_candidates:
            buffered_cand = cand.buffer(buffer_distance, 1, join_style=2)
            intersection = self._curr_pol.intersection(buffered_cand)
            intersection_area = intersection.area

            if intersection_area < minimum_waste_around:
                minimum_waste_around = intersection_area
                winner = cand

        return winner

    # clear candidates = candidates chosen by computing NFP/IFP, shap = shape we need to place
    def picking_policy_minimal_surround_waste_plus(self, clear_candidates, shap):
        start = time.time()
        if self._count_of_placed == 0:
            self.total_shapes_sqrt_area = 0

        # adds a square root of the area of current shape
        self.total_shapes_sqrt_area += sqrt(shap.area)
        average_sqrt = self.total_shapes_sqrt_area / (self._count_of_placed + 1)

        # the best _surround_waste_plus_parameter is something like 3.5 or 4, in wider range 3 - 4.5
        buffer_distance = average_sqrt / self._surround_waste_plus_parameter

        # will be counted including the area of candidate, but it's the same for every candidate
        minimum_waste_around = self._radius * self._radius * 1000
        winner = None

        for cand in clear_candidates:
            buffered_cand = cand.buffer(buffer_distance, 1, join_style=2)
            buffered_cand_inside = buffered_cand.intersection(self._container)
            buffered_cand_outside = buffered_cand.difference(self._container)
            st = time.time()
            inner_intersection = self._curr_pol.intersection(buffered_cand_inside)
            en = time.time()
            self._surr_waste_plus_intersection_time += en - st
            inner_intersection_area = inner_intersection.area

            outer_area = buffered_cand_outside.area

            # best _surround_waste_plus_parameter2 is apparently 0.08, maybe 0.04
            waste = inner_intersection_area + self._surround_waste_plus_parameter2 * outer_area

            if waste < minimum_waste_around:
                minimum_waste_around = waste
                winner = cand

        end = time.time()
        self._surr_waste_plus_time += end - start
        return winner

    def picking_policy_min_conv_hull_and_min_surr_waste_plus(self, clear_candidates, shap):
        if self._count_of_placed == 0:
            differences = []
            for m in range(len(clear_candidates)):
                difference = self._curr_pol.difference(clear_candidates[m].buffer(20000 * EPSILON, 1, join_style=2))
                differences.append(difference.length)
            idx = differences.index(min(differences))

            self.total_shapes_sqrt_area = clear_candidates[idx].area
            return clear_candidates[idx]

        minimum_convex_hull_area = self._radius * self._radius * 1000
        already_placed_shapes = unary_union(self._all_placed_shapes)

        conv_h_areas = []
        for cand in clear_candidates:
            tmp = already_placed_shapes.union(cand).convex_hull.area
            conv_h_areas.append(tmp)
            if tmp < minimum_convex_hull_area:
                minimum_convex_hull_area = tmp

        winners = []
        shap_area = shap.area
        for i in range(len(clear_candidates)):
            if conv_h_areas[i] < minimum_convex_hull_area + (shap_area / 5):
                winners.append(clear_candidates[i])

        return self.picking_policy_minimal_surround_waste_plus(winners, shap)

    def picking_policy_max_bounding_box_overlap(self, clear_candidates):
        if self._count_of_placed == 0:
            differences = []
            for m in range(len(clear_candidates)):
                difference = self._curr_pol.difference(clear_candidates[m].buffer(20000 * EPSILON, 1, join_style=2))
                differences.append(difference.length)
            idx = differences.index(min(differences))
            return clear_candidates[idx]

        bounding_boxes = [box(*sh.bounds) for sh in self._all_placed_shapes]
        bb_union = unary_union(bounding_boxes)

        max_overlap = -1
        winner = None

        for cand in clear_candidates:
            cand_bb = box(*cand.bounds)
            intersection = bb_union.intersection(cand_bb)
            intersection_area = intersection.area

            if intersection_area > max_overlap:
                max_overlap = intersection_area
                winner = cand

        return winner

    def picking_policy_my_own_old(self, clear_candidates, shap):
        # global_candidates should contain tuples:
        # (shape, area of smaller polygons that are created by putting, difference of lengths after putting)

        shap_area = shap.area
        shap_length = shap.length
        global_candidates = []

        log('start_for_cycles')

        # Go through all existing (distinct) polygons that we need to fill
        for pol in self._curr_pol:
            pol_area = pol.area
            if pol_area < shap_area:
                continue
            log(',')

            for m in range(len(clear_candidates)):
                difference = pol.difference(clear_candidates[m].buffer(20000 * EPSILON, 1, join_style=2))

                difference_area = difference.area
                # if pol is not the polygon where ve want to place candidate
                if pol_area - 10000 * EPSILON < difference_area:
                    continue

                if type(difference) is Polygon:
                    global_candidates.append((clear_candidates[m], difference_area, difference.length - pol.length))
                elif type(difference) is MultiPolygon:
                    max_area = 0
                    for small_pol in difference:
                        if small_pol.area > max_area:
                            max_area = small_pol.area

                    global_candidates.append(
                        (clear_candidates[m], difference_area - max_area, difference.length - pol.length))

        log('end_for_cycles')

        if len(global_candidates) == 0:
            log('unable to find place with touching at least points!')
            return -1

        # some big initial number
        minimum_circumference_increase = self._curr_pol.length * 1000
        for can in global_candidates:
            if can[2] < minimum_circumference_increase:
                minimum_circumference_increase = can[2]

        global_candidates = [x for x in global_candidates if x[2] < minimum_circumference_increase + (shap_length / 10)]

        # some big initial number
        minimum_waste = self._radius * self._radius * 1000
        for can in global_candidates:
            if minimum_waste > can[1]:
                minimum_waste = can[1]

        global_candidates = [x for x in global_candidates if x[1] < minimum_waste + 0.01]

        if len(global_candidates) == 0:
            log('something went wrong, all global candidates gone')
            return -2

        winner = global_candidates[0]
        return winner[0]

    def choose_the_best_candidate(self, candidates_shapes, candidates_points, candidates_areas, shap, choose_least_CFR_area, picking_policy):
        all_cand_shapes = list(itertools.chain(*candidates_shapes))
        log('len:', len(all_cand_shapes))
        if len(all_cand_shapes) == 0:
            log('No candidates available!')
            drawing.show_in_pyplot(self._all_placed_shapes, lines=[self._container.exterior], dpi=500, really_ret=False, mode=1, total_placed_shapes=self._count_of_placed)
            #drawing.show_in_pyplot(self._all_placed_shapes, lines=[self._container.exterior], last_polygon=shap, dpi=500, really_ret=False, CFR_mode=2)
            return -1

        if choose_least_CFR_area:
            shap_area = shap.area
            cand_shapes = []
            cand_points = []
            least_area = min(candidates_areas)
            # if we have some small area, then choose only small area/s
            if least_area < shap_area * 10:
                for i in range(len(candidates_areas)):
                    if candidates_areas[i] < least_area * 2 + (shap_area / 3):
                        cand_shapes.extend(candidates_shapes[i])
                        cand_points.extend(candidates_points[i])
            if len(cand_shapes) == 0:
                cand_shapes = all_cand_shapes
                cand_points = list(itertools.chain(*candidates_points))
        else:
            cand_shapes = all_cand_shapes
            cand_points = list(itertools.chain(*candidates_points))

        if picking_policy == 'my_own_old':
            winner = self.picking_policy_my_own_old(cand_shapes, shap)
        elif picking_policy == 'bottom_left':
            winner = self.picking_policy_bottom_left(cand_shapes, cand_points)
        elif picking_policy == 'convex_hull':
            winner = self.picking_policy_minimal_convex_hull(cand_shapes)
        elif picking_policy == 'surround_waste':
            winner = self.picking_policy_minimal_surround_waste(cand_shapes, shap)
        elif picking_policy == 'surround_waste_plus':
            winner = self.picking_policy_minimal_surround_waste_plus(cand_shapes, shap)
        elif picking_policy == 'max_bb_overlap':
            winner = self.picking_policy_max_bounding_box_overlap(cand_shapes)
        elif picking_policy == 'conv_hull_surr_waste':
            winner = self.picking_policy_min_conv_hull_and_min_surr_waste_plus(cand_shapes, shap)

        if type(winner) is int:
            drawing.show_in_pyplot([shap])
            drawing.show_in_pyplot([self._curr_pol])
            return winner

        if DEBUG:
            log('difference in area of "winner" is', winner.difference(self._curr_pol).area, severity=3)
        if not self.can_place_shape(winner, self._curr_pol):
            diff = winner.difference(self._curr_pol).area
            if diff > 0.01:
                log('Need to choose another winner!----------------------------------------------', severity=4)
                log('difference in area of "winner" is', diff, severity=4)
            else:
                log('Need to choose another winner!----------------------------------------------', severity=3)
                log('difference in area of "winner" is', diff, severity=3)
            for i in range(len(candidates_shapes)):
                try:
                    idx = candidates_shapes[i].index(winner)
                    del candidates_shapes[i][idx]
                    del candidates_points[i][idx]
                    break
                except ValueError:
                    pass
            winner = self.choose_the_best_candidate(candidates_shapes, candidates_points, candidates_areas, shap, choose_least_CFR_area, picking_policy)

        return winner


    def place_generated_shape(self, shap: Polygon, CFR_mode: int, choose_least_CFR_area: bool, picking_policy: str):
        if shap.area < self._smallest_shape_area:
            self._smallest_shape_area = shap.area
        if type(self._curr_pol) is Polygon:
            self._curr_pol = MultiPolygon([self._curr_pol])

        log('start CFR computation')
        n_rotations = 360 / self._rotations
        candidates_shapes = []
        candidates_points = []
        candidates_areas = []

        # Go through all the rotations
        for i in range(int(n_rotations)):
            s = rotate_around_first_point(shap, i * self._rotations)
            cands, points, areas = get_CFR_candidate_points(self._container, self._all_placed_shapes, s, CFR_mode=CFR_mode)
            candidates_shapes.extend(cands)
            candidates_points.extend(points)
            candidates_areas.extend(areas)

        log('start choosing the best candidate')
        winner = self.choose_the_best_candidate(candidates_shapes, candidates_points, candidates_areas, shap, choose_least_CFR_area=choose_least_CFR_area, picking_policy=picking_policy)
        if type(winner) is int:
            return winner

        log('best candidate chosen.')

        # place the best candidate to current polygon, but use a bigger shape to create some ok and valid geometry
        self._curr_pol = self._curr_pol.difference(winner.buffer(200 * EPSILON, 1, join_style=2))

        # remove too small holes in current polygon to gain performance
        if type(self._curr_pol) is MultiPolygon:
            polygons_to_use = [x for x in self._curr_pol if x.area > EPSILON] # (self._smallest_shape_area / 5)]
            self._curr_pol = MultiPolygon(polygons_to_use)

        self._all_placed_shapes.append(winner)

        # find out rotation and place in generator
        default_first_point = shap.exterior.coords[0]
        coords_of_first_point = winner.exterior.coords[0]
        coords_of_second_point = winner.exterior.coords[1]

        for it in range(int(n_rotations)):
            s = rotate_around_first_point(shap, it * self._rotations)
            s = translate_where_point_has_x_y(s, default_first_point, coords_of_first_point[0],
                                              coords_of_first_point[1])
            if (round(s.exterior.coords[1][0], 6) == round(coords_of_second_point[0], 6)) and (round(s.exterior.coords[1][1], 6) == round(coords_of_second_point[1], 6)):
                self._sg.place_shape(coords_of_first_point[0], coords_of_first_point[1], it * self._rotations)
                self._count_of_placed += 1
                if self._count_of_placed % 15 == 0:
                    log('shape successfully placed shape number', self._count_of_placed, '!', severity=3)
                else:
                    log('shape successfully placed shape number', self._count_of_placed, '!', severity=4)
                #drawing.show_in_pyplot([self._curr_pol], save=True)
                drawing.show_in_pyplot(self._all_placed_shapes, lines=[self._container.exterior], save=True, mode=1)
                return 0

        log('problem finding rotation!')
        return -2

    def run(self, CFR_mode: int, choose_least_CFR_area: bool, picking_policy: str, surround_waste_plus_parameter=None, surround_waste_plus_parameter2=None):
        start = time.time()

        log('start:', severity=2)
        geometry_tools.DEBUG = DEBUG
        geometry_tools.EPSILON = EPSILON
        geometry_tools.translate_number = self._radius * 5
        drawing.pyplot_radius = self._radius
        drawing.ret = drawing_return

        # relevant only for picking_policies 'surround_waste_plus' and == 'conv_hull_surr_waste'
        if surround_waste_plus_parameter is not None:
            self._surround_waste_plus_parameter = surround_waste_plus_parameter
        else:
            self._surround_waste_plus_parameter = 4  # range 3 - 4.5 is good overall

        if surround_waste_plus_parameter2 is not None:
            self._surround_waste_plus_parameter2 = surround_waste_plus_parameter2
        else:
            self._surround_waste_plus_parameter2 = 0.08  # 0.04 is also possible and good

        dt = datetime.datetime.now()
        drawing.drawing_name = picking_policy + '-' + str(CFR_mode) + '-' + str(int(choose_least_CFR_area)) + '_'\
                               + str(dt.hour) + '-' + str(dt.minute) + '-' + str(dt.second) + '_'
        drawing.counter = 0

        # do some magic
        return_sign = 0
        while return_sign == 0:
            s = self._sg.new_shape()
            pol_s = Polygon(s)
            return_sign = self.place_generated_shape(pol_s, CFR_mode, choose_least_CFR_area, picking_policy)

        end = time.time()
        log('the end', severity=3)
        log('time elapsed this run:', end - start, severity=3)
        log('IFP_time time elapsed this run:', geometry_tools.IFP_time, severity=3)
        log('NFP_time time elapsed this run:', geometry_tools.NFP_time, severity=3)
        log('NFP_unary_union_time time elapsed this run:', geometry_tools.NFP_unary_union_time, severity=3)
        log('difference_time time elapsed this run:', geometry_tools.difference_time, severity=3)
        log('get_geom_points_time time elapsed this run:', geometry_tools.get_geom_points_time, severity=3)
        if self._surr_waste_plus_time > 0:
            log('_surr_waste_plus_time time elapsed this run:', self._surr_waste_plus_time, severity=3)
            log('_surr_waste_plus_intersection_time time elapsed this run:', self._surr_waste_plus_intersection_time, severity=3)

        log('picking policy was:', picking_policy, severity=2)
        if picking_policy == 'surround_waste_plus' or picking_policy == 'conv_hull_surr_waste':
            log('self._surround_waste_plus_parameter =', self._surround_waste_plus_parameter, severity=2)
            log('self._surround_waste_plus_parameter2 =', self._surround_waste_plus_parameter2, severity=2)

        geometry_tools.IFP_time = 0
        geometry_tools.NFP_time = 0
        geometry_tools.NFP_unary_union_time = 0
        geometry_tools.difference_time = 0
        geometry_tools.get_geom_points_time = 0

        return self._sg


if __name__ == '__main__':
    #placer = DamiansPlacer(SquareShapeGenerator(radius, 120))
    placer = DamiansPlacer(RandomShapeGenerator(radius=10, rotations=Symmetry.fourfold, fixed_seed=42))
    #placer.run(1, True, 'bottom_left')
