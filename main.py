from ursina import *

app = Ursina()  # initializes the window gng

game_started = False
player = Entity(model="cube", color=color.cyan, scale=(1, 1, 1), collider="box")
score = 0

# Player combat stats & Health
player_damage = 1
player_hp = 3
max_player_hp = 3
damage_cooldown = 0  # Prevents taking damage every single frame
player_facing = 1  # 1 for right, -1 for left

# Sword Data: catalog of available weapons
swords = {
    'Basic Sword': {'damage': 1, 'price': 0, 'unlocked': True, 'color': color.light_gray},
    'Iron Sword': {'damage': 2, 'price': 10, 'unlocked': False, 'color': color.cyan},
    'Flame Sword': {'damage': 4, 'price': 25, 'unlocked': False, 'color': color.orange}
}

# A simple sword attached to the player
sword = Entity(
    parent=player,
    model='cube',
    color=color.light_gray,
    scale=(0.8, 0.15, 0.15),
    position=(1.0, 0, 0),
    collider='box'
)

# --- On-Screen HUD Elements ---
score_text = Text(
    text='Gold: 0',
    position=(-0.65, 0.45),
    scale=1.5,
    color=color.yellow,
    parent=camera.ui
)
score_text.disable()

hud_weapon = Text(
    text='Weapon: Basic Sword (Dmg: 1)',
    position=(-0.65, 0.38),
    scale=1.2,
    color=color.light_gray,
    parent=camera.ui
)
hud_weapon.disable()

hud_hp = Text(
    text='HP: 3/3',
    position=(-0.65, 0.31),
    scale=1.2,
    color=color.red,
    parent=camera.ui
)
hud_hp.disable()

# Massive Expanded Level Platforms Layout
level_1_data = [
    # Starting area
    ((0, -3, 0), (12, 0.5, 5)),
    # Stepping stones & bridges
    ((10, -1.0, 0), (5, 0.5, 3)),
    ((17, 1.0, 0), (5, 0.5, 3)),
    ((24, 0.0, 0), (5, 0.5, 3)),
    # Climbing upward section
    ((31, 2.5, 0), (5, 0.5, 3)),
    ((38, 4.5, 0), (5, 0.5, 3)),
    ((45, 6.5, 0), (5, 0.5, 3)),
    # Upper return path / floating islands
    ((38, 8.5, 0), (5, 0.5, 3)),
    ((28, 10.5, 0), (5, 0.5, 3)),
    ((18, 11.5, 0), (5, 0.5, 3)),
    # Final stretch leading to goal
    ((25, 13.5, 0), (4, 0.5, 3)),
    ((34, 15.5, 0), (6, 0.5, 3)),
]

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

# Spawning Lots of Coins
coin_data = [
    (10, 0.5, 0),
    (17, 2.5, 0),
    (24, 1.5, 0),
    (31, 4.0, 0),
    (38, 6.0, 0),
    (45, 8.0, 0),
    (38, 10.0, 0),
    (28, 12.0, 0),
    (18, 13.0, 0),
    (25, 15.0, 0),
    (32, 17.0, 0),
]
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

# Spawning Multiple Mobs Across the Map
mob_data = [
    (17, 2.5, 0),
    (31, 4.0, 0),
    (45, 8.0, 0),
    (28, 12.0, 0),
    (18, 13.0, 0)
]
mobs = []
for pos in mob_data:
    m = Entity(
        model='cube',
        color=color.red,
        position=pos,
        scale=(1, 1.5, 1),
        collider='box'
    )
    m.hp = 3
    m.velocity_y = 0
    mobs.append(m)
    m.disable()

# Creating a death system hazard block
hazard = Entity(
    model='cube',
    color=color.red,
    position=(24, 1.5, 0),
    scale=(1.5, 0.5, 1),
    collider='box'
)
hazard.disable()

# Goal point for level 1
goal = Entity(
    model='cube',
    color=color.gold,
    position=(34, 17.5, 0),
    scale=(1, 1, 1),
    collider='box'
)
goal.disable()

player.velocity_y = 0
player.grounded = False

# Camera setup
camera.orthographic = True
camera.fov = 10

# Setting game states and menu screen
menu_parent = Entity()
death_parent = Entity()
player.disable()
for p in platforms:
    p.disable()

# Death screen UI
title_text_death = Text(
    text='YOU DIED',
    scale=40,
    origin=(0, 0),
    y=0.25,
    parent=death_parent,
    color=color.red
)
start_button_death = Button(
    text='Back to menu',
    scale=(5, 3),
    y=-3,
    color=color.green,
    parent=death_parent
)

# Menu UI
title_text_menu = Text(
    text='MY 2.5D PLATFORMER',
    scale=40,
    origin=(0, 0),
    y=0.25,
    parent=menu_parent,
    color=color.green
)
start_button_menu = Button(
    text='Start Game',
    scale=(5, 3),
    y=-3,
    color=color.azure,
    parent=menu_parent
)


