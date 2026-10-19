from ursina import *
from ursina.prefabs.sky import Sky
import math

app = Ursina()
transitioning = False
transition_timer=0
game_started = False
player = Entity(model="cube",color=color.white, scale=(1, 1, 1),texture="Screenshot 2026-10-19 215511" ,collider="box")
score = 0
current_level = 1
my_sky=Sky()
my_sky = Sky(color=color.rgb(20, 24, 33))
# Player combat stats & Health
player_damage = 1
player_hp = 3
max_player_hp = 3
damage_cooldown = 0
player_facing = 1

#level transitioning text:
transition_text = Text(text='', scale=2, origin=(0, 0), position=(0, 0), parent=camera.ui, color=color.yellow)
transition_text.disable()

# Sword Data: catalog of available weapons
swords = {
    'Basic Sword': {'damage': 1, 'price': 0, 'unlocked': True, 'color': color.light_gray},
    'Iron Sword': {'damage': 2, 'price': 10, 'unlocked': False, 'color': color.cyan},
    'Flame Sword': {'damage': 4, 'price': 25, 'unlocked': False, 'color': color.orange}
}

sword = Entity(
    parent=player,
    model='cube',
    color=color.light_gray,
    scale=(0.8, 0.15, 0.15),
    position=(1.0, 0, 0),
    collider='box'
)

# --- On-Screen HUD Elements ---
score_text = Text(text='Gold: 0', position=(-0.65, 0.45), scale=1.5, color=color.yellow, parent=camera.ui)
score_text.disable()

hud_weapon = Text(text='Weapon: Basic Sword (Dmg: 1)', position=(-0.65, 0.38), scale=1.2, color=color.light_gray,
                  parent=camera.ui)
hud_weapon.disable()

hud_hp = Text(text='HP: 3/3', position=(-0.65, 0.31), scale=1.2, color=color.red, parent=camera.ui)
hud_hp.disable()

hud_level = Text(text='Level: 1', position=(-0.65, 0.24), scale=1.2, color=color.cyan, parent=camera.ui)
hud_level.disable()

