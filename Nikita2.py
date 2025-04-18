import pygame
import os
import random
import csv
import button


pygame.init()


win_wid = 800
win_hei = int(win_wid * 0.8)

window = pygame.display.set_mode((win_wid, win_hei))
pygame.display.set_caption('gun')
clock = pygame.time.Clock()
fps = 60

gravity = 0.75
thresh = 200

rows = 16
las = 150

blocks = win_hei // rows
blocks_t = 13
screen_scroll = 0
bg_scroll = 0
maxlevel = 1
start_game = False

left = False
right = False
shoot = False
gren = False
gren_thrown = False

pines_img = pygame.image.load('img/background/pine1.png').convert_alpha()
sky_img = pygame.image.load('img/background/sky_cloud.png').convert_alpha()
start_img = pygame.image.load('img/start_btn.png').convert_alpha()
exit_img = pygame.image.load('img/exit_btn.png').convert_alpha()
restart_img = pygame.image.load('img/restart_btn.png').convert_alpha()
img_list = []
for x in range(blocks_t):
	img = pygame.image.load(f'img/tile/{x}.png')
	img = pygame.transform.scale(img, (blocks, blocks))
	img_list.append(img)
	
bullet_img = pygame.image.load('img/pop/bullet/bullet.png').convert_alpha()
gren_img = pygame.image.load('img/pop/bullet/gren.png').convert_alpha()
health_box_img = pygame.image.load('img/pop/health_box.png').convert_alpha()
ammo_box_img = pygame.image.load('img/pop/ammo_box.png').convert_alpha()
gren_box_img = pygame.image.load('img/pop/grenade_box.png').convert_alpha()
item_boxes = {
	'Health'	: health_box_img,
	'Ammo'		: ammo_box_img,
	'Grenade'	: gren_box_img
}
BG = (144, 201, 120)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
font = pygame.font.SysFont('Arial', 20)

def draw_text(text, font, text_col, x, y):
	img = font.render(text, True, text_col)
	window.blit(img, (x, y))


def draw_bg():
	window.fill(BG)
	width = sky_img.get_width()
	for x in range(5):
		window.blit(sky_img, ((x * width) - bg_scroll * 0.5, 0))
		window.blit(pines_img, ((x * width) - bg_scroll * 0.7, win_hei - pines_img.get_height() - 150))


def reset_level():
	enemy_group.empty()
	bullet_group.empty()
	gren_group.empty()
	explosion_group.empty()
	item_box_group.empty()
	decoration_group.empty()
	water_group.empty()
	exit_group.empty()

	#x
	data = []
	for row in range(rows):
		r = [-1] * las
		data.append(r)

	return data


