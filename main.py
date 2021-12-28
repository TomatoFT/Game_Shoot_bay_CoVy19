import pygame as pg
import random
import sys
import os
# from pygame import event
# from pygame.time import Clock
pg.font.init()
pg.mixer.init()
# Picture
WIDTH, HEIGHT = 900, 500
screen = pg.display.set_mode((WIDTH, HEIGHT))
Background = pg.image.load(os.path.join('assests',"5.png"))
Background = pg.transform.scale(Background, (900, 500))
PlayerImg = pg.image.load(os.path.join("assests","1.png"))
PlayerImg = pg.transform.rotate(pg.transform.scale(PlayerImg, (80, 45)), 270)
EnemyImg = pg.image.load(os.path.join("assests","3.png"))
EnemyImg = pg.transform.rotate(pg.transform.scale(EnemyImg, (50, 50)), 90)
EnemyImg2 = pg.image.load(os.path.join("assests","2.png"))
EnemyImg2 = pg.transform.rotate(pg.transform.scale(EnemyImg2, (50, 50)), 90)
EnemyImg6 = pg.image.load(os.path.join("assests","6.png"))
EnemyImg6 = pg.transform.rotate(pg.transform.scale(EnemyImg6, (50, 50)), 90)
BulletImg = pg.image.load(os.path.join("assests","4.png"))
BulletImg = pg.transform.rotate(pg.transform.scale(BulletImg, (40, 65)), 360)
Menu_screen = pg.image.load(os.path.join("assests","7.png"))
Menu_screen = pg.transform.scale(Menu_screen, (900, 500))
Lost_screen = pg.image.load(os.path.join("assests","8.png"))
Lost_screen = pg.transform.scale(Lost_screen, (900, 500))
WINNER_screen = pg.image.load(os.path.join("assests","9.png"))
WINNER_screen = pg.transform.scale(WINNER_screen, (900, 500))
pg.display.set_caption("Game của bạn TomFT")

# music_in_game.set_volume = 0.6
# class


class bullet:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pg.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.x -= vel

    def off_screen(self):
        return not(self.x >= 0 and self.x <= WIDTH)

    def collision(self, obj):
        return collide(self, obj)


class character:
    COOLDOWN = 10

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.Char_Img = None
        self.Bullet_Img = None
        self.Bullets = []
        self.cool_down_counter = 0

    def draw(self, window):
        screen.blit(self.Char_Img, (self.x, self.y))
        for Bullet in self.Bullets:
            Bullet.draw(screen)

    def move_bullet(self, vel, obj):
        self.cooldown()
        for Bullet in self.Bullets:
            Bullet.move(vel)
            if Bullet.off_screen(WIDTH):
                self.Bullets.remove(Bullet)
            elif Bullet.collision(obj):
                obj.Health -= 40
                self.Bullets.remove(Bullet)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shooting(self):
        if self.cool_down_counter == 0:
            Bullet = bullet(self.x, self.y, self.Bullet_Img)
            self.Bullets.append(Bullet)
            self.cool_down_counter = 1

    def get_height(self):
        return self.Char_Img.get_height()

    def get_width(self):
        return self.Char_Img.get_width()


class player(character):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health=health)
        self.Char_Img = PlayerImg
        self.Bullet_Img = BulletImg
        self.mask = pg.mask.from_surface(self.Char_Img)
        self.max_health = health

    def move_bullet(self, vel, objs):
        self.cooldown()
        for Bullet in self.Bullets:
            Bullet.move(vel)
            if Bullet.off_screen():
                self.Bullets.remove(Bullet)
            else:
                for obj in objs:
                    if Bullet.collision(obj):
                        boom_effect = pg.mixer.Sound(
                            (os.path.join("sound","2.mp3")))
                        boom_effect.play()
                        objs.remove(obj)
                        if Bullet in self.Bullets:
                            self.Bullets.remove(Bullet)

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pg.draw.rect(window, (255, 0, 0), (self.x, self.y +
                     self.Char_Img.get_height() + 10, self.Char_Img.get_width(), 10))
        pg.draw.rect(window, (0, 255, 0), (self.x, self.y + self.Char_Img.get_height() +
                     10, self.Char_Img.get_width() * (self.health/self.max_health), 10))


