from damians_implementation import DamiansPlacer as PlacerDamian
#from placer_filip import MyPlacer as PlacerFilip
#from placer_daniel import MyPlacer as PlacerDaniel

from shape_generators import SG1, SG2, SG3, SG4, SG5, SG6, SG7, EUROS
from generator_placer_base import Symmetry

from timeit import default_timer as timer
import time

SFG_competition = [
    SG1,
    SG2,
    SG3,
    SG4,
    SG5,
    SG6,
    SG7
]

racers = {
    #"Filip": PlacerFilip,
    #"Daniel": PlacerDaniel,
    "Damian": PlacerDamian,
}

picking_policies = [
    'my_own_old',
    'bottom_left',
    'convex_hull',
    'surround_waste',
    'surround_waste_plus',
    'max_bb_overlap',
    'conv_hull_surr_waste',
]

for name, placer in racers.items():
    print("*" * 50)
    print(f" Racer: {name}")
    print("*" * 50)

    euro_datasets = False
    best_run = True
    run_dan_filip = False
    online_benchmarks = False

    if euro_datasets:
        # best method
        #picking_policy = 'surround_waste_plus'
        #CFR_mode = 0
        #choose_least_area_IFP = False

        picking_policy = 'surround_waste_plus'
        CFR_mode = 0
        choose_least_area_IFP = False

        filenames = ['../datasets/albano', '../datasets/dighe1', '../datasets/dighe2', '../datasets/marques', '../datasets/shapes', '../datasets/swim']
        scales = [0.1, 0.1, 0.1, 0.1, 0.1, 0.1]
        rotations = [Symmetry.fourfold, Symmetry.none, Symmetry.none, Symmetry.fourfold, Symmetry.twofold, Symmetry.twofold]
        widths = [49, 100.01, 100.01, 104, 40, 57.52]
        heights = [100, 100.01, 100.01, 80, 55, 60]

        filled = []
        shapes = []
        times = []
        for i in range(len(filenames)):
            filename = filenames[i]
            scale = scales[i]
            rotation = rotations[i]

            width = widths[i] * scale
            height = heights[i] * scale
            width_over_2 = width / 2
            height_over_2 = height / 2
            radius = max(width_over_2, height_over_2)
            cont = [[-width_over_2, -height_over_2], [width_over_2, -height_over_2], [width_over_2, height_over_2], [-width_over_2, height_over_2]]

            start = timer()

            mp = placer(EUROS(polygon_radius=radius, symmetry=rotation, filename=filename, container=cont, scale=scale), cont)
            sg = mp.run(CFR_mode, choose_least_area_IFP, picking_policy)

            end = timer()
            times.append(end - start)
            filled.append(sg.filled_area)
            shapes.append(sg.placed_shapes)
            print(f"SG done, placed {sg.placed_shapes} shapes!")
            time.sleep(1)

        print(f"Competition ended!")
        print(f"scores are:        {filled}")
        print(f"placed shapes are: {shapes}")
        print(f"percents are:      {[round(x * 100, 2) for x in filled]}")
        print(f"Average filled area: {sum(filled) / len(filled)}")
        print(f"times taken are:   {times}")
        print(f"Total time taken: {sum(times)}s, that is {sum(times) / sum(shapes)}s per shape")
        container = "circle" if cont is None else "square"
        print(
            f"Used picking policy: {picking_policy}, used container: {container}, used CFR_mode: {CFR_mode}, used choose_least_area_IFP: {choose_least_area_IFP}")
        print(
            f"**************************************************************************************************************************")

        with open('../results/' + 'EURO_' + picking_policy + '.txt', 'w') as f:
            print(f"{picking_policy}, {CFR_mode}, {choose_least_area_IFP}, {container}", file=f)
            for score in filled:
                print(f"{score}\t", end='', file=f)
            print("", file=f)
            for placed_count in shapes:
                print(f"{placed_count}\t", end='', file=f)
            print("", file=f)
            for time in times:
                print(f"{time}\t", end='', file=f)
            print("", file=f)
            print("", file=f)

    elif best_run:
        # best method
        # picking_policy = 'surround_waste_plus'
        # CFR_mode = 0
        # choose_least_area_IFP = False

        # set those parameters
        picking_policy = 'surround_waste_plus'
        CFR_mode = 0
        choose_least_area_IFP = False
        radius = 9
        containers = [[(-radius, -radius), (radius, -radius), (radius, radius), (-radius, radius)]]


        with open('../results/' + picking_policy + '_' + str(radius) + '.txt', 'w') as f:
            for cont in containers:
                filled = []
                shapes = []
                times = []
                for i, o in enumerate(SFG_competition):
                    start = timer()

                    mp = placer(o(cont), cont)
                    sg = mp.run(CFR_mode, choose_least_area_IFP, picking_policy)

                    end = timer()
                    times.append(end - start)
                    filled.append(sg.filled_area)
                    shapes.append(sg.placed_shapes)
                    print(f"SG done, placed {sg.placed_shapes} shapes!")

                print(f"Competition ended!")
                print(f"scores are:        {filled}")
                print(f"placed shapes are: {shapes}")
                print(f"percents are:      {[round(x * 100, 2) for x in filled]}")
                print(f"Average filled area: {sum(filled) / len(filled)}")
                print(f"times taken are:   {times}")
                print(f"Total time taken: {sum(times)}s, that is {sum(times) / sum(shapes)}s per shape")
                container = "circle" if cont is None else "square"
                print(
                    f"Used picking policy: {picking_policy}, used container: {container}, used CFR_mode: {CFR_mode}, used choose_least_area_IFP: {choose_least_area_IFP}")
                print(
                    f"**************************************************************************************************************************")

                print(f"{picking_policy}, {CFR_mode}, {choose_least_area_IFP}, {container}", file=f)
                for score in filled:
                    print(f"{score}\t", end='', file=f)
                print("", file=f)
                for placed_count in shapes:
                    print(f"{placed_count}\t", end='', file=f)
                print("", file=f)
                for time in times:
                    print(f"{time}\t", end='', file=f)
                print("", file=f)
                print("", file=f)

    elif run_dan_filip:
        with open('../results/' + name + '.txt', 'w') as f:
            filled = []
            shapes = []
            times = []
            for i, o in enumerate(SFG_competition):
                start = timer()

                mp = placer(o())
                sg = mp.run()

                end = timer()
                times.append(end - start)
                filled.append(sg.filled_area)
                shapes.append(sg.placed_shapes)
                sg.show_results(savename=f"{name.lower()}_{o.__name__}")
                print(f"SG done, placed {sg.placed_shapes} shapes!")

            print(f"Competition ended!")
            print(f"scores are:        {filled}")
            print(f"placed shapes are: {shapes}")
            print(f"percents are:      {[round(x * 100, 2) for x in filled]}")
            print(f"Average filled area: {sum(filled) / len(filled)}")
            print(f"times taken are:   {times}")
            print(f"Total time taken: {sum(times)}s, that is {sum(times) / sum(shapes)}s per shape")
            print(f"**************************************************************************************************************************")

            for score in filled:
                print(f"{score}\t", end='', file=f)
            print("", file=f)
            for placed_count in shapes:
                print(f"{placed_count}\t", end='', file=f)
            print("", file=f)
            for time in times:
                print(f"{time}\t", end='', file=f)
            print("", file=f)
            print("", file=f)

    elif online_benchmarks:
        containers = [[(-9, -9), (9, -9), (9, 9), (-9, 9)], None]
        picking_policy = picking_policies[0]

        with open('../results/' + picking_policy + '.txt', 'w') as f:
            for cont in containers:
                for CFR_mode in [0, 1, 2]:
                    for choose_least_area_IFP in [False, True]:
                        filled = []
                        shapes = []
                        times = []
                        for i, o in enumerate(SFG_competition):
                            start = timer()

                            mp = placer(o(cont), cont)
                            sg = mp.run(CFR_mode, choose_least_area_IFP, picking_policy)

                            end = timer()
                            times.append(end - start)
                            filled.append(sg.filled_area)
                            shapes.append(sg.placed_shapes)
                            #sg.show_results(savename=f"{name.lower()}_{o.__name__}")
                            print(f"SG done, placed {sg.placed_shapes} shapes!")

                        print(f"Competition ended!")
                        print(f"scores are:        {filled}")
                        print(f"placed shapes are: {shapes}")
                        print(f"percents are:      {[round(x * 100, 2) for x in filled]}")
                        print(f"Average filled area: {sum(filled) / len(filled)}")
                        print(f"times taken are:   {times}")
                        print(f"Total time taken: {sum(times)}s, that is {sum(times) / sum(shapes)}s per shape")
                        container = "circle" if cont is None else "square"
                        print(f"Used picking policy: {picking_policy}, used container: {container}, used CFR_mode: {CFR_mode}, used choose_least_area_IFP: {choose_least_area_IFP}")
                        print(f"**************************************************************************************************************************")

                        print(f"{picking_policy}, {CFR_mode}, {choose_least_area_IFP}, {container}", file=f)
                        for score in filled:
                            print(f"{score}\t", end='', file=f)
                        print("", file=f)
                        for placed_count in shapes:
                            print(f"{placed_count}\t", end='', file=f)
                        print("", file=f)
                        for time in times:
                            print(f"{time}\t", end='', file=f)
                        print("", file=f)
                        print("", file=f)
