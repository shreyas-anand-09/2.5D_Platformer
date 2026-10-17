import timeit

from ursina import *
app = Ursina() #initializes the window gng
game_started = False
#goal point for level 1, will be edited as the levels increase
goal = Entity(
    model='cube',
    color=color.gold,
    position=(18, 5.5, 0),
    scale=(1, 1, 1),
    collider='box')
goal.disable()
#intializing the player models and platforms
player=Entity(model="cube",color=color.cyan,scale=(1,1,1),collider="box")
player.velocity_y=0
level_1_data = [
    # (position), (scale)
    ((0, -3, 0), (15, 0.5, 5)),
    ((6, 0.5, 0), (4, 0.5, 3)),
    ((12, 2.5, 0), (4, 0.5, 3)),
    ((18, 4.5, 0), (5, 0.5, 3)),
    ((12, 6.5, 0), (3, 0.5, 3))]

# Automatically spawn all platforms from the list
platforms = []
for pos, scl in level_1_data:
    p = Entity(
        model='cube',
        color=color.green,
        position=pos,
        scale=scl,
        collider='box'
    )
    platforms.append(p)

player.grounded=False

#camera views to make it 2d(for now)
camera.orthographic = True
camera.fov = 10
camera.parent = player

#setting game states and menu screen
menu_parent=Entity()
player.disable()
for p in platforms:
    p.disable()
#menu
title_text = Text(
    text='MY 2.5D PLATFORMER',
    scale=40,
    origin=(0, 0),
    y=0.25,
    parent=menu_parent,
    color=color.green,)
start_button = Button(
    text='Start Game',
    scale=(5,3),
    y=-3,
    color=color.azure,
    parent=menu_parent)

def game_state(state):
    global game_started
    player.disable()
    menu_parent.disable()
    goal.disable()
    for p in platforms:
        p.disable()
    if state=="MENU":
        game_started = False
        menu_parent.enable()
        player.position=(0,-2,0)
    elif state=="PLAY":
        game_started = True
        menu_parent.disable()
        player.enable()
        for p in platforms:
            p.enable()
        goal.enable()

def start_game():
    game_state("PLAY")

start_button.on_click=start_game

#main game loop
def update():
    if not(game_started):
        return
    if held_keys['a']:
        player.x-=5*time.dt
    if held_keys['d']:
        player.x+=5*time.dt
    player.velocity_y-=9.8*time.dt
    next_y=player.y+player.velocity_y*time.dt
    ceil_ray = raycast(origin=player.position, direction=(0, 1, 0), distance=(player.scale_y / 2) + 0.1, ignore=(player,))
    floor_ray = raycast(origin=player.position, direction=(0, -1, 0), distance=(player.scale_y / 2) + 0.1, ignore=(player,))
    if floor_ray.hit and player.velocity_y<=0:
        player.velocity_y=0
        player.y = floor_ray.world_point.y + (player.scale_y / 2)
        player.grounded=True
    elif ceil_ray.hit and player.velocity_y>=0:
        player.velocity_y=0
        player.y = ceil_ray.world_point.y - (player.scale_y / 2)
    elif player.intersects(goal).hit:
        game_state('MENU')
        return
    else:
        if not(player.velocity_y>0 and ceil_ray.hit):
            player.grounded=False
            player.y += player.velocity_y * time.dt

def input(key):
    if not(game_started):
        return
    if key == 'space' and player.velocity_y == 0:
        player.velocity_y+=500*time.dt
        player.grounded=False
        update()

game_state("MENU")
app.run()