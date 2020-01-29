# -*- coding: Utf-8 -*-

from sources.resources import *
import random
import math


class LaserEnemy(pygame.sprite.Sprite):
    """Laser déclenché par les boss ou un ennemi standard
    Retourne  : objet laser
    Methodes  : update,
    Attributs : object: ship, speed, area, damage, movepos"""

    def __init__(self, ship, sens='middle', side='enemy', speed=10):
        self._layer = WEAPONE_LAYER
        group = ship.appli.allSprites, ship.appli.weaponE
        pygame.sprite.Sprite.__init__(self, group)
        self.stype = 'laser'  # A SUPPRIMER
        if side == 'enemy':
            self.image, self.rect = load_image('laser_red1.png')
        elif side == 'boss':
            self.image, self.rect = load_image('laser_red3.png')
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.movepos = [0, -speed]
        self.damage = 1
        # Droit, gauche ou milieu du vaisseau
        if sens == 'right':
            if speed < 0:
                x, y = ship.rect.bottomleft
                self.rect.midtop = (x+15, y)
        elif sens == 'left':
            if speed < 0:
                x, y = ship.rect.bottomright
                self.rect.midtop = (x-15, y)
        elif sens == 'middle':
            x, y = ship.rect.midtop
            self.rect.midbottom = (x, y + 10)

    def update(self):
        newpos = self.rect.move(self.movepos)  # x, y, largeur, hauteur
        if self.area.contains(newpos):
            self.rect = newpos
        else:
            self.kill()
        pygame.event.pump()


class LaserPlayer(pygame.sprite.Sprite):
    """Laser du joueur, peut recevoir un angle de tir
    Retourne  : object LaserPlayer
    Méthodes  : update, set_angle
    Attributs : object: ship, area, sens, movepos, angle, dx, dy, vx, vy"""

    def __init__(self, ship, sens='middle', angle=90, dx=-10, dy=-10):
        global rot
        self._layer = WEAPONP_LAYER
        group = ship.appli.allSprites, ship.appli.weaponP
        pygame.sprite.Sprite.__init__(self, group)
        self.image, self.rect = load_image('laser_green1.png')
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.stype = 'laser'  # A SUPPRIMER
        if sens == 'middle':
            x, y = ship.rect.midtop[0], ship.rect.midtop[1] + 10
        elif sens == 'right':
            x, y = ship.rect.midright[0] - 5, ship.rect.midright[1]
            rot = -10
        else:
            x, y = ship.rect.midleft[0] - 5, ship.rect.midleft[1]
            if angle == 90:
                x += 10
            rot = 10
        self.rect.midbottom = (x, y)
        self.rectx = self.rect.centerx
        self.recty = self.rect.centery
        if angle != 90:
            self.image = pygame.transform.rotate(self.image, rot)
        self.dx, self.dy = dx, dy  # 'pas' de déplacement
        self.vx, self.vy = 0, 0    # vitesse de déplacement x et y actuelle
        self.angle = angle  # angle de déplacement en degrés

    def update(self):
        angle_rad = math.radians(self.angle)
        self.vx = self.dx * math.cos(angle_rad)
        self.vy = self.dy * math.sin(angle_rad)
        self.rectx += self.vx
        self.recty += self.vy
        self.rect.centerx = self.rectx
        self.rect.centery = self.recty
        if not self.area.contains(self.rect):
            self.kill()
        pygame.event.pump()


class LaserRotation(pygame.sprite.Sprite):
    """Laser qui a la possibilité de tourner sur lui même
    retourne  : object LaserEnemy
    méthodes  : update, rotate
    attributs : object : PirateShip, speed, damage, rotation, movepos"""

    def __init__(self, ship, speed=5, damage=1, rota=False):
        self._layer = WEAPONE_LAYER
        group = ship.appli.allSprites, ship.appli.weaponE
        pygame.sprite.Sprite.__init__(self, group)
        self.image, self.rect = load_image('laser_red2.png')
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.stype = 'laser'  # A SUPPRIMER
        if rota:
            self.rot = rota
            self.rotation = 0   # rotation actuelle
            self.rotSpeed = 10  # vitesse de rotation
            self.lastRotation = 0
            self.original = self.image
        self.rect.midbottom = ship.rect.midbottom
        self.damage = damage
        self.enemy = ship  # réf. du vaisseau déclencheur
        self.speed = speed    # vitesse de déplacement
        self.movepos = [0, speed]

    def update(self):
        if self.rot:
            self.rotate()
        newpos = self.rect.move(self.movepos)
        self.rect = newpos
        if newpos[1] > self.area.height:
            self.kill()
        pygame.event.pump()

    def rotate(self):
        now = pygame.time.get_ticks()
        if now - self.lastRotation > 50:
            self.lastRotation = now
            center = self.rect.center
            self.rotation += self.rotSpeed
            self.image = pygame.transform.rotate(self.original, self.rotation)
            self.rect = self.image.get_rect(center=center)


