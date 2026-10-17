import timeit

from ursina import *
app = Ursina() #initializes the window gng
game_started = False
player=Entity(model="cube",color=color.cyan,scale=(1,1,1),collider="box")
score = 0
# A simple sword attached to the player
sword = Entity(
    parent=player,        # This makes the sword follow the player everywhere!
    model='cube',
    color=color.light_gray,
    scale=(0.8, 0.15, 0.15),
    position=(0.7, 0, 0),
    collider='box')
#score for coins:
score_text = Text(
    text='Score: 0',
    position=(-0.65, 0.45),  # top left corner of the screen
    scale=1.5,
    parent=camera.ui)        # this locks it to the UI camera overlay

score_text.disable()  # Hidden on the main menu by default
#spawning the coins at some given pos(same logic as platforms):
coin_data = [
    (3, 1.5, 0),
    (9, 3.5, 0),
    (15, 7.5, 0)]
coins = []
for pos in coin_data:
    c = Entity(
        model='sphere',
        color=color.gold,
        position=pos,
        scale=0.5,
        collider='box'
    )
    coins.append(c)
    c.disable()
#creating a death system:
# Create a red hazard block on the ground or a platform
hazard = Entity(
    model='cube',
    color=color.red,
    position=(8, 1.5, 0),  # Placed on a platform mid-level
    scale=(1.5, 0.5, 1),
    collider='box')
hazard.disable()  # Hidden on main menu initially

#goal point for level 1, will be edited as the levels increase
goal = Entity(
    model='cube',
    color=color.gold,
    position=(18, 5.5, 0),
    scale=(1, 1, 1),
    collider='box')
goal.disable()

#enemies:
mob = Entity(
    model='cube',
    color=color.red,
    position=(7, 1.5, 0),
    scale=(1, 1.5, 1),
    collider='box')
mob_hp=3
#intializing the player models and platforms
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

# Player combat stats
player_damage = 1

# Sword Data: catalog of available weapons
swords = {
    'Basic Sword':  {'damage': 1, 'price': 0,  'unlocked': True,  'color': color.light_gray},
    'Iron Sword':   {'damage': 2, 'price': 10, 'unlocked': False, 'color': color.cyan},
    'Flame Sword':  {'damage': 4, 'price': 25, 'unlocked': False, 'color': color.orange}}

#camera views to make it 2d(for now)
camera.orthographic = True
camera.fov = 10
camera.parent = player

#setting game states and menu screen
menu_parent=Entity()
death_parent=Entity()
player.disable()
for p in platforms:
    p.disable()
#death screen:
title_text_death = Text(
    text='YOU DIED',
    scale=40,
    origin=(0, 0),
    y=0.25,
    parent=death_parent,
    color=color.red,)
start_button_death = Button(
    text='Back to menu',
    scale=(5,3),
    y=-3,
    color=color.green,
    parent=death_parent)
#menu
title_text_menu = Text(
    text='MY 2.5D PLATFORMER',
    scale=40,
    origin=(0, 0),
    y=0.25,
    parent=menu_parent,
    color=color.green,)
start_button_menu = Button(
    text='Start Game',
    scale=(5,3),
    y=-3,
    color=color.azure,
    parent=menu_parent)

def game_state(state):
    global game_started,score
    player.disable()
    menu_parent.disable()
    goal.disable()
    sword.disable()
    mob.disable()
    hazard.disable()
    death_parent.disable()
    for p in platforms:
        p.disable()
    for c in coins:
        c.disable()
    if state=="MENU":
        game_started = False
        menu_parent.enable()
        player.position=(0,-2,0)
    elif state=="PLAY":
        game_started = True
        menu_parent.disable()
        player.enable()
        mob.enable()
        sword.enable()
        score_text.enable()
        hazard.enable()
        for p in platforms:
            p.enable()
        for c in coins:
            c.enable()
        goal.enable()
        score = 0
        score_text.text = 'Score: 0'
        player.position = (0, 1, 0)
        player.velocity_y = 0
    elif state=="DEATH":
        game_started = False
        death_parent.enable()
        player.position = (0, -2, 0)
        player.velocity_y = 0




def start_game():
    game_state("PLAY")
def menu():
    game_state("MENU")

start_button_menu.on_click=start_game
start_button_death.on_click=menu

#sword swinging animation:
is_attacking = False
has_hit=False
def reset_sword():
    global is_attacking
    sword.position = (0.7, 0, 0)  # Return to idle position
    is_attacking = False

def swing_sword():
    global is_attacking,has_hit
    if is_attacking:
        return  # Prevent spamming the swing while already attacking

    is_attacking = True
    has_hit = False

    #quickly animate the sword forward
    sword.animate_position((1.2, 0, 0), duration=0.1, curve=curve.linear)

    #reset it back to the side after a tiny delay
    invoke(reset_sword, delay=0.15)

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

    global mob_hp, is_attacking, has_hit,score
    if is_attacking and not has_hit and sword.intersects(mob).hit:
        # Check if the mob is still alive
        if mob_hp > 0:
            mob_hp -= 1
            mob.x += 0.5

            if mob_hp <= 0:
                mob.disable()
                score += 1

    for c in coins:
        if c.enabled and player.intersects(c).hit:
            c.disable()  # Hide the coin so it disappears
            score += 1  # Add 1 to the score
    score_text.text = f'Score: {score}'

    if (player.enabled and player.intersects(hazard).hit) or player.y < -5:
        game_state("DEATH")

    elif floor_ray.hit and player.velocity_y<=0:
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
    if key=="f":
        swing_sword()

def respawn_player():
    player.position = (0, 1, 0)
    player.velocity_y = 0



game_state("MENU")
app.run()