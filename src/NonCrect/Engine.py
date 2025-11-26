

from time import time
import pygame as pg
from .objects import (
    Charactor,
    Land,
    KillZone,
    BackGround,
    Unseen,
    Texts, CheckPoint, BackRect,
    Gool, StartCameraWork
)
from .Camera import Camera


unseen_units = [
    (-1, 30, 1, 32),
]

lands_units = [
    (0, 1, 24, 1),
    (10, 2, 5, 1),
    (11, 3, 3, 1),
    (25, 1, 8, 1),
    (36, 1, 14, 1),
] + [
    (51+(i+2)*2, 4-abs(i), 1, 1)
    for i in range(-2, 3)
] + [
    (61, 1, 9, 1),
] + [
    (73+(i+2)*5, 4-abs(i), 2, 1)
    for i in range(-2, 3)
] + [
    (98, 1, 15, 1),
] + [
    (
        111 if i%6==0 else
        113 if i%6==1 else
        115 if i%6==2 else
        116 if i%6==3 else
        114 if i%6==4 else
        112,
        i,
        1, 1
    )
    for i in range(22)
] + [
    (119+i*3, 21, 1, 1)
    for i in range(5)
]


back_rect_units = [
    (114-i%2, 2+(i*3), 1, 3)
    for i in range(9)
]

spawn_point = (12, 5)

check_point_units = [
    (43, 3, 1, 1),
    (65, 3, 1, 1),
    (105, 3, 1, 1),
]

gool_units = [
    (136, 22, 1, 1),
]

kill_units = [
    (18*i, -1, 18, 1)
    for i in range(10)
]


unseen = [
    Unseen(unit)
    for unit in unseen_units
]

lands = [
    Land(rand_unit)
    for rand_unit in set(lands_units)
]

back_rects = [
    BackRect(back_rect_unit)
    for back_rect_unit in back_rect_units
]

check_point = [
    CheckPoint(check_point_unit)
    for check_point_unit in check_point_units
]

gools = [
    Gool(unit)
    for unit in gool_units
]

kills = [
    KillZone(kill_unit)
    for kill_unit in set(kill_units)
]

class Engine:
    fps = None
    size = None
    objects: list = None
    charactor = None

    def __init__(self, fps = 60):
        self.fps = fps
        self.size = (900, 600)
        self.objects = [BackGround(), Texts()] + \
                       unseen + lands + kills + back_rects + \
                       check_point + gools + [StartCameraWork((-550, 600))]
        self.spawn_point = spawn_point
        self.gool = False
        self.c = 0
        self.start = True
        self.charactor = None
        return

    def __start__(self, camera):
        [obj.__start__(camera) for obj in self.objects]
        return

    def __key_down__(self, key_event: pg.event.Event) -> int | None:
        return

    def __update__(self, events: list[pg.event.Event], delta_t, camera) -> int | None:
        for event in events:
            if event.type == pg.QUIT:
                return -1
            if event.type == pg.KEYDOWN:
                self.__key_down__(event.key)
                ...
            ...

        [obj.__update__(pg.key.get_pressed(), delta_t, self.objects, camera) for obj in self.objects]
        chars = [obj for obj in self.objects if isinstance(obj, Charactor)]
        if not len(chars) == 0:
            self.spawn_point = chars[0].spawn_point
            self.gool = chars[0].gool
            ...
        else:
            if self.gool: self.c += 1
            if self.c > 180:
                return -1
            ...
        self.objects = [obj for obj in self.objects if not obj.killing]
        if self.start and StartCameraWork not in map(type, self.objects):
            self.start = False
            ...
        if not Charactor in map(type, self.objects) and not self.gool:
            self.charactor = Charactor(self.spawn_point)
            self.objects.append(self.charactor)
            ...
        if not self.start:
            camera.set_target(self.charactor)
            camera.limiting[0] = True
            self.charactor.control = True
            ...

        return

    def __render__(self, camera):
        camera.fill("White")
        camera.__update__()
        [obj.__render__(camera) for obj in self.objects]
        pg.display.update()
        return

    def __mainloop__(self):

        one_ft = 1/self.fps
        pre_ft = time()

        camera = Camera(pg.display.set_mode(self.size), (-1000, 0))
        camera.set_target(self.objects[-1])

        self.__start__(camera)

        done = False
        while not done:

            now_t = time()
            delta_t = now_t - pre_ft
            if delta_t < one_ft: continue
            pre_ft = now_t

            self.__render__(camera)

            op = self.__update__(pg.event.get(), one_ft, camera)

            if op is not None:
                match op:
                    case -1:
                        done = True
                    case -2:
                        break

            continue

        return

    def exe(self):
        pg.init()
        self.__mainloop__()
        pg.quit()
        return