import pygame
from pygame.locals import *
import random
import os

pygame.init()

pygame.mixer.init()
pygame.mixer.music.load("musica_fondo.mp3")  
pygame.mixer.music.play(-1) 

width, height = 700, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("ForOne")


gray = (100, 100, 100)
gray_s = (100, 100, 100)
red = (200, 0, 0)
white = (255, 255, 255)
yellow = (255, 232, 0)


road_width = 300
marker_width, marker_height = 10, 50
left_lane, center_lane, right_lane = 150, 250, 350
lanes = [left_lane, center_lane, right_lane]
road = (100, 0, road_width, height)
left_edge_marker = (95, 0, marker_width, height)
right_edge_marker = (395, 0, marker_width, height)


player_x, player_y = center_lane, 400
lane_marker_move_y = 0
clock = pygame.time.Clock()
fps = 120
speed = 2
score = 0

state = 'intro'
input_text = ''
SCORE_FILE = 'scores.txt'


def guardar_score(nombre, puntos):
    with open(SCORE_FILE, 'a') as f:
        f.write(f"{nombre},{puntos}\n")

def obtener_ranking(top=5):
    if not os.path.exists(SCORE_FILE):
        return []
    with open(SCORE_FILE, 'r') as f:
        scores = []
        for line in f:
            parts = line.strip().split(',')
            if len(parts) == 2 and parts[1].isdigit():
                scores.append((parts[0], int(parts[1])))
        return sorted(scores, key=lambda x: x[1], reverse=True)[:top]


class Vehicle(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        super().__init__()
        scale = 45 / image.get_rect().width
        new_size = (int(image.get_rect().width * scale), int(image.get_rect().height * scale))
        self.image = pygame.transform.scale(image, new_size)
        self.rect = self.image.get_rect(center=(x, y))

class PlayerVehicle(Vehicle):
    def __init__(self, x, y):
        image = pygame.image.load('images/car.png')
        super().__init__(image, x, y)

player_group = pygame.sprite.Group()
vehicle_group = pygame.sprite.Group()
player = PlayerVehicle(player_x, player_y)
player_group.add(player)

vehicle_filenames = ['pickup_truck.png', 'semi_trailer.png', 'taxi.png', 'van.png']
vehicle_images = [pygame.image.load('images/' + name) for name in vehicle_filenames]
crash = pygame.image.load('images/crash.png')
crash_rect = crash.get_rect()

running = True
gameover = False


while running:
    clock.tick(fps)

    
    if state == 'intro':
        screen.fill(gray_s)
        font = pygame.font.Font(None, 28)
        prompt = font.render('Ingresa tu nombre y presiona ENTER:', True, white)
        prompt_rect = prompt.get_rect(center=(width // 2, height // 2 - 60))
        screen.blit(prompt, prompt_rect)

        input_font = pygame.font.Font(None, 32)
        input_box = pygame.Rect(width // 2 - 100, height // 2, 200, 32)
        pygame.draw.rect(screen, white, input_box, 2)
        input_surface = input_font.render(input_text, True, white)
        screen.blit(input_surface, (input_box.x + 5, input_box.y + 5))

        ranking_text = font.render("Presiona 'R' para ver el ranking", True, yellow)
        screen.blit(ranking_text, (width // 2 - 130, height // 2 + 50))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN:
                if event.key == K_RETURN and input_text.strip() != '':
                    player_name = input_text.strip()
                    state = 'game'
                elif event.key == K_BACKSPACE:
                    input_text = input_text[:-1]
                elif event.key == K_r:
                    state = 'ranking'
                else:
                    if len(input_text) < 15:
                        input_text += event.unicode
        continue

    
    if state == 'ranking':
        screen.fill((30, 30, 30))
        font = pygame.font.Font(None, 32)
        title = font.render("🏆 RANKING DE PUNTAJES", True, white)
        screen.blit(title, title.get_rect(center=(width // 2, 40)))

        ranking = obtener_ranking()
        for i, (nombre, puntos) in enumerate(ranking, 1):
            entry = font.render(f"{i}. {nombre} - {puntos}", True, yellow)
            screen.blit(entry, (width // 2 - 100, 80 + i * 30))

        note = font.render("Presiona 'B' para volver", True, white)
        screen.blit(note, note.get_rect(center=(width // 2, 350)))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN and event.key == K_b:
                state = 'intro'
                input_text = ''
        continue

    
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

        if event.type == KEYDOWN and not gameover:
            idx = lanes.index(player.rect.centerx)
            if event.key == K_LEFT and idx > 0:
                player.rect.centerx = lanes[idx - 1]
            elif event.key == K_RIGHT and idx < len(lanes) - 1:
                player.rect.centerx = lanes[idx + 1]

    screen.fill(gray_s)
    pygame.draw.rect(screen, gray, road)
    pygame.draw.rect(screen, yellow, left_edge_marker)
    pygame.draw.rect(screen, yellow, right_edge_marker)

    lane_marker_move_y += speed * 2
    if lane_marker_move_y >= marker_height * 2:
        lane_marker_move_y = 0
    for y in range(-marker_height * 2, height, marker_height * 2):
        pygame.draw.rect(screen, white, (left_lane + 45, y + lane_marker_move_y, marker_width, marker_height))
        pygame.draw.rect(screen, white, (center_lane + 45, y + lane_marker_move_y, marker_width, marker_height))

    player_group.draw(screen)

    if len(vehicle_group) < 2:
        if all(v.rect.top >= v.rect.height * 1.5 for v in vehicle_group):
            lane = random.choice(lanes)
            image = random.choice(vehicle_images)
            vehicle = Vehicle(image, lane, height / -2)
            vehicle_group.add(vehicle)

    for vehicle in vehicle_group:
        vehicle.rect.y += speed
        if vehicle.rect.top >= height:
            vehicle.kill()
            score += 1
            if score % 5 == 0:
                speed += 1

    vehicle_group.draw(screen)

    font = pygame.font.Font(None, 20)
    score_text = font.render(f"Score: {score}", True, white)
    screen.blit(score_text, (10, 10))

    if pygame.sprite.spritecollideany(player, vehicle_group):
        gameover = True
        crash_rect.center = [player.rect.centerx, player.rect.top]
        guardar_score(player_name, score)

    if gameover:
        screen.blit(crash, crash_rect)
        pygame.draw.rect(screen, red, (0, 50, width, 100))
        text = font.render('Game Over. ¿Jugar otra vez? (Y/N)', True, white)
        screen.blit(text, text.get_rect(center=(width // 2, 80)))

    pygame.display.update()

   
    while gameover:
        clock.tick(fps)
        for event in pygame.event.get():
            if event.type == QUIT:
                gameover = False
                running = False
            elif event.type == KEYDOWN:
                if event.key == K_y:
                    speed = 2
                    score = 0
                    vehicle_group.empty()
                    player.rect.center = [player_x, player_y]
                    state = 'game'
                    gameover = False
                elif event.key == K_n:
                    gameover = False
                    state = 'intro'
                    input_text = ''
                    vehicle_group.empty()
                    player.rect.center = [player_x, player_y]

pygame.quit()