class Meteorite(pygame.sprite.Sprite):
    """Meteorites en rotation qui peuvent entrer en collision avec le joueur
    Retourne  : objet meteorite
    Méthodes  : update, rotate
    Attributs : speed, rotation, rotSpeed, lastUpate, life, size, movepos"""

    def __init__(self, appli, meteor, size=1, speedx=0, speedy=1, field=False):
        self._layer = METEOR_LAYER
        group = appli.allSprites, appli.meteors
        pygame.sprite.Sprite.__init__(self, group)
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.image, self.rect = meteor
        self.radius = int(self.rect.width * .90 / 2)  # radius pour coll. circle
        self.original = self.image  # image original pour la rotation
        self.stype = 'meteor'  # 'type' de sprite
        self.size = size       # dimension du météor
        # Position de départ
        self.rect.x = random.randrange(self.area.width-self.rect.width)
        self.rect.y = -self.rect[3]
        # Déplacement aléatoire
        if field:
            speedy = random.randrange(1, 4)
            speedx = random.randrange(-1, 2)
        self.movepos = [speedx, speedy]
        self.rotation = 0
        self.rotSpeed = random.randrange(-8, 8)     # vitesse de rotation
        self.lastUpdate = pygame.time.get_ticks()   # 'témoin' de dernière rot.

    def update(self):
        self.rotate()

        newpos = self.rect.move(self.movepos)  # x, y, largeur, hauteur
        if newpos[1] < self.area[3]:
            self.rect = newpos
        else:
            self.kill()
        pygame.event.pump()

    def rotate(self):
        now = pygame.time.get_ticks()
        if now - self.lastUpdate > 50:
            self.lastUpdate = now
            center = self.rect.center
            self.rotation += self.rotSpeed
            rotate = pygame.transform.rotate
            self.image = rotate(self.original, self.rotation)
            self.rect = self.image.get_rect(center=center)


class PowerUp(pygame.sprite.Sprite):
    """Apparition des bonus pour l'arme et le bouclier du joueur
    Retourne  : objet PowerUp
    Méthodes  : update
    Attributs : btype, speed, area, movepos"""

    def __init__(self, appli, bonus, btype='shield', speed=2):
        self._layer = BONUS_LAYER
        group = appli.allSprites, appli.powerup
        pygame.sprite.Sprite.__init__(self, group)
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.image, self.rect = bonus
        self.btype = btype  # type de bonus
        self.speed = speed  # vitesse du bonus
        px = random.randrange(self.rect.width, self.area.width-self.rect.width)
        self.rect.midbottom = (px, 0)
        self.movepos = [0, speed]

    def update(self):
        newpos = self.rect.move(self.movepos)
        if newpos[1] < self.area[3]:
            self.rect = newpos
        else:
            self.kill()
        pygame.event.pump()


class Explosion(pygame.sprite.Sprite):
    """Animation d'une exposion avec une liste d'image
    Retourne  : objet explosion
    Méthodes  : update
    Attributs : listExplo, frameRate, lastExplo, frame"""

    def __init__(self, appli, x, y, explo, fps=75):
        self._layer = WEAPONE_LAYER
        group = appli.allSprites, appli.explosions
        pygame.sprite.Sprite.__init__(self, group)
        self.image, self.rect = explo[0][0], explo[0][1]
        self.listExplo = explo  # liste des explosions
        self.frameRate = fps    # intervalle (ms.) entre les explosions
        self.lastExplo = 0      # indicateur de dernière explosion
        self.frame = 0          # image actuelle de l'explosion
        # Ajuster les images aux coord. définis
        for i in range(len(explo)):
            self.listExplo[i][1].midtop = (x, y)  # milieu haut de l'explosion

    def update(self):
        now = pygame.time.get_ticks()
        self.image = self.listExplo[self.frame][0]
        self.rect = self.listExplo[self.frame][1]
        if now - self.lastExplo > self.frameRate:
            self.lastExplo = now
            self.frame += 1
            if self.frame == len(self.listExplo):
                self.kill()
            else:
                pos = self.rect.move(0, 0)
                self.rect = pos
        pygame.event.pump()
