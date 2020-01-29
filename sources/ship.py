# -*- coding: Utf-8 -*-

from sources.weapon import *
import random
import math


class MasterSprite(pygame.sprite.Sprite):
    """Attributs communs à tous les sprites"""

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)


class SpaceShip(pygame.sprite.Sprite):
    """Vaisseau principale du joueur
    Retourne  : objet player_ship
    Méthodes  : update, get_keys, fire
    Attributs : life, shied, speed, movepos, fireSpeed, power, radius, stype"""

    def __init__(self, appli, x, y, speed=5):
        self._layer = PLAYER_LAYER
        group = appli.allSprites
        pygame.sprite.Sprite.__init__(self, group)
        self.image, self.rect = load_image('player_green1.png')
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.radius = int(self.rect.width * .90 / 2)  # pour collide circle
        self.stype = 'player'      # 'type' de sprite
        self.appli = appli         # réf. de la fenêtre principale
        self.rect.midtop = (x, y)  # positionement milieu haut
        self.speed = speed         # vitesse du vaisseau
        self.life = 3              # vie du joueur
        self.shield = 10           # bouclier du joueur
        self.fireSpeed = 250       # interval entre chaque tir (ms.)
        self.power = 1             # puissance du vaisseau
        self.lastfire = 0          # indicateur de dernier tir
        self.movepos = [0, 0]      # indicateur de déplacement

    def update(self):
        self.movepos = [0, 0]
        self.get_keys()
        newpos = self.rect.move(self.movepos)  # x, y, largeur, hauteur
        if self.area.contains(newpos):
            self.rect = newpos
        if not self.life:
            self.kill()
        pygame.event.pump()

    def get_keys(self):
        """Déplacement et tir du joueur"""
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.movepos = [0, -self.speed]
        if keys[pygame.K_DOWN]:
            self.movepos = [0, self.speed]
        if keys[pygame.K_LEFT]:
            self.movepos = [-self.speed, 0]
        if keys[pygame.K_RIGHT]:
            self.movepos = [self.speed, 0]
        if keys[pygame.K_SPACE]:
            self.fire()

    def fire(self):
        """Déclenche les tirs de lasers"""
        now = pygame.time.get_ticks()
        if now - self.lastfire > self.fireSpeed:
            self.lastfire = now
            if self.power == 0 or self.power > 1:
                LaserPlayer(self, sens='middle')  # middle laser
            elif self.power == 1:
                LaserPlayer(self, sens='left')  # left laser
                LaserPlayer(self, sens='right')  # right laser
            if self.power > 1:
                LaserPlayer(self, sens='right', angle=100)
                LaserPlayer(self, sens='left', angle=80)


class PirateShip1(pygame.sprite.Sprite):
    """Enemy type 1 : apparait en haut de la carte et dépl. horizontal
    Retourne  : objet enemy_ship
    Méthodes  : update, auto_fire
    Attributs : appli, life, speed, fireSpeed, sens, maxh, stype, movepos"""

    def __init__(self, appli, maxh=20, xh=200, speed=1):
        self._layer = ENEMY_LAYER
        group = appli.allSprites, appli.enemies
        pygame.sprite.Sprite.__init__(self, group)
        self.image, self.rect = load_image('enemy_ship1.png')
        self.rect = self.image.get_rect()
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.stype = 'pirate'  # 'type' de sprite
        self.appli = appli     # réf. de la fenêtre principale
        self.rect.midbottom = (xh, 0)  # position de départ
        self.lastFire = 0      # indicateur de dernier tir
        self.fireSpeed = 800 // appli.difficulty
        self.speed = speed  # vitesse de déplacement
        self.maxh = maxh    # hauteur maximale
        self.life = 3       # points de vie
        self.sens = random.randrange(-1, 2, 2)  # sens de déplacement
        self.movepos = [0, self.speed]  # direction

    def update(self):
        self.auto_fire()
        newpos = self.rect.move(self.movepos)  # x, y, largeur, hauteur
        if self.sens and newpos[1] > DASHSIZE + self.maxh:
            self.speed = self.speed * self.sens
            self.sens = 0
            self.movepos = [self.speed, 0]  # déplacement horizontal
        elif not self.area.contains(newpos) and not self.sens:
            self.speed = -self.speed
            self.movepos = [self.speed, 0]
            newpos = self.rect.move(self.speed, 0)
        self.rect = newpos
        pygame.event.pump()

    def auto_fire(self):
        """Tir automatique du vaisseau ennemi"""
        now = pygame.time.get_ticks()
        if now - self.lastFire > self.fireSpeed and self.rect[1] > 0:
            self.lastFire = now
            LaserEnemy(self, sens='left', side='enemy', speed=-5)
            LaserEnemy(self, sens='right', side='enemy', speed=-5)