class Player(pygame.sprite.Sprite):
	def __init__(self, char_t, x, y, scale, speed, ammo, grens):
		pygame.sprite.Sprite.__init__(self)
		self.alive = True
		self.char_t = char_t
		self.speed = speed
		self.ammo = ammo
		self.start_ammo = ammo
		self.shoot_cld = 0
		self.grens = grens
		self.health = 100
		
		self.max_health = self.health
		self.dir = 1
		self.vel_y = 0
		self.jump = False
		self.in_air = True
		self.flip = False
		self.animation_list = []
		self.frame_id = 0
		self.action = 0
		self.update_time = pygame.time.get_ticks()
		
		self.move_counter = 0
		self.vision = pygame.Rect(0, 0, 150, 20)
		self.idling = False
		self.idling_counter = 0
		ani_types = ['calmanim', 'walkanim', 'jump', 'death']
		for ani in ani_types:
			temp_list = []
			num_of_frames = len(os.listdir(f'img/{self.char_t}/{ani}'))
			for i in range(num_of_frames):
				img = pygame.image.load(f'img/{self.char_t}/{ani}/{i}.png').convert_alpha()
				img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
				temp_list.append(img)
			self.animation_list.append(temp_list)

		self.image = self.animation_list[self.action][self.frame_id]
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)
		self.width = self.image.get_width()
		self.height = self.image.get_height()


	def update(self):
		self.update_animation()
		self.check_alive()
		if self.shoot_cld > 0:
			self.shoot_cld -= 1


	def move(self, left, right):
		screen_scroll = 0
		x1 = 0
		y1 = 0

		if left:
			x1 = -self.speed
			self.flip = True
			self.dir = -1
		if right:
			x1 = self.speed
			self.flip = False
			self.dir = 1

		if self.jump == True and self.in_air == False:
			self.vel_y = -11
			self.jump = False
			self.in_air = True

		self.vel_y += gravity
		if self.vel_y > 10:
			self.vel_y
		y1 += self.vel_y

		for tile in world.obstacle_list:
			if tile[1].colliderect(self.rect.x + x1, self.rect.y, self.width, self.height):
				x1 = 0
				if self.char_t == 'enemy':
					self.dir *= -1
					self.move_counter = 0
			if tile[1].colliderect(self.rect.x, self.rect.y + y1, self.width, self.height):
				if self.vel_y < 0:
					self.vel_y = 0
					y1 = tile[1].bottom - self.rect.top
				elif self.vel_y >= 0:
					self.vel_y = 0
					self.in_air = False
					y1 = tile[1].top - self.rect.bottom
		if pygame.sprite.spritecollide(self, water_group, False):
			self.health = 0

		level_complete = False
		if pygame.sprite.spritecollide(self, exit_group, False):
			level_complete = True

		
		if self.rect.bottom > win_hei:
			self.health = 0

		if self.char_t == 'pop':
			if self.rect.left + x1 < 0 or self.rect.right + x1 > win_wid:
				x1 = 0

		self.rect.x += x1
		self.rect.y += y1

		if self.char_t == 'pop':
			if (self.rect.right > win_wid - thresh and bg_scroll < (world.level_length * blocks) - win_wid) or (self.rect.left < thresh and bg_scroll > abs(x1)):
				self.rect.x -= x1
				screen_scroll = -x1

		return screen_scroll, level_complete
	def shoot(self):
		if self.shoot_cld == 0 and self.ammo > 0:
			self.shoot_cld = 20
			bullet = Bullet(self.rect.centerx + (0.75 * self.rect.size[0] * self.dir), self.rect.centery, self.dir)
			bullet_group.add(bullet)
			self.ammo -= 1


	def ai(self):
		if self.alive and player.alive:
			if self.idling == False and random.randint(1, 200) == 1:
				self.update_action(0)
				self.idling = True
				self.idling_counter = 50
			if self.vision.colliderect(player.rect):
				self.update_action(0)
				self.shoot()
			else:
				if self.idling == False:
					if self.dir == 1:
						ai_moving_right = True
					else:
						ai_moving_right = False
					ai_moving_left = not ai_moving_right
					self.move(ai_moving_left, ai_moving_right)
					self.update_action(1)
					self.move_counter += 1
					self.vision.center = (self.rect.centerx + 99 * self.dir, self.rect.centery + 30 * self.dir)

					if self.move_counter > blocks:
						self.dir *= -1
						self.move_counter *= -1
				else:
					self.idling_counter -= 1
					if self.idling_counter <= 0:
						self.idling = False
		self.rect.x += screen_scroll





	def update_animation(self):
		ani_cld = 100
		self.image = self.animation_list[self.action][self.frame_id]
		if pygame.time.get_ticks() - self.update_time > ani_cld:
			self.update_time = pygame.time.get_ticks()
			self.frame_id += 1
		if self.frame_id >= len(self.animation_list[self.action]):
			if self.action == 3:
				self.frame_id = len(self.animation_list[self.action]) - 1
			else:
				self.frame_id = 0



	def update_action(self, new_action):
		if new_action != self.action:
			self.action = new_action
			self.frame_id = 0
			self.update_time = pygame.time.get_ticks()



	def check_alive(self):
		if self.health <= 0:
			self.health = 0
			self.speed = 0
			self.alive = False
			self.update_action(3)


	def draw(self):
		window.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)


class World():
	def __init__(self):
		self.obstacle_list = []

	def process_data(self, data):
		self.level_length = len(data[0])
		for y, row in enumerate(data):
			for x, tile in enumerate(row):
				if tile >= 0:
					img = img_list[tile]
					img_rect = img.get_rect()
					img_rect.x = x * blocks
					img_rect.y = y * blocks
					tile_data = (img, img_rect)
					if tile == 0 or tile == 2 or tile == 10 or tile == 5:
						self.obstacle_list.append(tile_data)
					elif tile == 4:
						water = Water(img, x * blocks, y * blocks)
						water_group.add(water)
					elif tile == 11 or tile == 12:
						decoration = Decoration(img, x * blocks, y * blocks)
						decoration_group.add(decoration)
					elif tile == 1:
						player = Player('pop', x * blocks, y * blocks, 1.65, 5, 20, 5)
						health_bar = HealthBar(10, 10, player.health, player.health)
					elif tile == 3:
						enemy = Player('enemy', x * blocks, y * blocks, 1.65, 2, 20, 0)
						enemy_group.add(enemy)
					elif tile == 6:
						item_box = ItemBox('Ammo', x * blocks, y * blocks)
						item_box_group.add(item_box)
					elif tile == 7:
						item_box = ItemBox('Grenade', x * blocks, y * blocks)
						item_box_group.add(item_box)
					elif tile == 8:
						item_box = ItemBox('Health', x * blocks, y * blocks)
						item_box_group.add(item_box)
					elif tile == 9:
						exit = Exit(img, x * blocks, y * blocks)
						exit_group.add(exit)

		return player, health_bar


	def draw(self):
		for tile in self.obstacle_list:
			tile[1][0] += screen_scroll
			window.blit(tile[0], tile[1])


