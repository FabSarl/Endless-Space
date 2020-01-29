# -*- coding: Utf-8 -*-

import pygame
import os

if not pygame.mixer:
    print("Attention, son désactivé")
if not pygame.font:
    print("Attention, polices désactivées")

# Game options/settings
WIDTH, HEIGHT = 590, 680  # 580, 690
HW, HH = WIDTH // 2, HEIGHT // 2
FPS = 120
BONUSTIME = 8000  # intervalle minimum (ms.) entre les bonus
METEORTIME = 500  # intervalle minimum (ms.) entre les météors
DASHSIZE = 45     # hauteur du tableau de bord

# Game properties
BONUS_LAYER = 0
PLAYER_LAYER = 1
METEOR_LAYER = 2
ENEMY_LAYER = 3
WEAPONP_LAYER = 4
WEAPONE_LAYER = 5
EXPLO_LAYER = 6
TEXT_LAYER = 7

# Define colors
BLACK = (0, 0, 0)
RED = (189, 62, 62)
WHITE = (200, 200, 200)
YELLOW = (255, 215, 0)
ORANGE = (234, 148, 8)
BLUE = (44, 105, 148)


def load_sound(name):
    """Charge un son ou retourne une classe fictive"""
    class NoneSound:
        def play(self): pass

    if not pygame.mixer:
        return NoneSound()
    fullname = os.path.join('sources/sound', name)
    try:
        sound = pygame.mixer.Sound(fullname)
    except pygame.error as message:
        print('Impossible de charger le son :', name)
        pygame.quit()
        raise SystemExit(message)
    return sound


def load_image(name, folder=''):
    """Charge une image et retourne un objet image"""
    folder = 'sources/graphic/' + folder
    fullname = os.path.join(folder, name)
    try:
        image = pygame.image.load(fullname)
        if image.get_alpha() is None:
            image = image.convert()
        else:
            image = image.convert_alpha()
    except pygame.error as message:
        print("Impossible de charger l'image :", fullname)
        pygame.quit()
        raise SystemExit(message)
    return image, image.get_rect()


def read_write_highscore(action, highscore=0):
    file = os.path.join('sources/graphic/', 'highscore')
    if action == 'read':
        try:
            with open(file, 'r') as f:
                highscore = int(f.read())
        except FileNotFoundError:
            highscore = 0
        except ValueError:
            highscore = 0
        return highscore
    elif action == 'write':
        with open(file, 'w') as f:
            f.write(str(highscore))
        return int(highscore)


# --- Chargement des sons et des graphismes du jeu --- #


def load_game_sounds():
    sound = {'explo1': load_sound('explo1.ogg'),
             'explo2': load_sound('explo2.ogg'),
             'loseLife': load_sound('loseLife.ogg'),
             'shieldUp': load_sound('shieldUp.ogg'),
             'powerUp': load_sound('powerUp.wav'),
             'starUp': load_sound('starUp.wav'),
             'highscore': load_sound('highscore.ogg')}
    return sound


def load_game_images(load=''):
    # Chargement des explosions
    if load == 'explo':
        small, medium, large, sonic = [], [], [], []
        for i in range(9):
            # Regular explosion
            image = load_image('regular_explo%s.png' % i, 'explosions')[0]
            imgsmall = pygame.transform.scale(image, (45, 45))  # small
            small.append((imgsmall, imgsmall.get_rect()))
            imgmedium = pygame.transform.scale(image, (75, 75))  # medium
            medium.append((imgmedium, imgmedium.get_rect()))
            large.append((image, image.get_rect()))  # large : real size
            # Sonic explosion
            image = load_image('sonic_explo%s.png' % i, 'explosions')[0]
            sonic.append((image, image.get_rect()))
        explo = {'small': small, 'medium': medium,
                 'large': large, 'sonic': sonic}
        return explo
    # Chargement des météorites
    if load == 'meteor':
        meteor = []
        for i in range(6):
            image, rect = load_image('meteor%s.png' % i)
            meteor.append([(image, rect), i+1])
        return meteor
    # Chargement des bonus
    if load == 'bonus':
        bonus = {'shield': (), 'power': (), 'star': (), 'powerdown': ()}
        for key in bonus:
            image, rect = load_image('bonus_%s.png' % key)
            bonus[key] = image, rect
        return bonus
    # Chargements des lasers et des vaisseaux -> A REVOIR
    if load == 'laser':
        laser = {'laser_green1': (), 'laser_red1': (),
                 'laser_red2': (), 'laser_red3': ()}
        for key in laser:
            image, rect = load_image('%s.png' % key)
            laser[key] = image, rect
        return laser