class PirateShip2(pygame.sprite.Sprite):
    """Enemy type 2 : apparaît sur le coté de la carte et dépl. horizontal
    Retourne  : object PirateShip2
    Méthodes  : update, autofire
    Attributs : speed, fireSpeed, life, sens, level, stype, movepos """

    def __init__(self, appli, sens=1, speed=1, life=3):
        self._layer = ENEMY_LAYER
        group = appli.allSprites, appli.enemies
        pygame.sprite.Sprite.__init__(self, group)
        self.image, self.rect = load_image('enemy_ship2.png')
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.stype = 'pirate'
        self.appli = appli  # réf. application principale
        self.sens = sens    # apparition côté droit ou gauche de la carte
        self.life = life    # points de vie
        self.speed = speed * sens  # vitesse initiale
        self.fireSpeed = 600 // appli.difficulty
        self.lastFire = 0
        # Positionner le vaisseau
        x = -self.rect[3]
        if self.sens < 0:
            x = self.area.width + self.rect[3]  # coté droit de la fenêtre
        self.rect.midtop = (x, DASHSIZE-1)
        self.movepos = [self.speed, 0]

    def update(self):
        self.auto_fire()
        newpos = self.rect.move(self.movepos)
        self.rect = newpos
        if (self.rect[0] > self.area.width and self.sens > 0) \
                or (self.rect[0] < -self.rect[3] and self.sens < 0):
            self.appli.nbEnemy -= 1
            self.kill()

    def auto_fire(self):
        now = pygame.time.get_ticks()
        if now - self.lastFire > self.fireSpeed:
            self.lastFire = now
            LaserEnemy(self, sens='left', side='enemy', speed=-5)
            LaserEnemy(self, sens='right', side='enemy', speed=-5)


class Kamikaze(pygame.sprite.Sprite):
    """Troisième type de vaisseau ennemie : avance vertical et tir auto
    Reourne   : objet Kamikaze
    Méthodes  : update, auto_fire
    Attributs : speed, posx, fireSpeed, level, life, stype, movepos"""

    def __init__(self, appli, speed=1, life=3, posx=50):
        self._layer = ENEMY_LAYER
        group = appli.allSprites, appli.enemies
        pygame.sprite.Sprite.__init__(self, group)
        self.image, self.rect = load_image('enemy_ship3.png')
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.posx = posx
        self.rect.midbottom = (posx, 0)  # position de départ
        self.appli = appli  # application principale
        self.speed = speed  # vitesse
        self.life = life    # points de vie
        self.stype = 'pirate'  # catégorie de sprite
        self.fireSpeed = 3000 // appli.difficulty
        self.lastFire = 0
        self.movepos = [0, speed]

    def update(self):
        self.auto_fire()
        newpos = self.rect.move(self.movepos)
        self.rect = newpos
        if newpos[1] > self.area.height:
            self.rect.midbottom = (self.rect.centerx, -40)
            # self.kill()
            # self.appli.nbEnemy -= 1

    def auto_fire(self):
        now = pygame.time.get_ticks()
        if now - self.fireSpeed > self.lastFire:
            self.lastFire = now
            LaserRotation(self, speed=3, rota=True)