class Decoration(pygame.sprite.Sprite):
	def __init__(self, img, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = img
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + blocks // 2, y + (blocks - self.image.get_height()))
	def update(self):
		self.rect.x += screen_scroll

class Water(pygame.sprite.Sprite):
	def __init__(self, img, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = img
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + blocks // 2, y + (blocks - self.image.get_height()))
	def update(self):
		self.rect.x += screen_scroll

class Exit(pygame.sprite.Sprite):
	def __init__(self, img, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = img
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + blocks // 2, y + (blocks - self.image.get_height()))

	def update(self):
		self.rect.x += screen_scroll

class ItemBox(pygame.sprite.Sprite):
	def __init__(self, item_type, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.item_type = item_type
		self.image = item_boxes[self.item_type]
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + blocks // 2, y + (blocks - self.image.get_height()))


	def update(self):
		self.rect.x += screen_scroll
		if pygame.sprite.collide_rect(self, player):
			if self.item_type == 'Health':
				player.health += 25
				if player.health > player.max_health:
					player.health = player.max_health
			elif self.item_type == 'Ammo':
				player.ammo += 15
			elif self.item_type == 'Grenade':
				player.grens += 3
			self.kill()


class HealthBar():
	def __init__(self, x, y, health, max_health):
		self.x = x
		self.y = y
		self.health = health
		self.max_health = max_health

	def draw(self, health):
		self.health = health
		ratio = self.health / self.max_health
		pygame.draw.rect(window, BLACK, (self.x - 2, self.y - 2, 154, 24))
		pygame.draw.rect(window, RED, (self.x, self.y, 150, 20))
		pygame.draw.rect(window, GREEN, (self.x, self.y, 150 * ratio, 20))


class Bullet(pygame.sprite.Sprite):
	def __init__(self, x, y, dir):
		pygame.sprite.Sprite.__init__(self)
		self.speed = 10
		self.image = bullet_img
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)
		self.dir = dir

	def update(self):
		self.rect.x += (self.dir * self.speed) + screen_scroll
		if self.rect.right < 0 or self.rect.left > win_wid:
			self.kill()
		for tile in world.obstacle_list:
			if tile[1].colliderect(self.rect):
				self.kill()
		if pygame.sprite.spritecollide(player, bullet_group, False):
			if player.alive:
				player.health -= 8
				self.kill()
		for enemy in enemy_group:
			if pygame.sprite.spritecollide(enemy, bullet_group, False):
				if enemy.alive:
					enemy.health -= 25
					self.kill()



class Grenade(pygame.sprite.Sprite):
	def __init__(self, x, y, dir):
		pygame.sprite.Sprite.__init__(self)
		self.timer = 100
		self.vel_y = -11
		self.speed = 7
		self.image = gren_img
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)
		self.width = self.image.get_width()
		self.height = self.image.get_height()
		self.dir = dir

	def update(self):
		self.vel_y += gravity
		x1 = self.dir * self.speed
		y1 = self.vel_y
		for tile in world.obstacle_list:
			if tile[1].colliderect(self.rect.x + x1, self.rect.y, self.width, self.height):
				self.dir *= -1
				x1 = self.dir * self.speed
			if tile[1].colliderect(self.rect.x, self.rect.y + y1, self.width, self.height):
				self.speed = 0
				if self.vel_y < 0:
					self.vel_y = 0
					y1 = tile[1].bottom - self.rect.top
				elif self.vel_y >= 0:
					self.vel_y = 0
					y1 = tile[1].top - self.rect.bottom	
		self.rect.x += x1 + screen_scroll
		self.rect.y += y1
		self.timer -= 1
		if self.timer <= 0:
			self.kill()
			explosion = Explosion(self.rect.x, self.rect.y, 0.5)
			explosion_group.add(explosion)
			if abs(self.rect.centerx - player.rect.centerx) < blocks * 2 and \
				abs(self.rect.centery - player.rect.centery) < blocks * 2:
				player.health -= 50
			for enemy in enemy_group:
				if abs(self.rect.centerx - enemy.rect.centerx) < blocks * 2 and \
					abs(self.rect.centery - enemy.rect.centery) < blocks * 2:
					enemy.health -= 50



class Explosion(pygame.sprite.Sprite):
	def __init__(self, x, y, scale):
		pygame.sprite.Sprite.__init__(self)
		self.images = []
		for num in range(1, 5 ):
			img = pygame.image.load(f'img/expl/ex{num}.png').convert_alpha()
			img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
			self.images.append(img)
		self.frame_id = 0
		self.image = self.images[self.frame_id]
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)
		self.counter = 0


	def update(self):
		self.rect.x += screen_scroll
		expl_speed = 4
		self.counter += 1

		if self.counter >= expl_speed:
			self.counter = 0
			self.frame_id += 1
			if self.frame_id >= len(self.images):
				self.kill()
			else:
				self.image = self.images[self.frame_id]
start_button = button.Button(win_wid // 2 - 130, win_hei // 2 - 150, start_img, 1)
exit_button = button.Button(win_wid // 2 - 110, win_hei // 2 + 50, exit_img, 1)
restart_button = button.Button(win_wid // 2 - 100, win_hei // 2 - 50, restart_img, 2)
enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
gren_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()


world_data = []
for row in range(rows):
	r = [-1] * las
	world_data.append(r)
with open(f'level1_data.csv', newline='') as csvfile:
	reader = csv.reader(csvfile, delimiter=',')
	for x, row in enumerate(reader):
		for y, tile in enumerate(row):
			world_data[x][y] = int(tile)
world = World()
player, health_bar = world.process_data(world_data)



on = True
while on:

	clock.tick(fps)
	if start_game == False:
		window.fill(BG)
		if start_button.draw(window):
			start_game = True
		if exit_button.draw(window):
			run = False

	else:
		draw_bg()
		world.draw()
		health_bar.draw(player.health)
		draw_text('ammo: ', font, WHITE, 10, 35)
		for x in range(player.ammo):
			window.blit(bullet_img, (90 + (x * 10), 40))
		draw_text('grenades: ', font, WHITE, 10, 60)
		for x in range(player.grens):
			window.blit(gren_img, (135 + (x * 15), 60))


		player.update()
		player.draw()

		for enemy in enemy_group:
			enemy.ai()
			enemy.update()
			enemy.draw()

		bullet_group.update()
		gren_group.update()
		explosion_group.update()
		item_box_group.update()
		decoration_group.update()
		water_group.update()
		exit_group.update()
		bullet_group.draw(window)
		gren_group.draw(window)
		explosion_group.draw(window)
		item_box_group.draw(window)
		decoration_group.draw(window)
		water_group.draw(window)
		exit_group.draw(window)


		if player.alive:
			if shoot:
				player.shoot()
			elif gren and gren_thrown == False and player.grens > 0:
				gren = Grenade(player.rect.centerx + (0.5 * player.rect.size[0] * player.dir),player.rect.top, player.dir)
				gren_group.add(gren)
				player.grens -= 1
				gren_thrown = True
			if player.in_air:
				player.update_action(2)
			elif left or right:
				player.update_action(1)
			else:
				player.update_action(0)
			screen_scroll, level_complete = player.move(left, right)
			bg_scroll -= screen_scroll
			if level_complete:
				bg_scroll = 0
				world_data = reset_level()
				with open(f'level{1}_data.csv', newline='') as csvfile:
					reader = csv.reader(csvfile, delimiter=',')
					for x, row in enumerate(reader):
						for y, tile in enumerate(row):
							world_data[x][y] = int(tile)
					world = World()
					player, health_bar = world.process_data(world_data)	
		else:
			screen_scroll = 0
			if restart_button.draw(window):
				bg_scroll = 0
				world_data = reset_level()
				with open(f'level{1}_data.csv', newline='') as csvfile:
					reader = csv.reader(csvfile, delimiter=',')
					for x, row in enumerate(reader):
						for y, tile in enumerate(row):
							world_data[x][y] = int(tile)
				world = World()
				player, health_bar = world.process_data(world_data)



	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			on = False
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_a:
				left = True
			if event.key == pygame.K_d:
				right = True
			if event.key == pygame.K_SPACE:
				shoot = True
			if event.key == pygame.K_q:
				gren = True
			if event.key == pygame.K_w and player.alive:
				player.jump = True
			if event.key == pygame.K_ESCAPE:
				on = False


		if event.type == pygame.KEYUP:
			if event.key == pygame.K_a:
				left = False
			if event.key == pygame.K_d:
				right = False
			if event.key == pygame.K_SPACE:
				shoot = False
			if event.key == pygame.K_q:
				gren = False
				gren_thrown = False


	pygame.display.update()

pygame.quit()