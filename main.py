# Allow pygame_sdl2 to be imported as pygame.
import pygame_sdl2
pygame_sdl2.import_as_pygame()

import pygame as pg
import os
import random
import math
from settings import *
from os import path

def save_state(x, y):
    """
    Saves the game state.
    """

    with open("state.txt", "w") as f:
        f.write("{} {}".format(x, y))

def load_state():
    try:
        with open("state.txt", "r") as f:
            x, y = f.read().split()
            x = int(x)
            y = int(y)

        return x, y
    except:
        return None, None

def delete_state():

    if os.path.exists("state.txt"):
        os.unlink("state.txt")

class Player(pg.sprite.Sprite):
    def __init__(self, game):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.image = self.game.player_img_d
        self.rect = self.image.get_rect()
        self.rect.left = 10
        self.rect.top = 10
        self.speedx = 0
        self.speedy = 0
        self.direction = "down"
        self.go = False

    def update(self):
        self.speedx = 0
        self.speedy = 0
        if self.go:
            if self.direction == "up":
                self.image = self.game.player_img_u
                self.speedy = -PLAYER_SPEED
            elif self.direction == "down":
                self.image = self.game.player_img_d
                self.speedy = PLAYER_SPEED
            elif self.direction == "left":
                self.image = self.game.player_img_l
                self.speedx = -PLAYER_SPEED
            elif self.direction == "right":
                self.image = self.game.player_img_r
                self.speedx = PLAYER_SPEED
            self.orect = self.rect.center
            self.rect = self.image.get_rect()
            self.rect.center = self.orect

        if self.rect.centerx > WIDTH:
            self.rect.centerx = 0
        if self.rect.centerx < 0:
            self.rect.centerx = WIDTH
        if self.rect.centery > HEIGHT:
            self.rect.centery = 0
        if self.rect.centery < 0:
            self.rect.centery = HEIGHT


        self.rect.centerx += self.speedx
        self.rect.centery += self.speedy

class Gold(pg.sprite.Sprite):
    def __init__(self, game):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.image = self.game.gold_img
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH / 2, HEIGHT / 2)

class Portal(pg.sprite.Sprite):
    def __init__(self, game, tele=False):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.tele = tele
        if self.tele == True:
            self.rot_speed = PORTAL_ROT_SPEED
            self.image_orig = self.game.portal_img_i
        else:
            self.rot_speed = -PORTAL_ROT_SPEED
            self.image_orig = self.game.portal_img_o
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.rect.centerx = random.randrange(0, WIDTH)
        self.rect.centery = random.randrange(0, HEIGHT)
        self.rot = 0
        self.last_update = pg.time.get_ticks()

    def update(self):
        now = pg.time.get_ticks()
        if now - self.last_update > 50:
            self.last_update = now
            self.rot = (self.rot + self.rot_speed) % 360
            new_image = pg.transform.rotate(self.image_orig, self.rot)
            old_center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect()
            self.rect.center = old_center

class Mob(pg.sprite.Sprite):
    def __init__(self, meteor_images):
        pg.sprite.Sprite.__init__(self)
        self.meteor_images = meteor_images
        self.image = random.choice(self.meteor_images)
        self.rect = self.image.get_rect()
        if self.image == self.meteor_images[6] or self.image == self.meteor_images[7] or self.image == self.meteor_images[8] or self.image == self.meteor_images[9]:
            scale = random.randrange(15, 30) / 100.0
        elif self.image == self.meteor_images[0] or self.image == self.meteor_images[1]:
            scale = random.randrange(35, 50) / 100.0
        elif self.image == self.meteor_images[2] or self.image == self.meteor_images[3] or self.image == self.meteor_images[4] or self.image == self.meteor_images[5]:
            scale = random.randrange(55, 70) / 100.0
        self.image = self.image.convert_alpha()
        self.image = pg.transform.scale(self.image, (int(self.rect.width * scale),
                                                     int(self.rect.height * scale)))
        self.rect = self.image.get_rect()
        self.center_x = WIDTH / 2
        self.center_y = HEIGHT / 2
        self.angle = random.random() * 2 * math.pi
        self.radius = random.randrange(60, WIDTH / 2)
        self.speed = 0.008

    def update(self):
        self.rect.centerx = self.radius * math.sin(self.angle) + self.center_x
        self.rect.centery = self.radius * math.cos(self.angle) + self.center_y
        self.angle += self.speed

