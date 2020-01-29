# -*- coding: Utf-8 -*-

from pygame.locals import *
from sources.resources import *


class Menu(object):
    """Gérer l'affichage des menus et la musique
    Méthodes : start_menu, pause, jukebox, dashboard, draw button, draw_text"""

    def __init__(self, appli):
        screen = pygame.display.get_surface()
        self.screen = screen
        self.appli = appli  # réf. de l'application principale
        self.area = screen.get_rect()
        self.width, self.height = screen.get_size()
        self.imgLife, self.rectLife = load_image('playerLife1_green.png')
        self.music = ['menu.ogg', 'track1.ogg', 'track2.ogg', 'track3.ogg',
                      'ending.ogg']
        self.playMusic = True
        self.dictSounds = load_game_sounds()  # dict. des sons
        self.playSound = True
        self.im = 0  # indice de liste de musique en cours
        self.end = False  # end of game flag
        self.background = load_image('background_menu.png')[0]
        self.clock = pygame.time.Clock()

    def start_menu(self):
        """Menu de démarrage"""
        self.jukebox()
        self.im = 0
        self.end = False
        ch = 0  # actual choice
        wb, hb = 190, 50  # button dimensions
        dif = hb * 1.8    # space beetween buttons
        while 1:
            self.clock.tick(30)
            state = [[WHITE, 1], [WHITE, 1], [WHITE, 1]]  # couleurs et bordure
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.appli.quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == K_DOWN and ch < 2:
                        ch += 1
                    if event.key == K_UP and ch > 0:
                        ch -= 1
                    if event.key == K_RETURN:
                        if ch == 0:
                            return
                        elif ch == 1:
                            self.option_menu()
                        elif ch == 2:
                            self.appli.quit()
            state[ch][0], state[ch][1] = RED, 0  # change selected button
            self.screen.blit(self.background, (0, 0))
            # Draw highscore and game name
            highscore = 'High Score: {}'.format(self.appli.highscore)
            self.draw_text(highscore, HW, DASHSIZE, 28)
            # self.draw_text('Endless', HW - 45, DASHSIZE + 90, 40, BLUE)
            # self.draw_text('Space', HW + 65, DASHSIZE + 90, 40, BLUE)
            # Draw buttons : top, middle, bottom
            self.draw_button(HW - wb // 2, HH - dif - hb // 2, wb, hb, state, 0)
            self.draw_text('New Game', HW, HH - dif, 30)
            self.draw_button(HW - wb // 2, HH - hb // 2, wb, hb, state, 1)
            self.draw_text('Options', HW, HH, 30)
            self.draw_button(HW - wb // 2, HH + dif - hb // 2, wb, hb, state, 2)
            self.draw_text('Exit', HW, HH + dif, 30)
            pygame.display.flip()

    def option_menu(self):
        """Menu d'option : activer/désactiver son et music, reset high score"""
        wb, hb = 220, 40  # button dimensions
        dif, ch = hb * 1.8, 0  # space beetween buttons and choice
        while 1:
            state = [[WHITE, 1], [WHITE, 1], [WHITE, 1], [WHITE, 1]]
            self.clock.tick(30)
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.appli.quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == K_DOWN and ch < 3:
                        ch += 1
                    if event.key == K_UP and ch > 0:
                        ch -= 1
                    if event.key == K_RETURN:
                        if ch == 0:
                            self.playMusic = not self.playMusic
                            self.jukebox()
                        if ch == 1:
                            self.playSound = not self.playSound
                        if ch == 2:
                            self.appli.highscore = read_write_highscore('write')
                        if ch == 3:
                            return
            state[ch][0], state[ch][1] = RED, 0  # change selected button
            self.screen.blit(self.background, (0, 0))
            highscore = 'High Score: {}'.format(self.appli.highscore)
            self.draw_text(highscore, HW, DASHSIZE, 28)
            # Draw buttons
            if self.playMusic:
                txtbutton1 = 'Disable music'
            else:
                txtbutton1 = 'Enable music'
            if self.playSound:
                txtbutton2 = 'Disable sound'
            else:
                txtbutton2 = 'Enable sound'
            xb = HW - wb // 2
            yb1 = HH - dif // 2 - dif
            yb2 = HH - dif // 2
            yb3 = HH + dif // 2
            yb4 = HH + dif // 2 + dif
            self.draw_button(xb, yb1, wb, hb, state, 0)
            self.draw_text(txtbutton1, HW, yb1 + hb // 2, 30)
            self.draw_button(xb, yb2, wb, hb, state, 1)
            self.draw_text(txtbutton2, HW, yb2 + hb // 2, 30)
            self.draw_button(xb, yb3, wb, hb, state, 2)
            self.draw_text('Reset High Score', HW, yb3 + hb // 2, 30)
            self.draw_button(xb, yb4, wb, hb, state, 3)
            self.draw_text('Back to main Menu', HW, yb4 + hb // 2, 30)
            pygame.display.flip()

    def pause(self):
        """Affiche le menu pause"""
        self.draw_text('PAUSE', HW, HEIGHT//1.6, 40)
        if not self.appli.gameOver:
            self.draw_text('Press [Echap] to exit', HW, HEIGHT // 1.4, 28)
        pygame.display.flip()
        while 1:
            event = pygame.event.wait()
            if event.type == KEYDOWN:
                if event.key == K_RETURN:
                    break
                if event.key == K_ESCAPE:
                    self.appli.exit = True
                    break
            elif event.type == QUIT:
                self.appli.quit()

    def play_sound(self, sound):
        if self.playSound:
            self.dictSounds[sound].play()

    def jukebox(self, nextm=False, music='menu.ogg', option=-1):
        """Gére la lecture des musiques"""
        if nextm:
            if self.im < len(self.music) - 2:
                self.im += 1  # next track
            else:
                self.im = 1  # retour track 1
            music = self.music[self.im]
        if self.playMusic:
            try:
                pygame.mixer.music.set_volume(0.5)
                pygame.mixer.music.load('sources/sound/music/{}'.format(music))
                pygame.mixer.music.play(option)
            except pygame.error as message:
                print("Impossible de charger la musique : ", message)
        else:
            pygame.mixer.music.stop()

    def dashboard(self, appli, player):
        """Affiche des informations sur la partie :
        vie, bouclier, score, highscore, (experience/level)"""
        # Afficher le Bouclier
        sizebar = 1
        if player.shield > 0:
            sizebar = (self.width / 5) * (player.shield / 10)
        pygame.draw.rect(self.screen, YELLOW, (10, 10, sizebar, 17))
        pygame.draw.rect(self.screen, WHITE, (10, 10, self.width / 5, 17), 2)
        # Afficher la puissance
        i = player.power
        if player.power > 0:
            while i > 0:
                img, rect = appli.imgBonus['power']
                x = self.width / 5 + rect[2] * i * 1.5
                y = rect[3] / 6
                self.screen.blit(img, (x, y))
                i -= 1
        else:
            img, rect = appli.imgBonus['powerdown']
            x = self.width / 5 + rect[2] * 1.5
            y = rect[3] / 5
            self.screen.blit(img, (x, y))
        # Afficher les vies
        i = player.life
        while i > 0:
            x = self.width - self.rectLife[2] * i * 1.15
            self.screen.blit(self.imgLife, (x, 4))
            i -= 1
        # Update level and score
        appli.txtLevel.texte = 'Level %s' % int(appli.level)
        appli.txtScore.texte = '%s' % appli.score
        # Afficher le Game Over et enregistrer le highscore si nécessaire
        if appli.gameOver and not self.end:
            if appli.score > appli.highscore:
                appli.highscore = read_write_highscore('write', appli.score)
                Text(appli, 'New High Score', WIDTH/2, HEIGHT / 4.5, 25, WHITE)
            Text(appli, 'Game Over', WIDTH / 2, HEIGHT / 3.3, 50, RED)
            Text(appli, str(appli.score), WIDTH / 2, HEIGHT / 2.4, 45, ORANGE)
            Text(appli, 'Press [C] to continue', WIDTH / 2, HEIGHT / 1.9, 40)
            self.end = True

    def draw_button(self, x, y, w, h, state, i):
        pygame.draw.rect(self.screen, state[i][0], (x, y, w, h), state[i][1])

    def draw_text(self, texte, x, y, size=25, coul=WHITE):
        font = pygame.font.Font(None, size)
        image = font.render(texte, 1, coul)
        rect = image.get_rect(centerx=x, centery=y)
        self.screen.blit(image, rect)


class Text(pygame.sprite.Sprite):
    """Permet de dessiner un texte sur l'écran avec possibilité de l'animer
    Return     : object text
    Méthodes   : update
    Attributes : texte, size, color, speed, font, movepos """

    def __init__(self, appli, texte, x, y, size=25, coul=WHITE, speed=0):
        self._layer = TEXT_LAYER
        group = appli.allSprites, appli.text
        pygame.sprite.Sprite.__init__(self, group)
        screen = pygame.display.get_surface()
        self.appli = appli
        self.area = screen.get_rect()
        self.texte = texte
        self.size = size
        self.x, self.y = x, y
        self.color = coul
        self.speed = speed
        self.movepos = [speed, 0]
        self.font = pygame.font.Font(None, size)
        self.image = self.font.render(texte, 1, coul)
        self.rect = self.image.get_rect(centerx=self.x, centery=self.y)

    def update(self):
        self.image = self.font.render(str(self.texte), 1, self.color)
        self.rect = self.image.get_rect(centerx=self.x, centery=self.y)
        newpos = self.rect.move(self.movepos)
        if not self.area.contains(newpos):
            self.speed = -self.speed
            self.movepos = [self.speed, 0]
            newpos = self.rect.move(self.movepos)
        self.rect = newpos