class enemy(character):
    COLOR_ENEMIES = {
        "red": (EnemyImg, EnemyImg),
        "green": (EnemyImg2, EnemyImg2),
        "blue": (EnemyImg6, EnemyImg6)
    }

    def __init__(self, x, y, color, health=50):
        super().__init__(x, y, health=health)
        self.Char_Img, self.Bullet_Img = self.COLOR_ENEMIES[color]
        self.mask = pg.mask.from_surface(self.Char_Img)

    def move(self, vel):
        self.x -= vel


def collide(obj1, obj2):
    offset_x = obj1.x - obj2.x
    offset_y = obj1.y - obj2.y
    return obj1.mask.overlap(obj2.mask, (int(offset_x), int(offset_y))) != None
# main


def main():
    FPS = 60
    win = False
    lost = False
    run = True
    level = 0
    shield = 5
    enemies = []
    wave_length = 0
    Player_vel = 8
    Enemy_vel = 0.8
    lost_count = 0
    win_count = 0
    main_font = pg.font.SysFont("Comicsian", 50)
    lost_font = pg.font.SysFont("Comicsian", 70)
    clock = pg.time.Clock()
    Player = player(10, 230, 300)
    music_in_game = pg.mixer.Sound(
                            (os.path.join("sound","1.mp3")))
    music_in_game.play()

    def Redraw_window():
        screen.blit(Background, (0, 0))
        lives_label = main_font.render(f"Shield: {shield}", 1, (0, 0, 255))
        level_label = main_font.render(f"Level: {level}", 1, (255, 255, 255))
        screen.blit(lives_label, (10, 10))
        screen.blit(level_label, (WIDTH - level_label.get_width()-10, 10))
        Player.draw(screen)
        for Enemy in enemies:
            Enemy.draw(screen)
        if lost == True:
            music_in_game.stop()
            screen.blit(Lost_screen, (0, 0))
            lost_label = lost_font.render(
                "CLICK TO PLAY AGAIN", 1, (255, 255, 255))
            screen.blit(lost_label, (WIDTH / 3, HEIGHT / 2))
        if win == True:
            music_in_game.stop()
            screen.blit(WINNER_screen, (0, 0))
        pg.display.update()
        
    while run:
        clock.tick(FPS)

        Redraw_window()
        if shield <= 0 or Player.health <= 0:
            lost = True
            lost_count += 1
        if level > 10:
            win = True
            win_count += 1
        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue
        if win:
            if win_count > FPS * 3:
                run = False
            else:
                continue
        if len(enemies) == 0:
            level += 1
            wave_length += 15
            Enemy_vel += 0.25
            for i in range(wave_length):
                Enemy = enemy(random.randrange(WIDTH, WIDTH + level * 500),
                              random.randrange(75, HEIGHT - 75), random.choice(["red", "green", "blue"]))
                enemies.append(Enemy)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                run = False

        key_pressed = pg.key.get_pressed()
        if key_pressed[pg.K_a] and Player.x - Player_vel > 0:
            Player.x -= Player_vel
        if key_pressed[pg.K_d] and Player.x + Player_vel < WIDTH - Player.get_width():
            Player.x += Player_vel
        if key_pressed[pg.K_w] and Player.y - Player_vel > 0:
            Player.y -= Player_vel
        if key_pressed[pg.K_s] and Player.y + Player_vel < HEIGHT - Player.get_height():
            Player.y += Player_vel
        if key_pressed[pg.K_SPACE]:
            Player.shooting()
            shooting_sound = pg.mixer.Sound(
                (os.path.join("sound","6.mp3")))
            shooting_sound.play()
        for Enemy in enemies[:]:
            Enemy.move(Enemy_vel)
            if Enemy.x < 0:
                shield -= 1
                enemies.remove(Enemy)
            if collide(Enemy, Player):
                Player.health -= 25
                enemies.remove(Enemy)
            elif Enemy.x - Enemy.get_width() < 0:
                shield -= 1
                enemies.remove(Enemy)
        Player.move_bullet(-15, enemies)


def main_menu():
    global lost
    screen.blit(Menu_screen, (0, 0))
    menu_sound = pg.mixer.Sound(os.path.join("sound","3.mp3"))
    menu_sound.play()
    pg.display.update()
    play = True
    while play:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                play = False
            if event.type == pg.MOUSEBUTTONDOWN:
                menu_sound.stop()
                main()
    pg.quit()


main_menu()