# --- Level Data Dictionary ---
all_levels = {
    1: {
        'platforms': [
            ((0, -3, 0), (8, 0.5, 5)),  # 1
            ((10, -2.0, 0), (4, 0.5, 3)),  # 2
            ((18, -0.5, 0), (4, 0.5, 3)),  # 3
            ((26, 1.0, 0), (4, 0.5, 3)),  # 4
            ((34, 2.5, 0), (4, 0.5, 3)),  # 5
            ((42, 4.0, 0), (4, 0.5, 3)),  # 6
            ((50, 5.5, 0), (4, 0.5, 3)),  # 7
            ((58, 7.0, 0), (4, 0.5, 3)),  # 8
            ((66, 8.5, 0), (4, 0.5, 3)),  # 9
            ((74, 10.0, 0), (4, 0.5, 3)),  # 10
            ((82, 11.5, 0), (4, 0.5, 3)),  # 11
            ((90, 13.0, 0), (4, 0.5, 3)),  # 12
            ((98, 14.5, 0), (5, 0.5, 3)),  # 13
            ((34, 0.5, 0), (3, 0.5, 3)),  # 14
            ((42, 2.0, 0), (3, 0.5, 3)),  # 15
            ((18, -4.0, 0), (4, 0.5, 3)),  # 16
            ((26, -2.5, 0), (4, 0.5, 3)),  # 17
            ((58, 5.0, 0), (4, 0.5, 3)),  # 18
            ((74, 7.5, 0), (4, 0.5, 3)),  # 19
            ((110, 15.0, 0), (8, 0.5, 3)),  # 20
        ],
        'moving': [
            ((5, -2.5, 0), (3, 0.5, 3), 2.5, 2.0),
            ((14, -1.2, 0), (3, 0.5, 3), 2.5, 2.2),
            ((22, 0.2, 0), (3, 0.5, 3), 2.5, 2.0),
            ((38, 3.2, 0), (3, 0.5, 3), 2.5, 2.5),
            ((54, 6.2, 0), (3, 0.5, 3), 2.5, 2.1),
            ((70, 9.2, 0), (3, 0.5, 3), 2.5, 2.4),
            ((86, 12.2, 0), (3, 0.5, 3), 2.5, 2.3),
        ],
        'coins': [
            (3, -2.0, 0), (6, -2.0, 0), (10, -1.0, 0), (14, -0.5, 0),
            (18, 0.5, 0), (22, 1.2, 0), (26, 2.0, 0), (30, 2.5, 0),
            (34, 3.5, 0), (38, 4.0, 0), (42, 5.0, 0), (46, 5.5, 0),
            (50, 6.5, 0), (54, 7.0, 0), (58, 8.0, 0), (62, 8.5, 0),
            (66, 9.5, 0), (70, 10.0, 0), (74, 11.0, 0), (78, 11.5, 0),
            (82, 12.5, 0), (86, 13.0, 0), (90, 13.5, 0), (94, 14.0, 0),
            (98, 14.5, 0), (34, 1.5, 0), (58, 6.0, 0), (74, 8.5, 0),
            (105, 15.0, 0), (110, 16.0, 0),
        ],
        'mobs': [
            (18, 0.0, 0), (34, 3.0, 0), (50, 6.0, 0),
            (66, 9.0, 0), (82, 12.0, 0), (98, 15.0, 0),
        ],
        'hazard': (26, -3.5, 0)
    },
    2: {
        'platforms': [
            ((0, -3, 0), (8, 0.5, 5)),  # 1
            ((12, -2.0, 0), (3, 0.5, 3)),  # 2
            ((22, -0.5, 0), (3, 0.5, 3)),  # 3
            ((32, 1.0, 0), (3, 0.5, 3)),  # 4
            ((42, 2.5, 0), (3, 0.5, 3)),  # 5
            ((52, 4.0, 0), (3, 0.5, 3)),  # 6
            ((62, 5.5, 0), (3, 0.5, 3)),  # 7
            ((72, 7.0, 0), (3, 0.5, 3)),  # 8
            ((82, 8.5, 0), (3, 0.5, 3)),  # 9
            ((92, 10.0, 0), (3, 0.5, 3)),  # 10
            ((100, 11.5, 0), (3, 0.5, 3)),  # 11
            ((105, 13.0, 0), (3, 0.5, 3)),  # 12
            ((110, 14.5, 0), (3, 0.5, 3)),  # 13
            ((32, -1.5, 0), (3, 0.5, 3)),  # 14
            ((52, 1.5, 0), (3, 0.5, 3)),  # 15
            ((22, -4.0, 0), (3, 0.5, 3)),  # 16
            ((32, -3.0, 0), (3, 0.5, 3)),  # 17
            ((62, 3.0, 0), (3, 0.5, 3)),  # 18
            ((82, 6.0, 0), (3, 0.5, 3)),  # 19
            ((110, 15.0, 0), (8, 0.5, 3)),  # 20
        ],
        'moving': [
            ((6, -2.5, 0), (2.5, 0.5, 3), 3.0, 2.5),
            ((17, -1.2, 0), (2.5, 0.5, 3), 3.5, 2.8),
            ((27, 0.2, 0), (2.5, 0.5, 3), 3.0, 2.6),
            ((47, 3.2, 0), (2.5, 0.5, 3), 3.5, 3.0),
            ((67, 6.2, 0), (2.5, 0.5, 3), 3.0, 2.7),
            ((87, 9.2, 0), (2.5, 0.5, 3), 3.5, 3.2),
            ((102, 12.2, 0), (2.5, 0.5, 3), 2.5, 2.8),
        ],
        'coins': [
            (4, -2.0, 0), (8, -2.0, 0), (12, -1.0, 0), (17, -0.5, 0),
            (22, 0.5, 0), (27, 1.2, 0), (32, 2.0, 0), (37, 2.5, 0),
            (42, 3.5, 0), (47, 4.0, 0), (52, 5.0, 0), (57, 5.5, 0),
            (62, 6.5, 0), (67, 7.0, 0), (72, 8.0, 0), (77, 8.5, 0),
            (82, 9.5, 0), (87, 10.0, 0), (92, 11.0, 0), (96, 11.5, 0),
            (100, 12.0, 0), (105, 13.0, 0), (32, -0.5, 0), (52, 2.5, 0),
            (62, 4.0, 0), (82, 7.0, 0), (95, 11.0, 0), (102, 12.5, 0),
            (108, 14.0, 0), (110, 16.0, 0),
        ],
        'mobs': [
            (22, 0.0, 0), (42, 3.0, 0), (62, 6.0, 0),
            (82, 9.0, 0), (52, 2.0, 0), (100, 12.0, 0),
        ],
        'hazard': (32, -2.5, 0)
    }
}