class Star(pg.sprite.Sprite):
    def __init__(self, game):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.image = pg.Surface((1, 1))
        self.image.fill(STAR_COLOR)
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH / 2
        self.rect.centery = HEIGHT / 2
        self.dir = random.randrange(360)
        self.speed = random.random()*.6 + .4
        self.speedx = math.sin(self.dir) * self.speed
        self.speedy = math.cos(self.dir) * self.speed
        self.steps = random.randint(0, 320) * .9

    def update(self):
        self.rect.centerx += self.speedx *self.steps
        self.rect.centery += self.speedy * self.steps
        if not 0 <= self.rect.centerx <= WIDTH or not 0 <= self.rect.centery <= HEIGHT:
            self.kill()
        else:
            self.speedx = self.speedx * 1.05
            self.speedy = self.speedy * 1.05

class Laser(pg.sprite.Sprite):
    def __init__(self, player, game, x, y):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.player = player
        if self.player.image == self.game.player_img_l:
            self.image = self.game.laser_img_l
            self.speedx = -20
            self.speedy = 0
        elif self.player.image == self.game.player_img_r:
            self.image = self.game.laser_img_r
            self.speedx = 20
            self.speedy = 0
        elif self.player.image == self.game.player_img_u:
            self.image = self.game.laser_img_u
            self.speedy = -20
            self.speedx = 0
        elif self.player.image == self.game.player_img_d:
            self.image = self.game.laser_img_d
            self.speedy = 20
            self.speedx = 0

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self):
        self.rect.centery += self.speedy
        self.rect.centerx += self.speedx

        if self.rect.bottom < 0:
             self.kill()
        if self.rect.top > HEIGHT:
            self.kill()
        if self.rect.left < 0:
            self.kill()
        if self.rect.right > WIDTH:
            self.kill()

class Powerup(pg.sprite.Sprite):
    def __init__(self, game, power):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.power = power
        if self.power == "laser":
            self.image = self.game.laser_img_u
        else:
            self.image = None
        self.rect = self.image.get_rect()
        self.rect.centerx = random.randrange(0, WIDTH)
        self.rect.centery = random.randrange(0, HEIGHT)

