import sys
import os
import pygame
import random


# Загрузка изображений
def load_image(name, color_key=None):
    fullname = os.path.join('images', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Не удаётся загрузить:', name)
        raise SystemExit(message)
    image = image.convert_alpha()
    if color_key is not None:
        if color_key is int('-1'):
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    return image


def main():
    global menu
    pygame.init()

    screen_size = screen_width, screen_height = (1920, 1080)     # Размер окна
    screen = pygame.display.set_mode(screen_size)
    pygame.display.set_caption('Космическое нашествие')
    background = pygame.transform.scale(load_image('long.png'), screen_size).convert()  # Задний фон
    x = 0  # Для движения фона
    alien_location = screen_height - 150
    step = 1    # скорость Корабля
    fps = 100

    ship = Ship(screen)     # Загрузка корабля
    all_sprites = pygame.sprite.Group()    # Для хранения всех спрайтов
    bullets = pygame.sprite.Group()   # Для хранения пуль
    fires = pygame.sprite.Group()     # Для хранения огня от пришельцев
    aliens = pygame.sprite.Group()     # Для хранения пришельцев
    meteorits = pygame.sprite.Group()   # Для хранения метеоритов
    heals = pygame.sprite.Group()    # Для хранения бонуса восполнения хп
    sheilds = pygame.sprite.Group()  # Для хранения бонуса защиты
    doubles = pygame.sprite.Group()  # Для хранения бонуса double

    pygame.key.set_repeat(1, 1)    # Для нормального движения корабля

    health = pygame.transform.scale(load_image('health.png'), (70, 50))

    clock = pygame.time.Clock()
    all_sprites.add(ship)

    # Для запуска начального меню, добавление музыки в игру
    if menu:
        main_menu(screen, screen_size)
        game_music()
        menu = False
    k = False
    score = 0
    start = 0

    win_1 = False
    win_2 = False
    # Для защиты корабля
    shield_of_ship = False
    shield_hp = 0

    hp = 5
    alien_hp = 50
    alien_hide = False

    restart = False
    running = True
    while running:
        clock.tick(fps)
        # До 4000 очков
        if score < 4000:
            if len(meteorits) < 20:
                if random.randint(0, 4) == 2:
                    if random.randint(0, 7) == 5:
                        meteor_size = 100
                    elif random.randint(0, 20) == 4:
                        meteor_size = 150
                    else:
                        meteor_size = 60
                    meteorit = Meteorit(screen, screen_size, meteor_size)
                    meteorits.add(meteorit)
                    all_sprites.add(meteorit)

            if hp < 5:
                if random.randint(0, 300) == 59:
                    new_heal = Heal(screen, screen_size)
                    heals.add(new_heal)
            if random.randint(0, 400) == 343:
                new_shield = Sheild(screen, screen_size)
                sheilds.add(new_shield)
            if random.randint(0, 500) == 342:
                new_double = Double(screen, screen_size)
                doubles.add(new_double)

        # До 10000 очков
        elif score < 10000:
            if len(meteorits) < 35:
                if random.randint(0, 4) == 2:
                    if random.randint(0, 5) == 5:
                        meteor_size = 100
                    elif random.randint(0, 7) == 4:
                        meteor_size = 150
                    else:
                        meteor_size = 60
                    meteorit = Meteorit(screen, screen_size, meteor_size)
                    meteorits.add(meteorit)
                    all_sprites.add(meteorit)
            if hp < 5:
                if random.randint(0, 200) == 7:
                    new_heal = Heal(screen, screen_size)
                    heals.add(new_heal)
            if random.randint(0, 400) == 343:
                new_shield = Sheild(screen, screen_size)
                sheilds.add(new_shield)
            if random.randint(0, 500) == 13:
                new_double = Double(screen, screen_size)
                doubles.add(new_double)

        else:
            if len(meteorits) == 0:
                if alien_location > -150:
                    new_alien = Alien(screen, screen_size, alien_location)
                    aliens.add(new_alien)
                    alien_location -= new_alien.alien_size + 15
            if k:
                win_1 = True
                running = False

        # Управление с клавиатуры
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Перемещение корабля
            # управление на стрелочки
            keys_pressed = pygame.key.get_pressed()
            if keys_pressed[pygame.K_UP]:
                if ship.rect.y > ship.screen_rect.top:
                    ship.rect.y -= step
            if keys_pressed[pygame.K_DOWN]:
                if ship.rect.y < (ship.screen_rect.bottom - ship.size):
                    ship.rect.y += step

            if keys_pressed[pygame.K_RIGHT]:
                if ship.rect.x < (2 * screen_width // 3):
                    ship.rect.x += step
            if keys_pressed[pygame.K_LEFT]:
                if ship.rect.x > 0:
                    ship.rect.x -= step

            # WASD - управление
            if pygame.key.get_pressed()[pygame.K_w]:
                if ship.rect.y > ship.screen_rect.top:
                    ship.rect.y -= step
            if pygame.key.get_pressed()[pygame.K_s]:
                if ship.rect.y < (ship.screen_rect.bottom - ship.size):
                    ship.rect.y += step
            if pygame.key.get_pressed()[pygame.K_d]:
                if ship.rect.x < (2 * screen_width // 3):
                    ship.rect.x += step
            if pygame.key.get_pressed()[pygame.K_a]:
                if ship.rect.x > 0:
                    ship.rect.x -= step

            # Принудительный выход на Q
            if pygame.key.get_pressed()[pygame.K_q]:
                sys.exit()

            # Выстрелы на ЛКМ, ПКМ и Колёсико
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Выстрел
                new_bullet = Bullet(screen, ship)
                new_bullet.sound_bullet()
                bullets.add(new_bullet)

        all_sprites.update()

        # Нанесение урона пришельцу
        if pygame.sprite.groupcollide(bullets, aliens, True, alien_hide):
            alien_hp -= 1
            if alien_hp <= 0:
                alien_hide = True
        if pygame.sprite.spritecollide(ship, aliens, True) or alien_hide:
            for alien in aliens.sprites():
                explosion = Explosion(alien.rect.center, alien.alien_size)
                aliens.remove(alien)
                all_sprites.add(explosion)
            if not alien_hide:
                win_2 = True
                running = False
            else:
                k = True

        # При взаимодействии метеоритов и пуль
        hits2 = pygame.sprite.groupcollide(meteorits, bullets, True, True)
        for hit in hits2:
            if hit:
                score += 10
            explosion = Explosion(hit.rect.center, hit.size)
            all_sprites.add(explosion)

        # При взаимодействии корабля и метеоритов
        for hit in pygame.sprite.spritecollide(ship, meteorits, True):
            if shield_of_ship == 1:
                shield_hp = 0
            else:
                if hp >= 0:
                    if hit.size > 140:
                        hp -= 2
                    else:
                        hp -= 1
                explosion = Explosion(ship.rect.center, ship.size - 20)
                all_sprites.add(explosion)

        if pygame.sprite.spritecollide(ship, doubles, True):
            start = 750
        start -= 1

        if pygame.sprite.spritecollide(ship, heals, True):
            if hp < 5:
                hp += 1

        if pygame.sprite.groupcollide(fires, bullets, True, True):
            pass
        if pygame.sprite.spritecollide(ship, fires, True):
            if shield_of_ship == 1:
                shield_hp = 0
            else:
                hp -= 2

        # Задаём цвет, получаем объекты, обновляем экран
        # Рисуем движущийся фон
        rel_x = x % background.get_rect().width
        screen.blit(background, (rel_x - background.get_rect().width, 0))
        if rel_x < screen_width:
            screen.blit(background, (rel_x, 0))
        x -= 5

        # Рисует пули
        for bullet in bullets.sprites():
            if start > 0:
                bullet.draw_double_bullet()
            else:
                bullet.draw_bullet()

        # Удаление пуль, вышедших за край экрана.
        for bullet in bullets.copy():
            if bullet.rect.left >= screen_width:
                bullets.remove(bullet)

        bullets.update()    # Перемещение пуль
        doubles.update()
        ship.print_ship()   # Корабль

        # Защита корабля
        if shield_of_ship:
            ship.print_shield()

        # Рисует пришельцев
        for alien in aliens.sprites():
            alien.print_alien()  # Пришелец
            if random.randint(1, 30) == 5:
                new_fire = Fire(screen, alien)
                fires.add(new_fire)

        # Рисует пули
        for fire in fires.sprites():
            fire.draw_fire()

        # Удаление пуль, вышедших за край экрана.
        for fire in fires.copy():
            if fire.rect.left >= screen_width:
                fires.remove(fire)

        aliens.update()
        fires.update()
        heals.update()
        sheilds.update()

        # Рисует метеориты
        for meteorit in meteorits.sprites():
            meteorit.print_meteorit()  # Метеориты

        # Удаление уничтоженных метеоритов
        for meteorit in meteorits.copy():
            if meteorit.rect.y < 0 or meteorit.rect.x < 0:
                meteorits.remove(meteorit)

        # Проверка на защиту
        if pygame.sprite.spritecollide(ship, sheilds, True):
            shield_of_ship = True
            shield_hp = 1
        if shield_hp == 0:
            shield_of_ship = False

        # Рисует сердечки
        for i in range(hp):
            screen.blit(health, (screen_width - 70 - 40 * i, 0))

        # Завершение игры
        if hp <= 0:
            running = False
            restart = True

        for sheild in sheilds.sprites():
            sheild.print_shield()
        for sheild in sheilds.copy():
            if sheild.rect.x <= 0:
                sheilds.remove(sheild)

        for double in doubles.sprites():
            double.print_double()
        for double in doubles.copy():
            if double.rect.x <= 0:
                doubles.remove(double)

        for heal in heals.copy():
            if heal.rect.x <= 0:
                heals.remove(heal)
        for heal in heals.sprites():
            heal.print_heal()

        screen.blit(pygame.font.SysFont(None, 50).render(str(int(clock.get_fps())), 100, (255, 235, 0)), (25, 25))
        screen.blit(pygame.font.SysFont(None, 50).render('score: ' + str(score), 100, ('red')), (25, screen_height - 50))

        all_sprites.draw(screen)
        pygame.display.flip()

    while win_1:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
        end = GameOver(screen, screen_size, '1')
        end.rendering()
    while win_2:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
        end = GameOver(screen, screen_size, '2')
        end.rendering()

    # Перезагрузка игры
    while restart:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                main()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                sys.exit()



def game_music():
    pygame.mixer.music.load("sounds/tgfcoder-FrozenJam-SeamlessLoop.ogg")
    pygame.mixer.music.play(-1)


def main_menu(screen, screen_size):
    pygame.mixer.music.load("sounds/menu.ogg")
    pygame.mixer.music.play(-1)

    title = pygame.transform.scale(pygame.image.load("images/main_menu.png"), (screen_size[0], screen_size[1]))
    width = screen_size[0]
    height = screen_size[1]

    screen.blit(title, (0, 0))
    pygame.display.update()

    while True:
        ev = pygame.event.poll()
        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_RETURN:
                break
            elif ev.key == pygame.K_q:
                sys.exit()
        elif ev.type == pygame.QUIT:
            sys.exit()
        else:
            text = pygame.font.Font(None, 70).render("Press [ENTER] To Begin", True, 'white')
            screen.blit(text, text.get_rect(center=(width / 2, height / 2 + 50)))

            text = pygame.font.Font(None, 70).render("or [Q] To Quit", True, 'white')
            screen.blit(text, text.get_rect(center=(width / 2, height / 2 + 120)))

            pygame.display.update()

    pygame.mixer.music.stop()
    pygame.mixer.Sound('sounds/getready.ogg').play()
    pygame.display.update()


# Класс Космического корабля
class Ship(pygame.sprite.Sprite):
    def __init__(self, screen):
        pygame.sprite.Sprite.__init__(self)
    # Инициализирует корабль и задает его начальную позицию.
        self.screen = screen
        self.size = 75

    # Загрузка изображения корабля и получение прямоугольника.
        self.image = pygame.transform.scale(load_image('ship.png'), (self.size, self.size))
        self.shield = pygame.transform.scale(load_image('sheild.png'), (self.size + 50, self.size + 50))

        self.rect = self.image.get_rect()
        self.screen_rect = screen.get_rect()

    # Каждый новый корабль появляется у посередине, снизу.
        self.rect.x = self.screen_rect.left
        self.rect.y = self.screen_rect.centery

    # Рисуем корабль
    def print_ship(self):
        self.screen.blit(self.image, self.rect)

    def print_shield(self):
        # Вывод пули на экран.
        self.screen.blit(self.shield, (self.rect.x - 25, self.rect.y - 25))


# Класс пули
class Bullet(pygame.sprite.Sprite):
    def __init__(self, screen, ship):
        pygame.sprite.Sprite.__init__(self)
        # Создает объект пули в текущей позиции корабля.
        super(Bullet, self).__init__()
        self.screen = screen
        # Создание пули в позиции (0,0) и назначение правильной позиции.
        self.bullet_width = 3
        self.bullet_height = 15
        self.rect = pygame.Rect(0, 0, self.bullet_width, self.bullet_height)

        self.rect.centerx = ship.rect.centerx
        self.rect.center = ship.rect.center

    # Позиция пули хранится в вещественном формате.
        # self.image = pygame.transform.scale(load_image('laser.png', -1), (17, 45))
        # self.image = pygame.transform.scale(load_image('laser.webp', -1), (40, 9))
        self.image = load_image('laser.webp')
        self.x = float(self.rect.x)
        self.y = self.rect.y
        self.bullet_speed = 10

    def update(self):
        # Перемещает пулю вверх по экрану.
        # Обновление позиции пули в вещественном формате.
        self.x += self.bullet_speed
        # Обновление позиции прямоугольника.
        self.rect.x = self.x
        self.rect.y = self.y

    def draw_bullet(self):
        # Вывод пули на экран.
        self.screen.blit(self.image, self.rect)

    def sound_bullet(self):
        self.ready = pygame.mixer.Sound(f'sounds/pew.wav')
        self.ready.set_volume(0.30)
        self.ready.play()

    def draw_double_bullet(self):
        self.rect.y -= 25
        self.screen.blit(self.image, self.rect)
        self.rect.y += 50
        self.screen.blit(self.image, self.rect)


# Класс пули
class Fire(pygame.sprite.Sprite):
    def __init__(self, screen, alien):
        pygame.sprite.Sprite.__init__(self)
        # Создает объект пули в текущей позиции корабля.
        self.screen = screen
        # Создание пули в позиции (0,0) и назначение правильной позиции.
        self.bullet_width = 3
        self.bullet_height = 15
        self.rect = pygame.Rect(0, 0, self.bullet_width, self.bullet_height)

        self.rect.centerx = alien.rect.centerx
        self.rect.center = alien.rect.center

    # Позиция пули хранится в вещественном формате.
        self.image = pygame.transform.scale(load_image('laser.png', -1), (70, 30))
        self.x = float(self.rect.x)
        self.bullet_speed = 10

    def update(self):
        # Перемещает пулю вверх по экрану.
        # Обновление позиции пули в вещественном формате.
        self.x -= self.bullet_speed
        # Обновление позиции прямоугольника.
        self.rect.x = self.x

    def draw_fire(self):
        # Вывод пули на экран.
        self.screen.blit(self.image, self.rect)


# Класс Пришельцев
class Alien(pygame.sprite.Sprite):
    def __init__(self, screen, screen_size, alien_location):
        self.screen = screen
        pygame.sprite.Sprite.__init__(self)
        self.alien_size = 150
        # Загрузка изображения пришельца и назначение атрибута rect.
        self.image = pygame.transform.scale(load_image('nlo2.png'), (250, self.alien_size))
        self.rect = self.image.get_rect()
        # Каждый новый пришелец появляется в правой стороне экрана.

        self.rect.y = alien_location #screen_size[1] // 2 - 80
        self.rect.x = screen_size[0]

        self.screen_size = screen_size
        self.speed = 5

        # Сохранение точной позиции пришельца.
        self.x = self.rect.x
        self.y = self.rect.y

    def update(self):
        # Перемещает метеорит влево по экрану.
        # Обновление позиции метеорита.
        if self.rect.x > 0:
            self.rect.x -= 5
        # Обновление позиции прямоугольника.
        self.rect.y = self.y

    def print_alien(self):
        # Выводит пришельца в текущем положении.
        self.screen.blit(self.image, self.rect)


# Класс Метеоритов
class Meteorit(pygame.sprite.Sprite):
    def __init__(self, screen, screen_size, meteor_size):
        self.screen = screen
        self.size = meteor_size
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(load_image('meteor.gif'), (meteor_size, meteor_size))
        self.rect = self.image.get_rect()

        self.rect.y = random.randrange(0, screen_size[1] - 60)
        self.rect.x = screen_size[0] - 50

        self.speedy = random.randrange(-3, 3)
        self.speedx = random.randrange(3, 13)

        self.x = self.rect.x
        self.y = self.rect.y

    def update(self):
        # Перемещает метеорит влево по экрану.
        # Обновление позиции метеорита.
        self.x -= self.speedx
        # Обновление позиции прямоугольника.
        self.rect.x = self.x

        self.y += self.speedy
        self.rect.y = self.y

    def print_meteorit(self):
        # Выводит пришельца в текущем положении.
        self.screen.blit(self.image, self.rect)


# Класс Взрывов
class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, explosion_size):
        pygame.sprite.Sprite.__init__(self)

        m1 = ['expl3.wav', 'expl6.wav']
        if random.randint(0, 3) == 2:
            i = 0
        else:
            i = 1
        self.ready = pygame.mixer.Sound(f'sounds/{m1[i]}')
        self.ready.set_volume(0.40)
        self.ready.play()

        self.size = 'lg'
        self.explosion_anim = {}
        self.explosion_anim['lg'] = []

        for i in range(9):
            filename = 'images/regularExplosion0{}.png'.format(i)
            img = pygame.image.load(filename).convert()
            img.set_colorkey("BLACK")
            img_lg = pygame.transform.scale(img, (explosion_size, explosion_size))
            self.explosion_anim['lg'].append(img_lg)

        self.image = self.explosion_anim[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(self.explosion_anim[self.size]):
                self.kill()
            else:
                center = self.rect.center
                self.image = self.explosion_anim[self.size][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center


# Класс бонуса: HEAL
class Heal(pygame.sprite.Sprite):
    def __init__(self, screen, screen_size):
        pygame.sprite.Sprite.__init__(self)
        # Создает объект пули в текущей позиции корабля.
        self.screen = screen

    # Позиция пули хранится в вещественном формате.
        self.image = pygame.transform.scale(load_image('heal.png'), (35, 35))

        self.rect = self.image.get_rect()
        self.screen_rect = screen.get_rect()

    # Каждый новый HEAL появляется справа.
        self.rect.y = random.randint(0, screen_size[1] - 50)
        self.rect.x = screen_size[0] - 50
        self.bullet_speed = 7

        self.x = self.rect.x


    def update(self):
        # Перемещает пулю вверх по экрану.
        # Обновление позиции пули в вещественном формате.
        self.x -= self.bullet_speed
        # Обновление позиции прямоугольника.
        self.rect.x = self.x

    def print_heal(self):
        # Вывод пули на экран.
        self.screen.blit(self.image, self.rect)


# Класс бонуса: SHEILD
class Sheild(pygame.sprite.Sprite):
    def __init__(self, screen, screen_size):
        pygame.sprite.Sprite.__init__(self)
        # Создает объект пули в текущей позиции корабля.
        self.screen = screen

    # Позиция пули хранится в вещественном формате.
        self.image = pygame.transform.scale(load_image('shield_gold.png'), (35, 35))

        self.rect = self.image.get_rect()
        self.screen_rect = screen.get_rect()

    # Каждый новый HEAL появляется справа.
        self.rect.y = random.randint(0, screen_size[1] - 50)
        self.rect.x = screen_size[0] - 50
        self.bullet_speed = 7

        self.x = self.rect.x


    def update(self):
        # Перемещает пулю вверх по экрану.
        # Обновление позиции пули в вещественном формате.
        self.x -= self.bullet_speed
        # Обновление позиции прямоугольника.
        self.rect.x = self.x

    def print_shield(self):
        # Вывод пули на экран.
        self.screen.blit(self.image, self.rect)


# Класс бонуса: double
class Double(pygame.sprite.Sprite):
    def __init__(self, screen, screen_size):
        pygame.sprite.Sprite.__init__(self)
        # Создает объект пули в текущей позиции корабля.
        self.screen = screen

    # Позиция пули хранится в вещественном формате.
        self.image = pygame.transform.scale(load_image('energy.png'), (35, 50))

        self.rect = self.image.get_rect()
        self.screen_rect = screen.get_rect()

    # Каждый новый HEAL появляется справа.
        self.rect.y = random.randint(0, screen_size[1] - 50)
        self.rect.x = screen_size[0] - 50
        self.bullet_speed = 7

        self.x = self.rect.x


    def update(self):
        # Перемещает пулю вверх по экрану.
        # Обновление позиции пули в вещественном формате.
        self.x -= self.bullet_speed
        # Обновление позиции прямоугольника.
        self.rect.x = self.x

    def print_double(self):
        # Вывод пули на экран.
        self.screen.blit(self.image, self.rect)


class GameOver:
    def __init__(self, screen, screen_size, variant):
        self.screen = screen
        self.image = pygame.transform.scale(pygame.image.load(f"images/win{variant}.png"), screen_size)
        self.pos_y = -self.image.get_rect().h
        self.speed = 250

    def rendering(self):
        clock = pygame.time.Clock()
        while self.pos_y < 0:
            self.screen.blit(self.image, (0, int(self.pos_y)))
            self.pos_y += clock.tick() / 1000 * self.speed
            pygame.display.flip()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    key = pygame.key.get_pressed()
                    if key[pygame.K_q]:
                        pygame.quit()
                        sys.exit()


if __name__ == '__main__':
    menu = True
    main()