def game_state(state):
    global game_started, score, player_hp, sword, swords
    player.disable()
    menu_parent.disable()
    goal.disable()
    sword.disable()
    hazard.disable()
    death_parent.disable()
    shop_menu.disable()
    score_text.disable()
    hud_weapon.disable()
    hud_hp.disable()

    for p in platforms:
        p.disable()
    for c in coins:
        c.disable()
    for m in mobs:
        m.disable()

    if state == "MENU":
        game_started = False
        camera.parent = scene
        camera.position = (0, 0, -10)
        menu_parent.enable()
        player.position = (0, -2, 0)
        global player_damage
        player_damage = swords['Basic Sword']['damage']
        sword.color = swords['Basic Sword']['color']
        hud_weapon.text = "Weapon: Basic Sword (Dmg: 1)"
        hud_weapon.color = swords['Basic Sword']['color']
    elif state == "PLAY":
        game_started = True
        camera.parent = player
        menu_parent.disable()
        player.enable()
        sword.enable()
        score_text.enable()
        hud_weapon.enable()
        hud_hp.enable()
        hazard.enable()

        for p in platforms:
            p.enable()
        for c in coins:
            c.enable()
        for m in mobs:
            m.enable()
            m.hp = 3
            m.velocity_y = 0

        goal.enable()
        score = 0
        score_text.text = 'Gold: 0'
        player_hp = max_player_hp
        hud_hp.text = f'HP: {player_hp}/{max_player_hp}'
        player.position = (0, 1, 0)
        player.velocity_y = 0

        # Reset mobs positions matching mob_data
        for i, m in enumerate(mobs):
            m.position = mob_data[i]
            m.hp = 3
            m.velocity_y = 0

    elif state == "DEATH":
        game_started = False
        camera.parent = scene
        camera.position = (0, 0, -10)
        death_parent.enable()
        player.position = (0, -2, 0)
        player.velocity_y = 0


def start_game():
    game_state("PLAY")


def menu():
    game_state("MENU")


start_button_menu.on_click = start_game
start_button_death.on_click = menu

# Sword swinging animation (direction-aware):
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


# Main game loop
def update():
    if not game_started:
        return

    global is_attacking, has_hit, score, player_hp, damage_cooldown, player_facing

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

    # --- Multiple Mobs Gravity & AI Tracking Logic ---
    for m in mobs:
        if m.enabled:
            m.velocity_y -= 9.8 * time.dt
            # ignore=(m, player) ensures the mob's floor ray never treats the player as a platform!
            mob_floor_ray = raycast(origin=m.position, direction=(0, -1, 0), distance=(m.scale_y / 2) + 0.1,
                                    ignore=(m, player))

            if mob_floor_ray.hit and m.velocity_y <= 0:
                m.velocity_y = 0
                m.y = mob_floor_ray.world_point.y + (m.scale_y / 2)
            else:
                m.y += m.velocity_y * time.dt

            # Chase player if within detection radius, keeping safe stopping distance
            dist = distance(m, player)
            if 1.0 < dist < 5.0:
                if m.x < player.x:
                    m.x += 2.5 * time.dt
                elif m.x > player.x:
                    m.x -= 2.5 * time.dt

            # Deal damage to player on touch (with cooldown)
            if player.intersects(m).hit and damage_cooldown <= 0:
                player_hp -= 1
                damage_cooldown = 1.0
                hud_hp.text = f'HP: {player_hp}/{max_player_hp}'
                player.x -= 0.5 * player_facing
                if player_hp <= 0:
                    game_state("DEATH")

            # Player Combat check against each mob
            if is_attacking and not has_hit and sword.intersects(m).hit:
                if m.hp > 0:
                    has_hit = True
                    m.hp -= player_damage
                    m.x += 0.8 * player_facing

                    if m.hp <= 0:
                        m.disable()
                        score += 5
                        score_text.text = f'Gold: {score}'

    for c in coins:
        if c.enabled and player.intersects(c).hit:
            c.disable()
            score += 1
            score_text.text = f'Gold: {score}'

    if (player.enabled and player.intersects(hazard).hit) or player.y < -5:
        game_state("DEATH")
    elif floor_ray.hit and player.velocity_y <= 0:
        player.velocity_y = 0
        player.y = floor_ray.world_point.y + (player.scale_y / 2)
        player.grounded = True
    elif ceil_ray.hit and player.velocity_y >= 0:
        player.velocity_y = 0
        player.y = ceil_ray.world_point.y - (player.scale_y / 2)
    elif player.intersects(goal).hit:
        game_state('MENU')
        return
    else:
        if not (player.velocity_y > 0 and ceil_ray.hit):
            player.grounded = False
            player.y += player.velocity_y * time.dt


# Shop UI container (hidden by default)
shop_menu = Entity(parent=camera.ui, enabled=False)

shop_bg = Entity(parent=shop_menu, model='quad', scale=(0.7, 0.7), color=color.black66)
shop_title = Text(text="WEAPON SHOP (Press 'B' to Close)", parent=shop_menu, position=(-0.3, 0.3), scale=1.2)

shop_message = Text(
    text="",
    parent=shop_menu,
    position=(-0.25, -0.2),
    scale=1.2,
    color=color.red
)


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


# Shop Buttons
iron_btn = Button(
    text="Iron Sword (10 Gold) - Dmg: 2",
    parent=shop_menu,
    position=(0, 0.1),
    scale=(0.5, 0.08),
    on_click=buy_iron_sword
)

flame_btn = Button(
    text="Flame Sword (25 Gold) - Dmg: 4",
    parent=shop_menu,
    position=(0, -0.05),
    scale=(0.5, 0.08),
    on_click=buy_flame_sword
)


def input(key):
    if not game_started:
        return
    if key == 'space' and player.velocity_y == 0:
        player.velocity_y += 500 * time.dt
        player.grounded = False
        update()
    if key == "m":
        swing_sword()
    if key == 'b':
        shop_menu.enabled = not shop_menu.enabled
        if shop_menu.enabled:
            shop_message.text = ""


game_state("MENU")
app.run()