# Active Level Entities Containers
active_platforms = []
active_moving_platforms = []
active_coins = []
active_mobs = []

goal = Entity(model='cube', color=color.gold, position=(110, 15.5, 0), scale=(1, 1, 1), collider='box', enabled=False)

player.velocity_y = 0
player.grounded = False

camera.orthographic = True
camera.fov = 10

menu_parent = Entity()
death_parent = Entity()
player.disable()

title_text_death = Text(text='YOU DIED', scale=40, origin=(0, 0), y=0.25, parent=death_parent, color=color.red)
start_button_death = Button(text='Back to menu', scale=(5, 3), y=-3, color=color.green, parent=death_parent)

title_text_menu = Text(text='MY 2.5D PLATFORMER', scale=40, origin=(0, 0), y=0.25, parent=menu_parent,
                       color=color.green)
start_button_menu = Button(text='Start Game', scale=(5, 3), y=-3, color=color.azure, parent=menu_parent)


def load_level(lvl_num):
    global current_level
    current_level = lvl_num
    clear_level()  # Clear any existing entities first

    data = all_levels[current_level]

    for pos, scl in data['platforms']:
        p = Entity(model='cube', color=color.green, position=pos, scale=scl, collider='box')
        active_platforms.append(p)

    for pos, scl, distance, speed in data['moving']:
        mp = Entity(model='cube', color=color.yellow, position=pos, scale=scl, collider='box')
        mp.start_x = pos[0]
        mp.travel_distance = distance
        mp.speed = speed
        active_moving_platforms.append(mp)

    for pos in data['coins']:
        c = Entity(model='sphere', color=color.gold, position=pos, scale=0.5, collider='box')
        active_coins.append(c)

    for pos in data['mobs']:
        m = Entity(model='cube', color=color.white, position=pos, scale=(1, 1.5, 1),texture="images.jpg", collider='box')
        m.hp = 3
        m.velocity_y = 0
        active_mobs.append(m)


def clear_level():
    global active_platforms, active_moving_platforms, active_coins, active_mobs
    destroy_ent_list = active_platforms + active_moving_platforms + active_coins + active_mobs
    for e in destroy_ent_list:
        destroy(e)
    active_platforms.clear()
    active_moving_platforms.clear()
    active_coins.clear()
    active_mobs.clear()

def game_state(state, level=1):
    global game_started, score, player_hp, player_damage, current_level,transitioning,transition_timer
    current_level = level
    player.disable()
    menu_parent.disable()
    goal.disable()
    sword.disable()
    death_parent.disable()
    shop_menu.disable()
    score_text.disable()
    hud_weapon.disable()
    hud_hp.disable()
    hud_level.disable()
    transition_text.disable()
    transition_timer=0
    transitioning = False
    if state == "MENU":
        game_started = False
        camera.parent = scene
        camera.position = (0, 0, -10)
        menu_parent.enable()
        player.position = (0, -2, 0)
        clear_level()
        transitioning = False
        transition_timer=0
    elif state == "PLAY":
        game_started = True
        camera.parent = player
        menu_parent.disable()
        player.enable()
        sword.enable()
        score_text.enable()
        hud_weapon.enable()
        hud_hp.enable()
        hud_level.enable()
        goal.enable()
        transition_text.disable()

        load_level(current_level)
        hud_level.text = f'Level: {current_level}'

        score = 0
        score_text.text = 'Gold: 0'
        player_hp = max_player_hp
        hud_hp.text = f'HP: {player_hp}/{max_player_hp}'

        player_damage = swords['Basic Sword']['damage']
        sword.color = swords['Basic Sword']['color']
        hud_weapon.text = "Weapon: Basic Sword (Dmg: 1)"
        hud_weapon.color = swords['Basic Sword']['color']

        player.position = (0, 0, 0)
        player.velocity_y = 0
    elif state == "DEATH":
        game_started = False
        camera.parent = scene
        camera.position = (0, 0, -10)
        death_parent.enable()
        player.position = (0, -2, 0)
        player.velocity_y = 0
        clear_level()
        transitioning = False
        transition_timer=0

def start_game():
    game_state("PLAY", level=1)

