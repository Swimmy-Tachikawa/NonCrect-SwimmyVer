
from abc import ABC, abstractmethod
from copy import deepcopy, copy
from random import randrange
from pygame import Surface, Rect
import pygame as pg


class Object(ABC):

    position = None
    size = None
    rect = None
    movement = None
    __surface__ = None
    killing = False
    depth = None

    @property
    def center(self): return [p+s//2 for p, s in zip(self.position, self.size)]
    @center.setter
    def center(self, value): self.position = [c-s//2 for c, s in zip(value, self.size)]

    def __init__(self, position, size, depth = 1.):
        self.position = list(position)
        self.size = list(size)
        self.rect = Rect(position, size)
        self.movement = [0, 0]
        self.__surface__ = Surface(size)
        self.killing = False
        self.depth = depth
        return

    @abstractmethod
    def __start__(self, camera): ...

    @abstractmethod
    def __update__(self, key_pressed, delta_t, objects, camera): ...

    def __render__(self, master):
        master.blit(self.__surface__, self.position, self.depth)
        return

    def kill(self):
        self.killing = True
        return

    ...


class NoneType(Object):
    def __start__(self, camera): ...
    def __update__(self, key_pressed, delta_t, objects, camera): ...
    ...


class Afterimage(Object):

    alpha = None
    rand = None

    def __init__(self, position, size, time):
        super().__init__(position, size)
        self.__surface__.fill((0, 0, 0, 192))
        self.alpha = 192
        self.rm_alpha = self.alpha/(60*time)
        self.rand = randrange(10, 20)/10
        return

    def __start__(self, camera): ...
    def __update__(self, key_pressed, delta_t, objects, camera):
        self.__surface__.set_alpha(self.alpha)
        self.alpha -= self.rm_alpha
        if self.alpha <= 0:
            return False
        return True
    def __up__(self):
        self.position[1] -= self.rand
        return

    ...


class Charactor(Object):

    is_land = None
    dash_cool = None
    afterimages = None
    afterimage_cool = None
    death_f = None
    spawn = None
    spawn_point = None
    control = None
    gool = None

    def get_spawn_point(self): return self.spawn_point

    def __init__(self, pos_unit):
        super().__init__(
            [pos_unit[0]*50+10, (pos_unit[1]-12)*-50+10],
            (30, 30)
        )
        self.is_land = False
        self.dash_cool = 0
        self.afterimages = []
        self.afterimage_cool = 0
        self.death_f = False
        self.spawn = True
        self.spawn_point = pos_unit
        self.control = False
        self.gool = False
        self.fly_cool_count = 0
        self.fly_cool = 12
        return

    def __start__(self, camera): ...

    def death(self):
        [
            self.afterimages.append(Afterimage(
                [
                    p + randrange(s - 5)
                    for p, s in zip(self.position, self.size)
                ],
                (5, 5),
                (randrange(14) + 1) / 10
            ))
            for _ in range(60)
        ]
        self.death_f = True
        return

    def __update__(self, key_pressed, delta_t, objects, camera):

        self.afterimages = [
            afterimage
            for afterimage in self.afterimages
            if afterimage.__update__(key_pressed, delta_t, objects, camera)
        ]

        if self.gool:
            [afterimage.__up__() for afterimage in self.afterimages]
            ...

        if self.death_f:
            if len(self.afterimages) == 0: self.kill()
            return

        self.afterimage_cool -= delta_t
        if randrange(4) == 0:
            self.afterimage_cool -= delta_t
            ...

        if self.afterimage_cool < 0:
            self.afterimages.append(Afterimage(
                [
                    p+randrange(s-15+1)
                    for p, s in zip(self.position, self.size)
                ],
                (15, 15),
                0.4
            ))
            self.afterimage_cool = 0.02
            ...

        if self.spawn:
            if self.control and key_pressed[pg.K_SPACE]:
                self.spawn = False
                ...
            return

        dash = False
        self.movement[1] += 35 * delta_t

        if self.control:
            self.movement[0] = 0
            if key_pressed[pg.K_LEFT]:
                self.movement[0] -= 240*delta_t
                ...
            if key_pressed[pg.K_RIGHT]:
                self.movement[0] += 240*delta_t
                ...

            self.fly_cool_count -= 1
            if key_pressed[pg.K_UP]:
                if self.is_land:
                    self.movement[1] = -7.8
                    self.is_land = False
                    self.fly_cool_count = self.fly_cool
                    ...
                elif self.fly_cool_count <= 0 and self.movement[1] > 0:
                    self.movement[1] = 0
                    self.fly_cool_count = self.fly_cool
                    ...
                ...

            self.dash_cool -= 1
            if key_pressed[pg.K_LSHIFT] and self.dash_cool < 0 and not self.movement[0] == 0:
                dash = True
                self.dash_cool = 30
                ...

            if key_pressed[pg.K_r]:
                self.death()
                ...

            ...

        lands = [
            obj
            for obj in objects
            if isinstance(obj, Land)
        ]

        for i in range(2):
            pre_pos = deepcopy(self.position)
            for _ in range(20 if i == 0 and dash else 1):
                self.position[i] += self.movement[i]
                self.rect[:2] = self.position
                for land in lands:
                    if self.rect.colliderect(land.rect):
                        if isinstance(land, Gool):
                            self.gool = True
                            self.death()
                            continue
                        if isinstance(land, CheckPoint):
                            self.spawn_point = land.pos_unit
                            continue
                        if isinstance(land, KillZone):
                            self.death()
                        if self.position[i] < land.position[i]:
                            self.position[i] = land.position[i] - self.size[i]
                            if i == 1: self.is_land = True
                            ...
                        else:
                            self.position[i] = land.position[i] + land.size[i]
                            ...
                        self.movement[i] = 0
                        ...
                    continue

                continue

            if i == 0 and dash:
                if pre_pos[0] < self.position[0]:
                    p1, p2 = pre_pos, self.position
                    ...
                else:
                    p1, p2 = self.position, pre_pos
                self.afterimages.append(Afterimage(
                    [
                        p
                        for p, s in zip(p1, self.size)
                    ],
                    [p2[0]-p1[0]+30, 30],
                    0.05
                ))

                ...

            continue
        self.rect[:2] = self.position
        if self.movement[1] >= 1: self.is_land = False

        return

    def __render__(self, master: Surface):
        [afterimage.__render__(master) for afterimage in self.afterimages]
        if not self.death_f and not self.spawn:
            super().__render__(master)
        return

    ...


class Land(Object):

    render_f = None

    def __init__(self, land_unit):
        super().__init__(
            [land_unit[0]*50, (land_unit[1]-12)*-50],
            [s*50 for s in land_unit[2:]]
        )
        self.render_f = False
        return

    def __start__(self, camera):
        self.render_f = self.rect.colliderect(camera.rect)
        return

    def __update__(self, key_pressed, delta_t, objects, camera):
        self.render_f = self.rect.colliderect(camera.rect)
        return

    def __render__(self, master: Surface):
        if self.render_f: super().__render__(master)
        return

    ...


class KillZone(Land):
    def __init__(self, land_unit):
        super().__init__(land_unit)
        self.__surface__.fill("Red")
        return

    ...


class Unseen(Land):
    def __init__(self, land_unit):
        super().__init__(land_unit)
        self.__surface__.set_alpha(0)
        return


class BackGroundRect(Object):
    alpha = None
    rm_alpha = None
    angle = None

    __base_surface__ = None
    base_position = None

    def __init__(self, camera):
        depth = 2
        pos = [
            camera.position[0]/depth-400+randrange(camera.size[0]+400),
            600
        ]
        side = randrange(1, 20)
        size = [side for _ in range(2)]
        super().__init__(pos, size,depth)
        self.base_position = pos
        self.alpha = randrange(120, 240)
        self.__surface__.fill((0, 0, 0, 0))
        self.__base_surface__ = pg.Surface(size)
        self.__base_surface__.fill((191, 191, 191))
        self.__surface__.set_alpha(self.alpha)
        self.rm_alpha = 1
        self.angle = randrange(0, 360)
        self.delta_t = 0
        return

    def __start__(self, camera): ...

    def __update__(self, key_pressed, delta_t, objects, camera):
        self.delta_t += delta_t
        if not self.delta_t > 1 / 20: return True
        rect = self.__surface__.get_rect()
        self.position[1] -= 1.5 * self.delta_t
        self.alpha -= self.rm_alpha
        if not self.alpha > 0: return False
        self.__surface__.set_alpha(self.alpha)
        return True

    ...


class BackGround(Object):

    delta_ts = None
    gen_t = 0.1
    objects = None

    def __init__(self):
        super().__init__((0, 0), (0, 0))
        self.delta_ts = 0
        self.objects = []
        self.limit = 50
        return

    def __start__(self, camera): ...

    def __update__(self, key_pressed, delta_t, objects, camera):
        self.delta_ts += delta_t
        if self.delta_ts > self.gen_t and len(self.objects) < self.limit:
            self.objects.append(BackGroundRect(camera))
            self.delta_ts -= self.gen_t
            ...

        self.objects = [
            obj
            for obj in self.objects
            if obj.__update__(key_pressed, delta_t, objects, camera)
        ]
        return

    def __render__(self, master: Surface):
        [obj.__render__(master) for obj in self.objects]
        return

    ...


class Text(Object):

    def __init__(self, text, position, size, font=None):
        super().__init__(position, (0, 0), 1.1)
        font = pg.font.SysFont(None, size)
        self.__surface__ = font.render(text, True, (0, 0, 0))
        return

    def __start__(self, camera): ...
    def __update__(self, key_pressed, delta_t, objects, camera): ...

    ...


class Texts(Object):

    texts = None
    charactor = None

    Spawn = list
    Tutorial = list

    def __init__(self):
        super().__init__((0, 0), (0, 0))
        self.texts = []
        self.charactor = None
        return

    def __start__(self, camera):
        self.add_text("Enter SPACE", (400, 250), 100)
        self.add_text("Enter SPACE", (2800, 250), 100)
        self.add_text("Enter SPACE", (1800, 250), 100)
        self.Spawn = copy(self.texts)
        self.texts = []
        self.add_text("Move [<-] and [->] key", (250, 250), 100)
        self.add_text("[^]", (1110, 250), 100)
        self.add_text("Jamp!!", (1040, 350), 100)
        self.add_text("[Left Shift]", (1430, 250), 100)
        self.add_text("Dash!!!", (1490, 350), 100)
        self.add_text("\Check point/", (1800, 350), 100)
        self.add_text("Enter R", (2900, 250), 100)
        self.add_text("Restart", (2900, 350), 100)
        self.add_text("Gool->", (6000, -450), 100)
        self.Tutorial = copy(self.texts)
        self.texts = []

        self.texts = self.Spawn
        return

    def __update__(self, key_pressed, delta_t, objects, camera):
        if not self.charactor in objects:
            char_list = [
                obj for obj in objects if isinstance(obj, Charactor)
            ]
            if len(char_list) > 0:
                self.charactor = char_list[0]
                ...
            self.texts = self.Spawn
            ...
        if key_pressed[pg.K_SPACE] and self.charactor.control:
            self.texts = self.Tutorial
            ...
        return

    def add_text(self, text, position, size, font=None):
        self.texts.append(Text(text, position, size, font))
        return

    def __render__(self, master):
        [text.__render__(master) for text in self.texts]
        return

    ...


class CheckPoint(Land):

    pos_unit = None
    check = None
    alpha = None

    def __init__(self, land_unit):
        super().__init__(land_unit)
        self.alpha = 127
        self.__surface__.fill("Black")
        self.__surface__.set_alpha(self.alpha)
        self.pos_unit = land_unit[:2]
        self.check = False
        return

    def __update__(self, key_pressed, delta_t, objects, camera):
        chara_object = [obj for obj in objects if isinstance(obj, Charactor)]
        for chara in chara_object:
            if self.rect.colliderect(chara):
                self.check = True
                ...
            continue
        if not self.check: return

        self.alpha -= 3
        self.__surface__ = pg.transform.rotozoom(self.__surface__, 0, 1.03)
        rect = self.__surface__.get_rect()
        self.position = [
            p-(rs-s)/2
            for p, s, rs in zip(self.position, self.size, rect[2:])
        ]
        self.size = rect[2:]
        self.__surface__.set_alpha(self.alpha)

        if self.alpha < 0: self.killing = True
        return

    def __render__(self, master):
        Object.__render__(self, master)
        return

    ...


class BackRect(Object):

    def __init__(self, rect_unit):
        super().__init__(
            [rect_unit[0] * 50, (rect_unit[1] - 12) * -50],
            [s * 50 for s in rect_unit[2:]],
        )
        self.__surface__.fill((63, 63, 63))
        return

    def __start__(self, camera): ...
    def __update__(self, key_pressed, delta_t, objects, camera): ...

    ...


class GoolRect(Object):

    base_position = None
    __base_surface__ = None
    angle = None
    roto = None
    alpha = None

    def __init__(self, rect_unit, roto):
        super().__init__(
            [rect_unit[0] * 50, (rect_unit[1] - 12) * -50],
            [s * 50 for s in rect_unit[2:]]
        )
        self.base_position = deepcopy(self.position)
        self.__base_surface__ = pg.Surface(self.size)
        self.__base_surface__.fill("Gray")
        self.alpha = 127
        self.angle = 0
        self.roto = roto
        return

    def __start__(self, camera): ...
    def __update__(self, key_pressed, delta_t, objects, camera):
        self.__surface__ = pg.transform.rotozoom(
            self.__base_surface__, self.angle, 1
        )
        self.__surface__.set_colorkey("Black")
        rect = self.__surface__.get_rect()
        self.position = [
            bp + ss//2 - rc
            for bp, ss, rc in zip(self.base_position, self.size, rect.center)
        ]
        self.__surface__.set_alpha(self.alpha)
        self.angle += self.roto
        return True

    ...


class Gool(Land):

    objects = None

    def __init__(self, land_unit):
        self_land_unit = list(land_unit)
        self_land_unit[2:] = [lu*0.50 for lu in land_unit[2:]]
        self_land_unit[:2] = [
            lp+ls/a
            for lp, ls, a in zip(
                self_land_unit[:2], self_land_unit[2:], (2, -2)
            )
        ]
        super().__init__(self_land_unit)
        self.objects = [GoolRect(land_unit, i) for i in range(-1, 2, 2)]
        return

    def __start__(self, camera): ...
    def __update__(self, key_pressed, delta_t, objects, camera):
        self.objects = [
            obj
            for obj in self.objects
            if obj.__update__(key_pressed, delta_t, objects, camera)
        ]
        return
    def __render__(self, master):
        [obj.__render__(master) for obj in self.objects]
        return

    ...


class StartCameraWork(NoneType):

    def __init__(self, position):
        super().__init__(position, (0, 0))
        return

    def __update__(self, key_pressed, delta_t, objects, camera):
        chars = [obj for obj in objects if isinstance(obj, Charactor)]
        if len(chars) == 0: return
        char = chars[0]
        self.movement = [
            3*(cp-sp)/abs(cp-sp) if 3 < abs(cp-sp) else
            (cp-sp)/abs(cp-sp) if 0 < abs(cp-sp) else
            0
            for sp, cp in zip(self.position, char.position)
        ]
        self.position = [p+m for p, m in zip(self.position, self.movement)]
        if sum(map(int, (map(abs, self.movement)))) == 0:
            self.killing = True
            ...
        return
