#! /usr/bin/python3
# -*- coding: Utf-8 -*-

####################################
# Shoot'em up : Endless Space      #
# Version : Alpha 0.3              #
# Author : Fab Sarl                #
# Licence : MIT                    #
####################################

try:
    import sys
    import pygame
    import os
    import time
    from random import randrange
    from pygame.locals import *
    from sources.ship import *
    from sources.weapon import *
    from sources.menu import *
    from sources.resources import *
except ImportError as err:
    print("Impossible de charger le module. %s" % err)
    sys.exit(2)


class Application(object):
    """Partie principale de l'application : boucle du jeu, gère l'apparition et
    les collision des sprites et redémarre une nouvelle partie
    Méthodes : mainloop, spawn_sprite, collide_test, hit_sprite, new_game, cheat
    """

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Endless Space")
        self.background = load_image('background_blue.png')[0]
        self.level = 1.  # niveau du jeu
        self.difficulty = 1  # difficultée actuelle
        self.meteorTime = METEORTIME  # intervalle (ms.) entre les météorites
        self.bonusTime = BONUSTIME    # intervalle (ms.) entre les bonus
        self.newMeteor = self.meteorTime  # permet de définir
        self.newBonus = self.bonusTime    # un intervalle de temps aléatoire
        self.enemyTime = 1500  # intervalle (ms.) entre les ennemis
        self.lastMeteor = 0    # temps (ms.)
        self.lastEnemy = 0     # du dernier
        self.lastBonus = 0     # lancement
        self.rand = 0   # pos. aléat. de départ de la vague ennemi type 1
        self.sens = 0   # pos. droite ou gauche du déplacement des types 2
        self.spawn = 0  # nombre d'ennemis instanciés
        self.maxEnemy = 1  # nombre max. d'ennemis en jeu
        self.nbEnemy = 0   # nombre d'ennemis actuellement présent
        self.kamikaze = True      # autorisation vague de kamikaze
        self.bossAlive = False    # 'marqueur' de boss en jeu
        self.meteorField = False  # champ de météors en cours
        self.gameOver = False     # fin de la partie
        self.nbMeteor = 0  # nb. météors max par champ
        self.score = 0     # score total
        # Initialiser les graphismes et les sons
        self.imgMeteor = load_game_images('meteor')  # liste des météors
        self.imgExplo = load_game_images('explo')    # dict. des explosions
        self.imgBonus = load_game_images('bonus')    # dict. des bonus
        self.imgLaser = load_game_images('laser')    # dict. des lasers
        # Initialiser les groupes de sprites
        self.allSprites = pygame.sprite.LayeredUpdates()
        self.powerup = pygame.sprite.Group()
        self.meteors = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.weaponP = pygame.sprite.Group()
        self.weaponE = pygame.sprite.Group()
        self.explosions = pygame.sprite.Group()
        self.text = pygame.sprite.Group()
        self.highscore = read_write_highscore('read')  # charger le highscore
        self.txtScore = Text(self, str(self.score), WIDTH / 1.8, 30)
        self.txtLevel = Text(self, str(self.level), WIDTH / 1.8, 10)
        # Initialiser le joueur, le menu et l'horloge
        self.player = SpaceShip(self, WIDTH / 2, HEIGHT - 100)
        self.menu = Menu(self)
        self.exit = False  # back to main menu
        self.clock = pygame.time.Clock()

    def mainloop(self):
        """Boucle principale du jeu"""
        self.menu.start_menu()
        pygame.mixer.music.fadeout(300)
        self.menu.jukebox(nextm=True)
        while 1:
            self.clock.tick(FPS)
            # CHEAT
            # self.cheat()
            # - Events handler - #
            for event in pygame.event.get():
                # Pause menu
                if event.type == KEYDOWN and event.key == K_RETURN:
                    exitgame = self.menu.pause()
                    if exitgame:
                        return
                # Restart game
                if (event.type == KEYDOWN and event.key == K_c
                        and self.gameOver) or self.exit:
                    pygame.mixer.music.fadeout(500)
                    self.menu.start_menu()
                    self.newgame()
                # Exit game
                if event.type == QUIT:
                    self.quit()

            # - Start game - #
            self.allSprites.update()
            self.spawn_sprite()
            if not self.gameOver:
                self.collide_test()
            # Blitter le backgound et dessiner les sprites
            self.screen.blit(self.background, (0, 0))
            self.allSprites.draw(self.screen)
            self.menu.dashboard(self, self.player)
            pygame.display.flip()

    def spawn_sprite(self):
        now = pygame.time.get_ticks()
        # - Apparition du boss - #
        if ((self.maxEnemy >= 3 + int(self.level + 1)) or self.maxEnemy == 7)\
                and not self.bossAlive:
            self.bossAlive = True
            if (self.level - int(self.level)) and self.level >= 2:
                BossShip2(self)  # level = *.5
            else:
                BossShip1(self)
            self.maxEnemy = 1

        # - Apparition des météorites - #
        if now - self.lastMeteor > self.newMeteor:
            self.lastMeteor = now
            # Champ de météorite
            if self.meteorField and self.nbMeteor == 0:
                self.meteorTime = 45 - int(self.level)
                if self.meteorTime < 10:
                    self.meteorTime = 10
                self.nbMeteor = 1
                self.bonusTime = int(BONUSTIME / 3)  # increase bonus
                self.lastBonus = now
                self.newBonus = randrange(self.bonusTime, self.bonusTime * 2)
            if self.nbMeteor:
                self.nbMeteor += 1
            # Meteor Wave ending
            if self.nbMeteor > 250:
                self.level += 0.5  # real level up
                if self.level == 2 or self.level == 3:
                    self.menu.jukebox(nextm=True)  # next song
                    self.difficulty += 1
                # TODO: need real end
                if self.level == 6:
                    self.difficulty += 1
                self.meteorField = False
                self.bonusTime = BONUSTIME
                self.nbMeteor = 0
                self.meteorTime = 400
                self.lastEnemy = now
            # Tirage aléatoire d'un nouvel intervalle de temps
            self.newMeteor = randrange(self.meteorTime, self.meteorTime * 4)
            i = random.randrange(len(self.imgMeteor))
            meteor = self.imgMeteor[i][0]  # image + rect
            size = self.imgMeteor[i][1]    # taille du météor
            field = self.meteorField
            Meteorite(self, meteor, size, field=field)

        # - Apparitions des ennemis - #
        if (now - self.lastEnemy > self.enemyTime) \
                and self.spawn < self.maxEnemy and not self.bossAlive \
                and not self.meteorField:
            self.lastEnemy = now
            if self.maxEnemy <= 3:
                if not self.rand:
                    self.rand = randrange(100, WIDTH - 101)
                xh = self.rand  # position de départ
                mh = self.spawn * 60  # descente maximale
                PirateShip1(self, mh, xh)
            else:
                # Tirage d'une vague de kamikaze ou d'un pirate type 2
                rnd = randrange(0, 4)
                if rnd and self.maxEnemy < 6 and self.kamikaze:
                    maxwidth = int(WIDTH / self.maxEnemy)
                    for i in range(70, WIDTH, maxwidth):
                        Kamikaze(self, posx=i)
                    self.spawn += self.maxEnemy - 1
                    self.nbEnemy += self.maxEnemy - 1
                else:
                    self.kamikaze = False
                    if not self.sens:
                        self.sens = random.randrange(-1, 2, 2)
                    PirateShip2(self, self.sens)
            self.spawn += 1
            self.nbEnemy += 1
        # Tous les ennemis de la vague en cours ont été détruits
        if self.spawn == self.maxEnemy and not self.nbEnemy:
            self.spawn, self.nbEnemy, self.sens, self.rand = 0, 0, 0, 0
            self.kamikaze = True
            self.maxEnemy += 1
            self.lastEnemy = now - self.enemyTime / 2  # wait 1/2 intervalle

        # - Apparition des bonus - #
        if now - self.lastBonus > self.newBonus:
            self.lastBonus = now
            self.newBonus = randrange(self.bonusTime, self.bonusTime * 2)
            # Tirage du type de bonus
            rndtype = random.randrange(0, 11)
            if rndtype > 5:
                btype = 'power'
            elif rndtype > 0:
                btype = 'shield'
            else:
                btype = 'star'
            PowerUp(self, self.imgBonus[btype], btype)

    def collide_test(self):
        # Test des collisions des armes du joueur et des ennemis
        enemies = pygame.sprite.\
            groupcollide(self.enemies, self.weaponP, False, True)
        for enemy in enemies:
            self.hit_sprite(sprite=enemy, score=(500 * int(self.level)))
        # Test des collisions des armes du joueur et des météorites
        for meteor in pygame.sprite.groupcollide(self.meteors, self.weaponP,
                                                 True, True).keys():
            self.hit_sprite(meteor, score=meteor.size*10*int(self.level))
        # Test des collisions des armes des ennemis avec le joueur
        weapons = pygame.sprite.spritecollide(self.player, self.weaponE, True)
        for weapon in weapons:
            self.hit_sprite(sprite=self.player, damage=weapon.damage)
        # Test des collisions du joueur et des ennemis
        enemies = pygame.sprite.spritecollide(self.player, self.enemies, False)
        for enemy in enemies:
            self.hit_sprite(self.player)
            self.hit_sprite(enemy, score=500*int(self.level))
        # Test des collisions du joueur et des météorites
        for meteor in pygame.sprite.spritecollide(
                self.player, self.meteors, True, pygame.sprite.collide_circle):
            self.hit_sprite(self.player, explo=False)
            self.hit_sprite(meteor, score=meteor.size*10*int(self.level))
        # - Test de capture des Power Up - #
        for bonus in pygame.sprite.\
                spritecollide(self.player, self.powerup, True):
            if bonus.btype == 'shield':
                if self.player.shield <= 8:
                    self.player.shield += 2
                self.menu.play_sound('shieldUp')
            elif bonus.btype == 'power':
                if self.player.power < 3:
                    self.player.power += 1
                self.menu.play_sound('powerUp')
            elif bonus.btype == 'star':
                if self.player.shield < 10:
                    self.player.shield = 10  # recharger le bouclier
                if self.player.power < 3:
                    self.player.power = 3  # puissance max.
                self.score += 1000 * int(self.level)
                self.menu.play_sound('starUp')
            self.score += 500 * int(self.level)

    def hit_sprite(self, sprite, score=100, damage=1, explo=True):
        # - Hit sur le joueur - #
        if sprite.stype == 'player':
            # Coordonnées du centre du vaisseau joueur
            xp = self.player.rect[0] + (self.player.rect[2] / 2)
            yp = self.player.rect[1] - (self.player.rect[3] / 2)
            if self.player.shield >= 2:
                self.player.shield -= 2
            elif self.player.shield == 0:  # bouclier down
                self.player.life -= 1
                if self.player.life > 0:
                    self.menu.play_sound('loseLife')
                    Explosion(self, xp, yp, self.imgExplo['sonic'])
                    explo = False
                self.player.shield = 10  # bouclier up
            if self.player.power > 0:
                self.player.power -= 1
            if self.player.life > 0:
                if explo:
                    Explosion(self, xp, yp, self.imgExplo['medium'])
            # ------ GAME OVER ------ #
            else:
                self.menu.jukebox(music='ending.ogg')  # play end music
                self.player.shield = 0
                Explosion(self, xp, yp, self.imgExplo['sonic'], fps=120)
                self.menu.play_sound('explo2')
                self.player.kill()
                self.gameOver = True
        # - Hit sur un meteor - #
        elif sprite.stype == 'meteor':
            self.score += score
            # Coordonnées du milieu haut du météor
            xm = sprite.rect[0] + (sprite.rect[2] / 2)
            ym = sprite.rect[1]
            size = 'small'
            if sprite.size > 4:
                size = 'medium'
            Explosion(self, xm, ym, self.imgExplo[size])
        # - Hit sur un ennemi standard - #
        elif sprite.stype == 'pirate':
            sprite.life -= damage
            if sprite.life > 0:
                # Coordonnées de l'ennemi (= milieu haut de l'explosion)
                xe = sprite.rect[0] + sprite.rect[2] / 2
                ye = sprite.rect[1] - sprite.rect[3] / 5
                Explosion(self, xe, ye, self.imgExplo['medium'])
            else:
                # Coordonnées du centre de l'ennemi
                xe = sprite.rect[0] + (sprite.rect[2] / 2)
                ye = sprite.rect[1] - (sprite.rect[3] / 2)
                sprite.kill()
                Explosion(self, xe, ye, self.imgExplo['large'])
                self.score += score
                self.nbEnemy -= 1
        # - Hit sur un boss - #
        elif sprite.stype == 'boss':
            sprite.life -= damage
            if sprite.life < 1:
                sprite.kill()
                self.bossAlive = False
                self.score += (5000 * int(self.level))
                self.menu.play_sound('explo1')
                if self.level - int(self.level):
                    self.meteorField = True  # lauch meteor field if level = *.5
                else:
                    self.level += 0.5
            # Coordonnées milieu arrière du boss (=milieu haut de l'explo.)
            xb = sprite.rect[0] + (sprite.rect[2] / 2)
            yb = sprite.rect[1]
            Explosion(self, xb, yb, self.imgExplo['sonic'])

    def newgame(self):
        """Redémarre une nouvelle partie"""
        self.spawn, self.nbEnemy, self.score = 0, 0, 0
        self.maxEnemy, self.difficulty, self.level = 1, 1, 1.
        self.gameOver, self.bossAlive = False, False
        self.meteorTime, self.bonusTime = METEORTIME, BONUSTIME
        self.meteorField, self.nbMeteor = False, 0
        # Effacer tous les sprites
        for sprite in self.allSprites:
            sprite.kill()
        # Instancier un joueur et les objets score et level
        self.exit = False
        self.player = SpaceShip(self, WIDTH/2, HEIGHT-100)
        self.txtScore = Text(self, str(self.score), WIDTH / 1.8, 30)
        self.txtLevel = Text(self, str(self.level), WIDTH / 1.8, 10)
        pygame.mixer.music.fadeout(300)
        self.menu.jukebox(nextm=True)

    def cheat(self):
        """Méthode réservée au développement"""
        keys = pygame.key.get_pressed()
        if keys[pygame.K_l]:  # life +
            if self.player.life < 5:
                self.player.life += 1
        if keys[pygame.K_r]:  # life -
            if 1 < self.player.life < 6:
                self.player.life -= 1
        if keys[pygame.K_p]:
            if self.player.power < 5:
                self.player.power += 1  # power +
        if keys[pygame.K_s]:
            for sprite in self.enemies:
                if sprite.life > 1:
                    sprite.life = 1  # enemy life -1
        if keys[pygame.K_a]:
            for sprite in self.enemies:
                self.hit_sprite(sprite)  # Godlike
        if keys[pygame.K_m]:
            if self.meteorField and self.nbMeteor < 240:
                self.nbMeteor = 240  # end of meteor wave

    @staticmethod
    def quit():
        pygame.quit()
        sys.exit()


if __name__ == '__main__':
    Application().mainloop()