class Explosion(pg.sprite.Sprite):
    def __init__(self, game, center, size):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.size = size
        self.image = self.game.explosion_anim[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pg.time.get_ticks()
        self.frame_rate = 75

    def update(self):
        if self.size == 'fireworks':
            self.rect.center = self.game.player.rect.center
        if self.game.now - self.last_update > self.frame_rate:
            self.last_update = self.game.now
            self.frame += 1
            if self.frame == len(self.game.explosion_anim[self.size]):
                self.kill()
                if self.size == 'player' or self.size == 'fireworks':
                    self.game.done = True
            else:
                center = self.rect.center
                self.image = self.game.explosion_anim[self.size][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center

class Medals(pg.sprite.Sprite):
    def __init__(self, game):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        if self.game.highscore >= 60:
            self.medal_count = 7
        elif self.game.highscore >= 50:
            self.medal_count = 6
        elif self.game.highscore >= 40:
            self.medal_count = 5
        elif self.game.highscore >= 30:
            self.medal_count = 4
        elif self.game.highscore >= 20:
            self.medal_count = 3
        elif self.game.highscore >= 10:
            self.medal_count = 2
        elif self.game.highscore >= 5:
            self.medal_count = 1
        else:
            self.medal_count = 0
        self.once = False
        self.draw_medals()


    def draw_medals(self):
        for i in range(self.medal_count):
            self.image = self.game.medal_imgs[i]
            self.rect = self.image.get_rect()
            self.spot = ((-1) ** i)
            if self.spot == -1:
                self.rect.center = (WIDTH / 2 + 30 * ((-1) ** i) - i * 30, HEIGHT / 2 + 25)
            else:
                self.rect.center = (WIDTH / 2 + 30 * i * self.spot, HEIGHT / 2 + 25)

            self.game.screen.blit(self.image, self.rect)

pg.mixer.init(buffer=256)
pg.init()
screen = pg.display.set_mode((1280, 720))
WIDTH, HEIGHT = screen.get_size()

class Main:
    def __init__(self, screen):
        self.clock = pg.time.Clock()
        self.score = 0
        self.bullets = 5
        self.meteor_images = []
        for i in range(1, 11):
            self.meteor_images.append(pg.image.load( 'img/meteor{}.png'.format(i)).convert_alpha())
        self.background = pg.image.load('img/starfield.png').convert_alpha()
        self.background = pg.transform.scale(self.background, (WIDTH, HEIGHT))
        self.background_rect = self.background.get_rect()
        self.laser_img = pg.image.load("img/laser.png").convert_alpha()
        self.laser_img_d = pg.transform.scale(self.laser_img, (4, 18))
        self.laser_img_u = pg.transform.flip(self.laser_img_d, False, True)
        self.laser_img_r = pg.transform.rotate(self.laser_img_d, 90)
        self.laser_img_l = pg.transform.flip(self.laser_img_r, True, False)
        self.gun = True
        self.cooldown = -1000
        self.sleeping = False
        self.screen = screen
        self.done = False
        self.five = True
        self.ten = True
        self.twenty = True
        self.thirty = True
        self.fourty = True
        self.fifty = True
        self.sixty = True
        self.load_data()

    def load_data(self):
        # load high score
        self.dir = path.dirname(__file__)
        try:
            with open(path.join(self.dir, HS_FILE), 'r+' ) as f:
                self.highscore = int(f.read())
        except:
            with open(path.join(self.dir, HS_FILE), 'w'):
                self.highscore = 0
        # load player images
        self.player_img_d = pg.image.load(PLAYER_IMG).convert_alpha()
        self.player_img_d = pg.transform.scale(self.player_img_d, (26, 21))
        self.player_img_u = pg.transform.flip(self.player_img_d, False, True)
        self.player_img_r = pg.transform.rotate(self.player_img_d, 90)
        self.player_img_l = pg.transform.flip(self.player_img_r, True, False)
        # load gold image
        self.gold_img = pg.image.load(GOLD_IMG).convert_alpha()
        self.gold_img = pg.transform.scale(self.gold_img, (15, 15))
        # load portal images
        self.portal_img_i = pg.image.load(PORTAL_IMG).convert_alpha()
        self.portal_img_i = pg.transform.scale(self.portal_img_i, (30, 30))
        self.portal_img_o = pg.image.load(PORTAL_IMG2).convert_alpha()
        self.portal_img_o = pg.transform.scale(self.portal_img_o, (30, 30))
        # load explosions
        self.explosion_anim = {}
        self.explosion_anim['lg'] = []
        self.explosion_anim['sm'] = []
        self.explosion_anim['player'] = []
        for i in range(9):
            self.img = pg.image.load('img/regularExplosion0{}.png'.format(i)).convert_alpha()
            self.img_lg = pg.transform.scale(self.img, (75, 75))
            self.explosion_anim['lg'].append(self.img_lg)
            self.img_sm = pg.transform.scale(self.img, (32, 32))
            self.explosion_anim['sm'].append(self.img_sm)
            self.img = pg.image.load('img/sonicExplosion0{}.png'.format(i)).convert_alpha()
            self.img = pg.transform.scale(self.img, (75, 75))
            self.explosion_anim['player'].append(self.img)
        # load fireworks
        self.explosion_anim['fireworks'] = []
        for i in range(10):
            self.img = pg.image.load('img/5000{}.png'.format(i)).convert_alpha()
            self.img = pg.transform.scale(self.img, (100, 100))
            self.explosion_anim['fireworks'].append(self.img)
        self.img = pg.image.load('img/50010.png').convert_alpha()
        self.img = pg.transform.scale(self.img, (100, 100))
        self.explosion_anim['fireworks'].append(self.img)
        self.img = pg.image.load('img/50011.png').convert_alpha()
        self.img = pg.transform.scale(self.img, (100, 100))
        self.explosion_anim['fireworks'].append(self.img)
        # load arrow keys
        self.arrow_keys = pg.image.load('img/arrow_keys.png').convert_alpha()
        self.arrow_keys = pg.transform.scale(self.arrow_keys, (320, 320))
        # load shoot key
        self.shoot_key = pg.image.load('img/aim-clipart-Aim.png').convert_alpha()
        self.shoot_key = pg.transform.scale(self.shoot_key, (120, 120))
        # load and play music
        self.music = random.randrange(2)
        if self.music == 0:
            pg.mixer.music.load('snd/spacewalk.ogg')
        if self.music == 1:
            pg.mixer.music.load('snd/throughspace.ogg')
        pg.mixer.music.play(loops=-1)
        # load other sound
        self.shoot_sound = pg.mixer.Sound('snd/Laser_Shoot.wav')
        self.player_die_sound = pg.mixer.Sound('snd/rumble1.ogg')
        self.gold_sound = pg.mixer.Sound('snd/gold.wav')
        self.reload_gun_sound = pg.mixer.Sound('snd/teleport.ogg')
        self.teleport_sound = pg.mixer.Sound('snd/portal.wav')
        self.expl_sounds = []
        for snd in ['snd/Explosion.wav', 'snd/Explosion2.wav']:
            self.expl_sounds.append(pg.mixer.Sound(snd))
        # load medals
        self.medal_imgs = []
        for i in range(7):
            self.img = pg.image.load('img/shaded_medal{}.png'.format(i)).convert_alpha()
            self.medal_imgs.append(self.img)
        # load text img
        self.arrow_img = pg.image.load('img/arrow.png').convert_alpha()
        self.arrow_img = pg.transform.scale(self.arrow_img, (100, 31))

    def draw_text(self, text, size, color, x, y, align="topleft"):
        font = pg.font.Font("DejaVuSans.ttf", size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.center = (x, y)
        self.screen.blit(text_surface, text_rect)

    def new(self):
        self.all_sprites = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.portals = pg.sprite.Group()
        self.stars = pg.sprite.Group()
        self.lasers = pg.sprite.Group()
        self.ulasers = pg.sprite.Group()
        self.up_rect = pg.Rect(250, HEIGHT - 380, 100, 120)
        self.down_rect = pg.Rect(250, HEIGHT - 180, 100, 120)
        self.left_rect = pg.Rect(140, HEIGHT - 270, 120, 100)
        self.right_rect = pg.Rect(340, HEIGHT - 270, 120, 100)
        self.shoot_rect = pg.Rect(WIDTH - 340, HEIGHT - 290, 140, 140)
        self.gold = Gold(self)
        self.portal = Portal(self, tele=True)
        self.portal2 = Portal(self)
        self.lpower = Powerup(self, "laser")
        self.all_sprites.add(self.portal2)
        self.all_sprites.add(self.portal)
        self.all_sprites.add(self.lpower)
        self.ulasers.add(self.lpower)
        self.portals.add(self.portal)
        self.portals.add(self.portal2)
        if self.score <= 0:
            self.score = 0
        self.mob_count = self.score * 5 + 45
        for i in range(self.mob_count):
            self.mob = Mob(self.meteor_images)
            self.all_sprites.add(self.mob)
            self.mobs.add(self.mob)
        self.player = Player(self)
        self.all_sprites.add(self.player)
        self.all_sprites.add(self.gold)
        for i in range(NUM_STARS):
            self.star = Star(self)
            self.stars.add(self.star)
            self.all_sprites.add(self.star)
        self.point = False
        self.draw_debug = False
        # On startup, load state saved by APP_WILLENTERBACKGROUND, and the delete
        # that state.
        self.x, self.y = load_state()
        delete_state()
        self.run()

    def run(self):
        self.running = True
        while self.running:
            self.clock.tick(FPS)
            self.events()
            if not self.sleeping:
                self.update()
                self.draw()
                pg.display.flip()

    def update(self):
        self.all_sprites.update()
        self.now = pg.time.get_ticks()
         # mobs hit player
        hits = pg.sprite.spritecollide(self.player, self.portals, False)
        if not hits:
            hits = pg.sprite.spritecollide(self.player, self.mobs, True)
            if hits and self.point == False:
                self.player_die_sound.play()
                self.death_explosion = Explosion(self, self.player.rect.center, 'player')
                self.all_sprites.add(self.death_explosion)
                self.player.kill()
                self.player.rect.center = (-100, -100)
                self.score -= 1

        if self.done == True:
            self.done = False
            self.new()

        if self.point == False:
            # player hits gold
            hits = pg.sprite.collide_rect(self.player, self.gold)
            if hits:
                self.gold_sound.play()
                self.point = True
                self.gold.rect.center = (-100, -100)
                self.gold.kill()
                self.victory_explosion = Explosion(self, self.player.rect.center, 'fireworks')
                self.all_sprites.add(self.victory_explosion)
                self.score += 1

        hits = pg.sprite.collide_rect(self.player, self.portal)
        if hits:
            self.teleport_sound.play()
            self.player.rect.center = self.portal2.rect.center

        hits = pg.sprite.groupcollide(self.lasers, self.mobs, True, True)
        for hit in hits:
            random.choice(self.expl_sounds).play()
            self.expl = Explosion(self, hit.rect.center, 'lg')
            self.all_sprites.add(self.expl)

        if self.bullets <= 0:
            self.bullets = 0
        if self.score <= 0:
            self.score = 0

        if self.score > self.highscore:
            self.highscore = self.score
            with open(path.join(self.dir, HS_FILE), 'w') as f:
                f.write(str(self.score))

        hits = pg.sprite.spritecollide(self.player, self.ulasers, False)
        for hit in hits:
            self.reload_gun_sound.play()
            self.lpower.kill()
            self.bullets += 1

    def events(self):
        for event in pg .event.get():
            # pg quit.
            if event.type == pg.QUIT:
                self.running = False
                pg.quit()

            # Android back key.
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_AC_BACK:
                    self.running = False
                    pg.quit()
                if event.key == pg.K_h:
                    self.draw_debug = not self.draw_debug

            self.cur = pg.mouse.get_pos()
            self.click = pg.mouse.get_pressed()
            if self.up_rect.collidepoint(self.cur):
                if self.click[0]:
                    self.player.go = True
                    self.player.direction = "up"
            elif self.down_rect.collidepoint(self.cur):
                if self.click[0]:
                    self.player.go = True
                    self.player.direction = "down"
            elif self.left_rect.collidepoint(self.cur):
                if self.click[0]:
                    self.player.go = True
                    self.player.direction = "left"
            elif self.right_rect.collidepoint(self.cur):
                if self.click[0]:
                    self.player.go = True
                    self.player.direction = "right"
            elif self.shoot_rect.collidepoint(self.cur):
                self.player.go = False
                if self.click[0] and self.bullets > 0 and self.gun == True and self.now - self.cooldown > 1000:
                    self.shoot_sound.play()
                    self.bullets -=1
                    self.cooldown = self.now
                    self.laser = Laser(self.player, self, self.player.rect.centerx, self.player.rect.centery)
                    self.all_sprites.add(self.laser)
                    self.lasers.add(self.laser)

            if event.type == pg.MOUSEBUTTONUP:
                self.player.go = False

            if event.type == pg.APP_WILLENTERBACKGROUND:
                # The app is about to go to sleep. It should save state, cancel
                # any timers, and stop drawing the screen until an APP_DIDENTERFOREGROUND
                # event shows up.

                save_state(self.x, self.y)

                self.sleeping = True

            if event.type == pg.APP_DIDENTERFOREGROUND:
                # The app woke back up. Delete the saved state (we don't need it),
                # restore any times, and start drawing the screen again.

                delete_state()
                self.sleeping = False

                # For now, we have to re-open the window when entering the
                # foreground.
                self.screen = pg.display.set_mode((1280, 720))

    def draw(self):
        self.award_screen()
        self.screen.fill(BLACK)
        self.screen.blit(self.arrow_keys, (140, HEIGHT - 380))
        if self.bullets > 0:
            self.gun = True
            self.draw_shoot_key()
        else:
            self.gun = False
        pg.display.set_caption("{:.2f}".format(self.clock.get_fps()))
        self.all_sprites.draw(self.screen)
        self.draw_text(str(self.score), 36, WHITE, WIDTH / 2, 18)
        for i in range(NUM_STARS - len(self.stars)):
            self.star = Star(self)
            self.stars.add(self.star)
            self.all_sprites.add(self.star)
        for sprite in self.all_sprites:
            if self.draw_debug:
                pg.draw.rect(self.screen, CYAN, (sprite.rect), 1)

    def award_screen(self):
        if self.score == 5 and self.highscore == 5 and self.five == True:
            self.five = False
            self.screen.fill(BLACK)
            self.draw_text('Bronze Medal Achieved!', 48, CYAN, WIDTH / 2, HEIGHT / 4)
            self.screen.blit(self.medal_imgs[0], (WIDTH / 2 - 20, HEIGHT / 2))
            pg.display.flip()
            pg.time.wait(3000)
        if self.score == 10 and self.highscore == 10 and self.ten == True:
            self.ten = False
            self.screen.fill(BLACK)
            self.draw_text('Silver Medal Achieved!', 48, CYAN, WIDTH / 2, HEIGHT / 4)
            self.screen.blit(self.medal_imgs[1], (WIDTH / 2 - 20, HEIGHT / 2))
            pg.display.flip()
            pg.time.wait(3000)
        if self.score == 20 and self.highscore == 20 and self.twenty == True:
            self.twenty = False
            self.screen.fill(BLACK)
            self.draw_text('Silver Star Achieved!', 48, CYAN, WIDTH / 2, HEIGHT / 4)
            self.screen.blit(self.medal_imgs[2], (WIDTH / 2 - 20, HEIGHT / 2))
            pg.display.flip()
            pg.time.wait(3000)
        if self.score == 30 and self.highscore == 30 and self.thirty == True:
            self.thirty = False
            self.screen.fill(BLACK)
            self.draw_text('Silver Medal of Honor Achieved!', 48, CYAN, WIDTH / 2, HEIGHT / 4)
            self.screen.blit(self.medal_imgs[3], (WIDTH / 2 - 20, HEIGHT / 2))
            pg.display.flip()
            pg.time.wait(3000)
        if self.score == 40 and self.highscore == 40 and self.fourty == True:
            self.fourty = False
            self.screen.fill(BLACK)
            self.draw_text('Gold Medal Achieved!', 48, CYAN, WIDTH / 2, HEIGHT / 4)
            self.screen.blit(self.medal_imgs[4], (WIDTH / 2 - 20, HEIGHT / 2))
            pg.display.flip()
            pg.time.wait(3000)
        if self.score == 50 and self.highscore == 50 and self.fifty == True:
            self.fifty = False
            self.screen.fill(BLACK)
            self.draw_text('Gold Star Achieved!', 48, CYAN, WIDTH / 2, HEIGHT / 4)
            self.screen.blit(self.medal_imgs[5], (WIDTH / 2 - 20, HEIGHT / 2))
            pg.display.flip()
            pg.time.wait(3000)

        if self.score == 60 and self.highscore == 60 and self.sixty == True:
            self.sixty = False
            self.screen.fill(BLACK)
            self.draw_text('Gold Medal of Honor Achieved!', 48, CYAN, WIDTH / 2, HEIGHT / 4)
            self.screen.blit(self.medal_imgs[6], (WIDTH / 2 - 20, HEIGHT / 2))
            pg.display.flip()
            pg.time.wait(3000)
            self.screen.fill(BLACK)
            self.draw_text('Created by Peter Scholtens', 36, CYAN, WIDTH / 2, HEIGHT / 2)
            self.draw_text('Icon made by Nema Shokraee', 24, CYAN, WIDTH / 2, HEIGHT / 2 + 36)
            self.draw_text('Target explosion by Ashish Yadav', 24, CYAN, WIDTH / 2, HEIGHT / 2 + 60)
            pg.display.flip()
            pg.time.wait(3000)


    def draw_shoot_key(self):
##        pg.draw.rect(self.screen, BLUE, self.shoot_rect)
        self.screen.blit(self.shoot_key, (WIDTH - 330, HEIGHT - 280))
        self.draw_text(str(self.bullets), 18, WHITE, WIDTH - 270, HEIGHT - 220)

    def show_start_screen(self):
        # game splash/start screen
        self.screen.fill(BLACK)
        self.screen.blit(self.background, self.background_rect)
        if self.highscore < 5:
            self.draw_text('Created by Peter Scholtens', 36, CYAN, WIDTH / 2, HEIGHT / 2)
            self.draw_text('Icon made by Nema Shokraee', 24, CYAN, WIDTH / 2, HEIGHT / 2 + 36)
        self.medals = Medals(self)
        if self.medals.medal_count > 0:
            self.draw_text('Medals', 24, CYAN, WIDTH / 2, HEIGHT / 2 - 30)
        self.draw_text(TITLE, 96, YELLOW, WIDTH / 2, HEIGHT / 4)
        self.draw_text("High score: %s" % self.highscore, 24, WHITE, WIDTH / 2, HEIGHT * 3 / 4)
        pg.display.flip()
        self.wait_for_press()

    def show_intro_screen(self):
        # intro screen
        self.write = ['Welcome to %s!' % TITLE,
                      'Your ship starts in the top left corner.',
                      'This is a portal.',
                      'Go through the blue one and come out the purple one,',
                      'In each course there is one bullet, pick it up by going over it.',
                      'Your controls are the arrow keys on the bottom left.',
                      'The shoot button is on the bottom right.',
                      'Dodge the asteriods and reach the gold in the middle.',
                      'Good Luck!']
        for i in range(len(self.write)):
            self.screen.fill(BLACK)
            self.draw_text(self.write[i], 36, CYAN, WIDTH / 2, HEIGHT / 2)
            if i == 1:
                self.screen.blit(self.player_img_d, (WIDTH / 2 - 13, HEIGHT / 2 + 30))
            if i == 2:
                self.screen.blit(self.portal_img_i, (WIDTH / 2 - 15, HEIGHT / 2 + 30))
            if i == 3:
                self.draw_text('you can\'t go back and forth.', 36, CYAN, WIDTH / 2, HEIGHT / 2 + 30)
                self.screen.blit(self.portal_img_i, (WIDTH / 2 - 90, HEIGHT / 2 + 60))
                self.screen.blit(self.arrow_img, (WIDTH / 2 - 50, HEIGHT / 2 + 60))
                self.screen.blit(self.portal_img_o, (WIDTH / 2 + 60, HEIGHT / 2 + 60))
            if i == 4:
                self.screen.blit(self.laser_img_d, (WIDTH / 2, HEIGHT / 2 + 30))
            pg.display.flip()
            pg.time.wait(3000)
            if i == 3 or i == 4:
                pg.time.wait(1300)
        self.new()

    def wait_for_press(self):
        self.waiting = True
        while self.waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                # Android back key.
                if event.type == pg.QUIT:
                    self.running = False
                    pg.quit()
                if event.type == pg.KEYDOWN and event.key == pg.K_AC_BACK:
                    self.running = False
                    pg.quit()
                if event.type == pg.APP_WILLENTERBACKGROUND:
                    # The app is about to go to sleep. It should save state, cancel
                    # any timers, and stop drawing the screen until an APP_DIDENTERFOREGROUND
                    # event shows up.

                    save_state(self.x, self.y)

                    self.sleeping = True

                if event.type == pg.APP_DIDENTERFOREGROUND:
                    # The app woke back up. Delete the saved state (we don't need it),
                    # restore any times, and start drawing the screen again.

                    delete_state()
                    self.sleeping = False

                    # For now, we have to re-open the window when entering the
                    # foreground.
                    self.screen = pg.display.set_mode((1280, 720))
                if event.type == pg.MOUSEBUTTONUP:
                    if self.highscore == 0:
                        self.show_intro_screen()
                    else:
                        self.new()

if __name__ == "__main__":
    m = Main(screen)
    m.show_start_screen()
