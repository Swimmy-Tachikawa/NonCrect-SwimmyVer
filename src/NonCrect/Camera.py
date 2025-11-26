

import pygame as pg
from .objects import Object, NoneType


class Camera(Object):

    __master = None

    target = None
    limiting = None

    @property
    def master(self): return self.__master

    def __init__(self, master: pg.Surface, pos):
        self.__master = master
        pg.display.set_caption("NonCrect")
        super().__init__(pos, master.get_size())
        self.target = NoneType((0, 0), master.get_size())
        self.limiting = [False, True]
        return

    def set_target(self, target: Object):
        self.target = target
        return

    def __start__(self, camera): ...

    def __update__(self, *args, **kwargs):
        self.center = [
            int(p+(t-p)/12)
            for t, p in zip(self.target.center, self.center)
        ]

        if self.limiting[1]:
            if self.position[1]+self.size[1] > self.size[1]:
                self.position[1] = 0
                ...
        if self.limiting[0]:
            if self.position[0] < 0:
                self.position[0] = 0
                ...
            ...

        self.rect[:2] = self.position
        return

    def blit(self, source: pg.Surface, dest: list[int, int], depth):
        dest = [d-p*(1/depth) for d, p in zip(dest, self.position)]
        self.__master.blit(source, dest)
        return

    def fill(self, color):
        self.__master.fill(color)
        return

    ...