class BossShip1(pygame.sprite.Sprite):
    """Boss ship type 1
    Retourne   : objet BossShip
    Méthodes   : update, auto_fire
    Attributs  : power, speed, maxh, fireSpeed, level, life, movepos"""

    def __init__(self, appli, speed=1, sens=-1):
        self._layer = ENEMY_LAYER
        group = appli.allSprites, appli.enemies
        pygame.sprite.Sprite.__init__(self, group)
        self.image, self.rect = load_image('enemy_boss1.png')
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        posx = random.randrange(self.rect[2], WIDTH - self.rect[2])
        self.rect.midbottom = (posx, 0)
        self.stype = 'boss'
        self.appli = appli         # réf. de l'application principale
        self.speed = speed         # vitesse de déplacement
        self.sens = sens           # sens du déplacement
        self.maxh = self.rect[3]   # descente maximale
        self.movepos = [0, speed]  # direction
        self.lastfire = 0          # indicateur de dernier tir
        self.life = 15 + appli.difficulty * 10
        self.fireSpeed = 450 - appli.difficulty * 50

    def update(self):
        self.auto_fire()
        newpos = self.rect.move(self.movepos)
        if self.sens and newpos[1] > DASHSIZE:
            self.speed = self.speed * self.sens
            self.sens = 0
            self.movepos = [self.speed, 0]  # déplacament horizontal
        elif not self.area.contains(newpos) and not self.sens:
            self.speed = -self.speed
            self.movepos = [self.speed, 0]
            newpos = self.rect.move(self.movepos)
        self.rect = newpos
        pygame.event.pump()

    def auto_fire(self):
        """Tire automatique du boss : plusieurs armes (à terminer)"""
        now = pygame.time.get_ticks()
        if now - self.lastfire > self.fireSpeed and self.rect[1] > 0:
            self.lastfire = now
            LaserEnemy(self, sens='left', side='boss', speed=-3)
            LaserEnemy(self, sens='right', side='boss', speed=-3)


class BossShip2(pygame.sprite.Sprite):
    """Boss type 2 : circle move
    Return : object BossShip2
    Methods : update, set_angle, auto_fire
    Attributes : life, speed, fireSpeed, vx, vy, dx, dy"""

    def __init__(self, appli):
        self._layer = ENEMY_LAYER
        group = appli.allSprites, appli.enemies
        pygame.sprite.Sprite.__init__(self, group)
        self.image, self.rect = load_image('enemy_boss2.png')
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.rect.midbottom = (WIDTH // 2, 0)
        self.stype = 'boss'
        self.appli = appli  # main application
        self.life = 20 + appli.difficulty * 10
        self.fireSpeed = 450 - appli.difficulty * 50
        self.lastFire = 0
        self.dx, self.dy = 1.8, 0.6  # 'pas' de déplacement en cercle
        self.vx, self.vy = 0, 0  # actual speed
        self.rectx = self.rect.centerx
        self.recty = self.rect.centery
        self.angle = 0  # degree

    def update(self):
        self.auto_fire()
        if self.rect[1] < DASHSIZE:
            newpos = self.rect.move(0, 1)
            self.rect = newpos
            self.rectx, self.recty = self.rect.centerx, self.rect.centery
        else:
            self.set_angle()
            self.rectx += self.vx
            self.recty += self.vy
            self.rect.centerx = self.rectx
            self.rect.centery = self.recty

    def set_angle(self):
        self.angle += 0.5
        angle_rad = math.radians(self.angle)
        self.vx = self.dx * math.cos(angle_rad)
        self.vy = self.dy * math.sin(angle_rad)

    def auto_fire(self):
        now = pygame.time.get_ticks()
        if now - self.lastFire > self.fireSpeed:
            self.lastFire = now
            LaserEnemy(self, sens='left', side='boss', speed=-3)
            LaserEnemy(self, sens='right', side='boss', speed=-3)
