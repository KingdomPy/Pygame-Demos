import math
from src import contentLoader
from src.entities import baseEntity

projectile_data = contentLoader.load_projectile_data()


class Player(baseEntity.Entity):
    def __init__(self, pointer):
        super().__init__(pointer)

        # Default Display
        # self.mapping = ((1.5, 0), (1, 5 * math.pi / 7), (1, - 5 * math.pi / 7))  # (radius, angle in radians)
        self.mapping = (
            (1, 0.36),
            (1.8, 0.19),
            (1.9, 0.28),
            (1.2, 1.67),
            (1.6, 2.28),
            (1.9, 3.06),
            (1.8, 3.01),
            (1.6, 2.99),
            (1.6, -2.99),
            (1.8, -3.01),
            (1.9, -3.06),
            (1.6, -2.28),
            (1.2, -1.67),
            (1.9, -0.28),
            (1.8, -0.19),
            (1, -0.36))
        self.size = 55  # Scale factor for mapping
        self.colour = (0, 0, 0)
        self.name = "Player"
        self.sprite_type = "player"

        # Animations
        self.shape = []  # List of xy coordinates for each vertex of the entity
        self.current_size = self.size
        self.set_size(self.size)
        self.current_colour = self.colour

        # Stats
        self.movement_speed = 768  # Float
        self.max_health = 100  # Integer
        self.health = 100  # Integer
        self.max_energy = 3  # Integer
        self.energy = 3  # Integer
        self.level = 1
        self.experience = 0
        self.ship_type = "Recruit"  # For Warrior, Scribe, Wanderer and Recruit (tutorial)
        self.emblems = [None, None]  # Permanent stat boosters that scale with your level for STR, INT and AGI

        # Core Stats
        self.strength = 0  # Integer
        self.intelligence = 0  # Integer
        self.agility = 0  # Integer

        # Advanced Stats
        self.attack = 0  # Integer
        self.power = 0  # Integer
        self.critical_rate = 0 # 0 - 1 float
        self.defence = 0 # 0 - 1 float

        # Specialist Stats
        self.cooldown_reduction = 0  # 0 - 1 float
        self.energy_haste = 0 # 0 - 1 float
        self.energy_recharge_time = 60  # Seconds

        # Data
        self.player_data = []  # Saved data
        self.items = []
        self.equipped_items = ["test"]  # Up to 4 equipped items
        self.attack_type = None # A string with the values of Surge, Spray and Hyper
        self.technique_deck = []  # A List of techniques and talents (talent combination like Grand Fantasia?)
        self.equipped_techniques = []  # A Maximum of 8 equipped techniques
        self.equipped_talents = []  # Using talents grants proficiency in them over time granting bonus effects
        self.talent_points = 0  # Determines how many talents you can equip, talents have different weightings
        self.command_menu = ("Attack", "Techniques", "Items", "Gears")  # Options displayed in the command menu
        self.command_menu_selected = 0  # Selected slot from 1 to 4
        self.command_menu_page = 0  # Which page is the menu on
        self.money = 0  # Integer

        # Commands
        self.cooldowns = []  # A list of of lists that in the format (current time, time when cooled down)

    def calculate_stats(self):
        #  Talent Points
        self.talent_points = 5 + self.level

        # Battle Style
        if self.ship_type == "Warrior":
            self.strength = self.level * 4
            self.agility = self.level * 2
            self.intelligence = self.level

        elif self.ship_type == "Scribe":
            self.intelligence = self.level * 4
            self.agility = self.level * 2
            self.strength = self.level

        elif self.ship_type == "Wanderer":
            self.agility = self.level * 4
            self.strength = self.level * 2
            self.intelligence = self.level

        # Emblems
        stat_boost = self.emblems[0]
        if stat_boost == "STR":
            self.strength += self.level
        if stat_boost == "INT":
            self.intelligence += self.level
        if stat_boost == "AGI":
            self.agility += self.level

        stat_boost = self.emblems[1]
        if stat_boost == "STR":
            self.strength += self.level // 2
        if stat_boost == "INT":
            self.intelligence += self.level // 2
        if stat_boost == "AGI":
            self.agility += self.level // 2

        # Early game bonuses
        if self.level >= 2:
            self.intelligence += 10

        if self.level >= 4:
            self.strength += 10
            self.agility += 10

        if self.level >= 7:
            self.agility += 10

        if self.level >= 8:
            self.strength += 20

        if self.level >= 11:
            self.strength += 20
            self.agility += 20

        if self.level >= 15:
            self.intelligence += 20

        # Later bonuses
        if self.level >= 20:
            self.strength += 10

        if self.level >= 25:
            self.agility += 10

        if self.level >= 30:
            self.strength += 10

        if self.level >= 35:
            self.intelligence += 10

        if self.level >= 40:
            self.agility += 10

        if self.level >= 45:
            self.agility += 10

        if self.level >= 50:
            self.strength += 10

        if self.level >= 55:
            self.intelligence += 20

        if self.level >= 60:
            self.strength += 10
            self.intelligence += 20
            self.agility += 20

        #  Advanced Stats
        self.attack = self.strength * 0.2 + self.agility * 0.1
        self.power = self.intelligence * 0.3 + self.agility * 0.1
        self.critical_rate = self.agility * 0.2
        self.defence = self.strength * 0.1
        self.max_health = int(self.strength * 0.5 + self.intelligence * 0.1 + self.agility * 0.1)
        self.max_energy = int(self.intelligence * 0.1)
        self.defence = self.strength * 0.1
        self.cooldown_reduction = 0
        self.energy_haste = 0

    def set_player_data(self, data):
        self.player_data = data
        self.experience = data[1]
        self.level = math.floor(math.sqrt((max(self.experience, 370)-300)/70)-1)
        self.money = data[2]

        if data[3] == 0:
            self.ship_type = "Warrior"
        elif data[3] == 1:
            self.ship_type = "Scribe"
        elif data[3] == 2:
            self.ship_type = "Wanderer"

        for i in range(2):
            if data[4][i] == 0:
                self.emblems[i] == "STR"
            elif data[4][i] == 1:
                self.emblems[i] == "INT"
            elif data[4][i] == 2:
                self.emblems[i] == "AGI"

        self.items = data[5]
        self.technique_deck = data[7]["technique deck"]
        self.equipped_talents = data[7]["equipped talents"]
        self.equipped_techniques = data[7]["equipped techniques"]
        self.calculate_stats()

        self.health = self.max_health
        self.energy = self.max_energy

        if "Surge" in self.equipped_talents:
            self.attack_type = "Surge"
        elif "Spray" in self.equipped_talents:
            self.attack_type = "Spray"
        elif "Hyper" in self.equipped_talents:
            self.attack_type = "Hyper"

    def left_mouse_pressed(self):
        selected_option = self.command_menu[self.command_menu_selected]
        if self.command_menu_page == 0:
            if selected_option == "Attack":
                if self.attack_type is not None:
                    return self.attack_type
            else:
                if selected_option == "Techniques" and self.equipped_techniques != []:
                    self.command_menu = self.equipped_techniques
                    self.command_menu_page += 1
                    self.command_menu_selected = 0
                    return "page up"

                elif selected_option == "Items" and self.equipped_items != []:
                    self.command_menu = self.equipped_items
                    self.command_menu_page += 1
                    self.command_menu_selected = 0
                    return "page up"
        elif self.command_menu_page == 1:
            self.activate_command(selected_option)
        return 1

    def right_mouse_pressed(self):
        if self.command_menu_page > 0:
            self.command_menu_page -=1
            self.command_menu_selected = 0
            if self.command_menu_page == 0:
                self.command_menu = ("Attack", "Techniques", "Items", "Gears")
            return "page down"
        return 1

    def command_menu_scroll(self, direction):
        if direction == "up":
            direction = 1
        elif direction == "down":
            direction = -1
        if self.command_menu_page == 0:
            self.command_menu_selected -= direction
            self.command_menu_selected %= 4
            selected = self.command_menu[self.command_menu_selected]
            if selected == "Techniques":
                if not self.equipped_techniques:
                    self.command_menu_scroll(direction)
            elif selected == "Items":
                if not self.equipped_items:
                    self.command_menu_scroll(direction)
        else:
            self.command_menu_selected -= direction
            if self.command_menu_selected == len(self.command_menu):
                self.command_menu_selected = 0
            elif self.command_menu_selected < 0:
                self.command_menu_selected = len(self.command_menu) - 1
        return self.command_menu_selected

    def activate_command(self, command):
        if command == "Barrier":
            pass
        elif command == "Combo":
            pass
        elif command == "Missile":
            pass
        elif command == "Repair":
            if self.energy > 0:
                self.health = self.max_health
                self.energy = 0
        return 1

    def update(self, dt, touching_mouse = False):
        if self.health <= 0:
            return 0
        if self.energy <= 0:
            self.energy -= 1 / self.energy_recharge_time * self.max_energy * dt
            if self.energy <= -1 * self.max_energy:
                self.energy = self.max_energy
        return 1