def advance_level():
    global transitioning
    transitioning = False
    if current_level < len(all_levels):
        game_state("PLAY", level=current_level + 1)
        transition_text.disable()
    else:
        game_state('MENU')
        transition_text.disable()

def menu():
    game_state("MENU")


start_button_menu.on_click = start_game
start_button_death.on_click = menu

is_attacking = False
has_hit = False


def reset_sword():
    global is_attacking, player_facing
    sword.position = (1.0 * player_facing, 0, 0)
    is_attacking = False


def swing_sword():
    global is_attacking, has_hit, player_facing
    if is_attacking:
        return

    is_attacking = True
    has_hit = False

    target_x = 1.6 * player_facing
    sword.animate_position((target_x, 0, 0), duration=0.1, curve=curve.linear)
    invoke(reset_sword, delay=0.15)


def update():
    if not game_started:
        return

    global is_attacking, has_hit, score, player_hp, damage_cooldown, player_facing, current_level,transitioning,transition_timer

    if transitioning:
        transition_timer -= time.dt
        if transition_timer <= 0:
            transitioning = False
            if current_level < len(all_levels):
                game_state("PLAY", level=current_level + 1)
                transition_text.disable()
            else:
                game_state('MENU')
                transition_text.disable()
        return
    if damage_cooldown > 0:
        damage_cooldown -= time.dt

    if held_keys['a']:
        player.x -= 5 * time.dt
        player_facing = -1
        if not is_attacking:
            sword.x = -1.0
    if held_keys['d']:
        player.x += 5 * time.dt
        player_facing = 1
        if not is_attacking:
            sword.x = 1.0

    player.velocity_y -= 9.8 * time.dt

    ceil_ray = raycast(origin=player.position, direction=(0, 1, 0), distance=(player.scale_y / 2) + 0.1,
                       ignore=(player,))
    floor_ray = raycast(origin=player.position, direction=(0, -1, 0), distance=(player.scale_y / 2) + 0.1,
                        ignore=(player,))

    # --- Moving Platforms Update & Rider Logic ---
    for mp in active_moving_platforms:
        if mp.enabled:
            old_x = mp.x
            mp.x = mp.start_x + math.sin(time.time() * mp.speed) * mp.travel_distance
            platform_delta_x = mp.x - old_x

            if player.grounded and player.intersects(mp).hit:
                player.x += platform_delta_x

    # --- Multiple Mobs Gravity & AI Tracking Logic ---
    for m in active_mobs:
        if m.enabled:
            m.velocity_y -= 9.8 * time.dt
            mob_floor_ray = raycast(origin=m.position, direction=(0, -1, 0), distance=(m.scale_y / 2) + 0.1,
                                    ignore=(m, player))

            if mob_floor_ray.hit and m.velocity_y <= 0:
                m.velocity_y = 0
                m.y = mob_floor_ray.world_point.y + (m.scale_y / 2)
            else:
                m.y += m.velocity_y * time.dt

            dist = abs(m.x - player.x)
            if 1.0 < dist < 5.0:
                if m.x < player.x:
                    m.x += 2.5 * time.dt
                elif m.x > player.x:
                    m.x -= 2.5 * time.dt

            if player.intersects(m).hit and damage_cooldown <= 0:
                player_hp -= 1
                damage_cooldown = 1.0
                hud_hp.text = f'HP: {player_hp}/{max_player_hp}'
                player.x -= 0.5 * player_facing
                if player_hp <= 0:
                    game_state("DEATH")

            if is_attacking and not has_hit and sword.intersects(m).hit:
                if m.hp > 0:
                    has_hit = True
                    m.hp -= player_damage
                    m.x += 0.8 * player_facing

                    if m.hp <= 0:
                        m.disable()
                        score += 5
                        score_text.text = f'Gold: {score}'

    for c in active_coins:
        if c.enabled and player.intersects(c).hit:
            c.disable()
            score += 1
            score_text.text = f'Gold: {score}'


    if floor_ray.hit and player.velocity_y <= 0:
        player.velocity_y = 0
        player.y = floor_ray.world_point.y + (player.scale_y / 2)
        player.grounded = True
    elif player.y<-5:
        game_state("DEATH")
    elif player.intersects(goal).hit and not transitioning:
        transitioning = True
        goal.disable()
        clear_level()

        if current_level < len(all_levels):
            transition_text.text = f"Moving to Level {current_level + 1}..."
        else:
            transition_text.text = "You Win!"

        transition_text.enable()
        player.disable()
        transition_timer = 3.0  # Set a rock-solid 3-second delay
        return
    elif ceil_ray.hit and player.velocity_y >= 0:
        player.velocity_y = 0
        player.y = ceil_ray.world_point.y - (player.scale_y / 2)
    elif player.intersects(goal).hit:
        if current_level < len(all_levels):
            game_state("PLAY", level=current_level + 1)
        else:
            game_state('MENU')
        return
    else:
        if not (player.velocity_y > 0 and ceil_ray.hit):
            player.grounded = False
            player.y += player.velocity_y * time.dt


# Shop UI container
shop_menu = Entity(parent=camera.ui, enabled=False)
shop_bg = Entity(parent=shop_menu, model='quad', scale=(0.7, 0.7), color=color.black66)
shop_title = Text(text="WEAPON SHOP (Press 'B' to Close)", parent=shop_menu, position=(-0.3, 0.3), scale=1.2)
shop_message = Text(text="", parent=shop_menu, position=(-0.25, -0.2), scale=1.2, color=color.red)


def show_shop_message(msg_text, msg_color=color.red):
    shop_message.text = msg_text
    shop_message.color = msg_color
    shop_message.color = color.rgba(msg_color.r, msg_color.g, msg_color.b, 1)
    invoke(
        shop_message.animate_color,
        color.rgba(msg_color.r, msg_color.g, msg_color.b, 0),
        duration=1.0,
        delay=1.5
    )


def buy_iron_sword():
    global score, player_damage
    if not swords['Iron Sword']['unlocked'] and score >= swords['Iron Sword']['price']:
        score -= swords['Iron Sword']['price']
        swords['Iron Sword']['unlocked'] = True
        player_damage = swords['Iron Sword']['damage']
        sword.color = swords['Iron Sword']['color']
        score_text.text = f'Gold: {score}'
        hud_weapon.text = "Weapon: Iron Sword (Dmg: 2)"
        hud_weapon.color = swords['Iron Sword']['color']
        show_shop_message("Purchased & Equipped Iron Sword!", color.green)
    elif swords['Iron Sword']['unlocked']:
        player_damage = swords['Iron Sword']['damage']
        sword.color = swords['Iron Sword']['color']
        hud_weapon.text = "Weapon: Iron Sword (Dmg: 2)"
        hud_weapon.color = swords['Iron Sword']['color']
        show_shop_message("Equipped Iron Sword!", color.cyan)
    else:
        show_shop_message("Not enough gold!", color.red)


def buy_flame_sword():
    global score, player_damage
    if not swords['Flame Sword']['unlocked'] and score >= swords['Flame Sword']['price']:
        score -= swords['Flame Sword']['price']
        swords['Flame Sword']['unlocked'] = True
        player_damage = swords['Flame Sword']['damage']
        sword.color = swords['Flame Sword']['color']
        score_text.text = f'Gold: {score}'
        hud_weapon.text = "Weapon: Flame Sword (Dmg: 4)"
        hud_weapon.color = swords['Flame Sword']['color']
        show_shop_message("Purchased & Equipped Flame Sword!", color.green)
    elif swords['Flame Sword']['unlocked']:
        player_damage = swords['Flame Sword']['damage']
        sword.color = swords['Flame Sword']['color']
        hud_weapon.text = "Weapon: Flame Sword (Dmg: 4)"
        hud_weapon.color = swords['Flame Sword']['color']
        show_shop_message("Equipped Flame Sword!", color.cyan)
    else:
        show_shop_message("Not enough gold!", color.red)


iron_btn = Button(text="Iron Sword (10 Gold) - Dmg: 2", parent=shop_menu, position=(0, 0.1), scale=(0.5, 0.08),
                  on_click=buy_iron_sword)
flame_btn = Button(text="Flame Sword (25 Gold) - Dmg: 4", parent=shop_menu, position=(0, -0.05), scale=(0.5, 0.08),
                   on_click=buy_flame_sword)


def input(key):
    if not game_started:
        return
    if key == 'space' and player.velocity_y == 0:
        player.velocity_y += 500 * time.dt
        player.grounded = False
        update()
    if key == "f":
        swing_sword()
    if key == 'b':
        shop_menu.enabled = not shop_menu.enabled
        if shop_menu.enabled:
            shop_message.text = ""


game_state("MENU")
app.run()