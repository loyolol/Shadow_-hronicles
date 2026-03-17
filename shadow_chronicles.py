import random
from time import sleep
import os
import json
from datetime import datetime

class Character:
    def __init__(self, name, hp, dmg, deff, exp_value=0, level=1):
        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.dmg = dmg
        self.deff = deff
        self.exp_value = exp_value
        self.level = level
        self.exp = 0
        self.gold = 0
        self.inventory = []
    
    def is_alive(self):
        return self.hp > 0
    
    def attack(self, target):
        print(f"\n{self.name} атакует!")
        print("Бросок кубика d20...")
        sleep(1)
        d20_attack = random.randint(1, 20)
        print(f"Выпало: {d20_attack}")
        
        if d20_attack == 1:
            print("💥 КРИТИЧЕСКАЯ НЕУДАЧА!")
            print(f"{self.name} споткнулся и упал, ударившись головой!")
            damage = random.randint(1, 15)
            self.hp -= damage
            print(f"{self.name} нанес себе {damage} урона! Осталось HP: {self.hp}")
            
        elif d20_attack == 20:
            print("⚡ КРИТИЧЕСКАЯ УДАЧА!")
            print(f"{self.name} наносит сокрушительный удар!")
            damage = random.randint(self.dmg // 2, self.dmg) * 2
            target.hp -= damage
            print(f"Нанесено {damage} урона! У {target.name} осталось HP: {target.hp}")
            
        elif d20_attack > target.deff:
            damage = random.randint(1, self.dmg)
            target.hp -= damage
            print(f"Попадание! Нанесено {damage} урона")
            print(f"У {target.name} осталось HP: {target.hp}")
        else:
            print("Промах! Атака не достигла цели")
    
    def heal(self, amount):
        self.hp = min(self.hp + amount, self.max_hp)
        print(f"{self.name} восстановил {amount} HP! Текущее HP: {self.hp}")
    
    def gain_exp(self, amount):
        self.exp += amount
        print(f"✨ Получено {amount} опыта!")
        while self.exp >= self.level * 100:
            self.level_up()
    
    def level_up(self):
        self.level += 1
        self.exp -= (self.level - 1) * 100
        self.max_hp += 20
        self.hp = self.max_hp
        self.dmg += 5
        self.deff += 2
        print(f"🎉 УРОВЕНЬ ПОВЫШЕН! Теперь уровень {self.level}!")
        print(f"Характеристики увеличены: HP+20, Урон+5, Защита+2")
    
    def add_item(self, item):
        self.inventory.append(item)
        print(f"📦 Получен предмет: {item['name']}")
    
    def __str__(self):
        return f"{self.name} (Ур.{self.level}): HP {self.hp}/{self.max_hp} | Урон: {self.dmg} | Защита: {self.deff}"


class Enemy(Character):
    def __init__(self, name, hp, dmg, deff, exp_value, enemy_type, gold_drop=0):
        super().__init__(name, hp, dmg, deff, exp_value)
        self.enemy_type = enemy_type
        self.gold_drop = gold_drop
        self.loot_table = []
    
    def special_ability(self, target):
        if self.enemy_type == "goblin":
            if random.random() < 0.3:
                print(f"👺 {self.name} использует гоблинскую хитрость и уворачивается!")
                return True
        elif self.enemy_type == "orc":
            if random.random() < 0.2:
                print(f"👹 {self.name} впадает в ярость и наносит двойной урон!")
                self.dmg *= 2
                self.attack(target)
                self.dmg //= 2
                return True
        elif self.enemy_type == "skeleton":
            if self.hp < self.max_hp * 0.3:
                print(f"💀 {self.name} восстанавливается из костей!")
                self.hp += self.max_hp * 0.2
                print(f"HP восстановлено до {int(self.hp)}")
                return True
        elif self.enemy_type == "vampire":
            damage = random.randint(5, 15)
            target.hp -= damage
            self.hp += damage
            print(f"🧛 {self.name} высасывает жизнь! Нанесено {damage} урона, {self.name} восстановил {damage} HP")
            return True
        elif self.enemy_type == "dragon":
            if random.random() < 0.4:
                print(f"🐉 {self.name} ДЫШИТ ОГНЕМ!")
                damage = random.randint(20, 40)
                target.hp -= damage
                print(f"Огненное дыхание наносит {damage} урона!")
                return True
        return False
    
    def generate_loot(self):
        loot = []
        if self.gold_drop > 0:
            loot.append({"type": "gold", "amount": self.gold_drop})
        
        if self.enemy_type == "dragon":
            if random.random() < 0.8:
                loot.append({"type": "item", "name": "Драконья чешуя", "value": 100})
        elif self.enemy_type == "vampire":
            if random.random() < 0.5:
                loot.append({"type": "item", "name": "Клык вампира", "value": 50})
        elif random.random() < 0.3:
            loot.append({"type": "item", "name": "Зелье лечения", "value": 30, "heal": 30})
        
        return loot


class Shop:
    def __init__(self):
        self.items = [
            {"name": "Малое зелье лечения", "price": 20, "heal": 20, "type": "potion"},
            {"name": "Большое зелье лечения", "price": 40, "heal": 50, "type": "potion"},
            {"name": "Эликсир силы", "price": 50, "dmg_boost": 5, "type": "buff"},
            {"name": "Эликсир защиты", "price": 50, "deff_boost": 3, "type": "buff"},
            {"name": "Меч +1", "price": 100, "dmg_boost": 10, "type": "weapon", "permanent": True},
            {"name": "Щит +1", "price": 80, "deff_boost": 5, "type": "armor", "permanent": True},
        ]
    
    def show_items(self, player):
        print("\n" + "=" * 50)
        print(" " * 20 + "ЛАВКА")
        print("=" * 50)
        print(f"Ваши монеты: {player.gold} 🪙")
        print("-" * 50)
        
        for i, item in enumerate(self.items, 1):
            print(f"{i}. {item['name']} - {item['price']} 🪙")
            if "heal" in item:
                print(f"   Восстанавливает {item['heal']} HP")
            elif "dmg_boost" in item and item.get("permanent"):
                print(f"   Увеличивает урон на {item['dmg_boost']} (навсегда)")
            elif "deff_boost" in item and item.get("permanent"):
                print(f"   Увеличивает защиту на {item['deff_boost']} (навсегда)")
            elif "dmg_boost" in item:
                print(f"   Увеличивает урон на {item['dmg_boost']} (на 1 бой)")
        
        print("0. Выйти из лавки")
        print("-" * 50)
    
    def buy(self, player, choice):
        if choice < 1 or choice > len(self.items):
            return False
        
        item = self.items[choice - 1]
        
        if player.gold < item["price"]:
            print("❌ Недостаточно монет!")
            return False
        
        player.gold -= item["price"]
        
        if item["type"] == "potion":
            player.add_item(item)
            print(f"✅ Приобретено: {item['name']}")
        elif item["type"] == "buff":
            print(f"✅ Использован: {item['name']}")
            if "dmg_boost" in item:
                player.dmg += item["dmg_boost"]
                print(f"Урон увеличен на {item['dmg_boost']} (до конца боя)")
            if "deff_boost" in item:
                player.deff += item["deff_boost"]
                print(f"Защита увеличена на {item['deff_boost']} (до конца боя)")
        elif item.get("permanent"):
            print(f"✅ Экипировано: {item['name']}")
            if "dmg_boost" in item:
                player.dmg += item["dmg_boost"]
            if "deff_boost" in item:
                player.deff += item["deff_boost"]
        
        return True


class Game:
    def __init__(self):
        self.player = None
        self.score = 0
        self.enemies_killed = 0
        self.round_count = 0
        self.difficulty = "normal"
        self.boss_defeated = False
        self.shop = Shop()
        
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def show_title(self):
        self.clear_screen()
        print("=" * 60)
        print(" " * 15 + "CONSOLE TEXT RPG")
        print(" " * 10 + "⚔️ ПОЛНАЯ ВЕРСИЯ ⚔️")
        print("=" * 60)
        print()
    
    def create_player(self):
        self.show_title()
        print("СОЗДАНИЕ ПЕРСОНАЖА")
        print("-" * 40)
        
        name = input("Введите имя вашего героя: ").strip()
        if not name:
            name = "Безымянный герой"
        
        print("\nВыберите класс:")
        print("1. Воин (HP: 120, Урон: 25, Защита: 14)")
        print("2. Разбойник (HP: 90, Урон: 35, Защита: 10)")
        print("3. Маг (HP: 70, Урон: 40, Защита: 8)")
        print("4. Паладин (HP: 110, Урон: 20, Защита: 18)")
        
        choice = input("Ваш выбор (1-4): ").strip()
        
        if choice == "2":
            self.player = Character(name, 90, 35, 10)
            print("Вы выбрали класс Разбойник!")
        elif choice == "3":
            self.player = Character(name, 70, 40, 8)
            print("Вы выбрали класс Маг!")
        elif choice == "4":
            self.player = Character(name, 110, 20, 18)
            print("Вы выбрали класс Паладин!")
        else:
            self.player = Character(name, 120, 25, 14)
            print("Вы выбрали класс Воин!")
        
        self.player.gold = 50
        self.player.add_item({"name": "Малое зелье лечения", "heal": 20, "type": "potion"})
        self.player.add_item({"name": "Малое зелье лечения", "heal": 20, "type": "potion"})
        
        print(f"\nДобро пожаловать, {self.player.name}!")
        print(f"Стартовые монеты: {self.player.gold} 🪙")
        print(f"Стартовые предметы: 2x Малое зелье лечения")
        input("\nНажмите Enter, чтобы продолжить...")
    
    def choose_difficulty(self):
        self.clear_screen()
        print("ВЫБОР СЛОЖНОСТИ")
        print("-" * 40)
        print("1. Легко (враги слабее, больше шанс критической удачи)")
        print("2. Нормально (стандартные параметры)")
        print("3. Сложно (враги сильнее, больше шанс критической неудачи)")
        print("4. Легендарно (враги очень сильны, но награды выше)")
        
        choice = input("Ваш выбор (1-4): ").strip()
        
        if choice == "1":
            self.difficulty = "easy"
            print("Выбрана сложность: ЛЕГКО")
        elif choice == "3":
            self.difficulty = "hard"
            print("Выбрана сложность: СЛОЖНО")
        elif choice == "4":
            self.difficulty = "legendary"
            print("Выбрана сложность: ЛЕГЕНДАРНО")
        else:
            self.difficulty = "normal"
            print("Выбрана сложность: НОРМАЛЬНО")
        
        input("\nНажмите Enter, чтобы продолжить...")
    
    def generate_enemy(self, force_boss=False):
        if force_boss:
            enemies = [
                {"name": "Вампир-лорд", "hp": 200, "dmg": 35, "deff": 16, "exp": 100, "type": "vampire", "gold": 150},
                {"name": "Дракон", "hp": 300, "dmg": 40, "deff": 18, "exp": 150, "type": "dragon", "gold": 300},
            ]
        else:
            enemies = [
                {"name": "Гоблин", "hp": 40, "dmg": 15, "deff": 8, "exp": 10, "type": "goblin", "gold": 5},
                {"name": "Гоблин-воин", "hp": 60, "dmg": 20, "deff": 10, "exp": 15, "type": "goblin", "gold": 8},
                {"name": "Орк", "hp": 80, "dmg": 25, "deff": 12, "exp": 20, "type": "orc", "gold": 12},
                {"name": "Орк-берсерк", "hp": 100, "dmg": 30, "deff": 10, "exp": 25, "type": "orc", "gold": 15},
                {"name": "Скелет", "hp": 50, "dmg": 18, "deff": 12, "exp": 12, "type": "skeleton", "gold": 6},
                {"name": "Скелет-воин", "hp": 70, "dmg": 22, "deff": 14, "exp": 18, "type": "skeleton", "gold": 10},
                {"name": "Вампир", "hp": 120, "dmg": 28, "deff": 14, "exp": 40, "type": "vampire", "gold": 30},
            ]
        
        enemy_data = random.choice(enemies)
        
        if self.difficulty == "easy":
            enemy_data["hp"] = int(enemy_data["hp"] * 0.8)
            enemy_data["dmg"] = int(enemy_data["dmg"] * 0.8)
        elif self.difficulty == "hard":
            enemy_data["hp"] = int(enemy_data["hp"] * 1.3)
            enemy_data["dmg"] = int(enemy_data["dmg"] * 1.2)
            enemy_data["deff"] += 2
        elif self.difficulty == "legendary":
            enemy_data["hp"] = int(enemy_data["hp"] * 1.8)
            enemy_data["dmg"] = int(enemy_data["dmg"] * 1.5)
            enemy_data["deff"] += 4
            enemy_data["exp"] = int(enemy_data["exp"] * 2)
            enemy_data["gold"] = int(enemy_data["gold"] * 2.5)
        
        return Enemy(
            enemy_data["name"],
            enemy_data["hp"],
            enemy_data["dmg"],
            enemy_data["deff"],
            enemy_data["exp"],
            enemy_data["type"],
            enemy_data["gold"]
        )
    
    def show_stats(self, enemy):
        self.clear_screen()
        print("=" * 60)
        print(f"РАУНД {self.round_count}")
        print("=" * 60)
        print(f"\n{self.player}")
        print(f"\n👾 {enemy}")
        print(f"\nСчет: {self.score} | Врагов: {self.enemies_killed} | Монет: {self.player.gold} 🪙")
        print(f"Предметов: {len(self.player.inventory)}")
        print("-" * 60)
    
    def use_item(self):
        if not self.player.inventory:
            print("У вас нет предметов!")
            return False
        
        print("\nВаши предметы:")
        for i, item in enumerate(self.player.inventory, 1):
            if item["type"] == "potion":
                print(f"{i}. {item['name']} - восстанавливает {item['heal']} HP")
            else:
                print(f"{i}. {item['name']}")
        
        print("0. Отмена")
        
        try:
            choice = int(input("\nВыберите предмет: "))
            if choice == 0:
                return False
            
            item = self.player.inventory[choice - 1]
            
            if item["type"] == "potion":
                self.player.heal(item["heal"])
                self.player.inventory.pop(choice - 1)
                return True
            else:
                print("Этот предмет нельзя использовать в бою")
                return False
                
        except (ValueError, IndexError):
            print("Неверный выбор")
            return False
    
    def battle(self, enemy):
        while self.player.is_alive() and enemy.is_alive():
            self.round_count += 1
            self.show_stats(enemy)
            
            print(f"\n⚔️ Ваш ход против {enemy.name}!")
            print("\nВыберите действие:")
            print("1. Атаковать")
            print("2. Защита (+2 к защите на этот раунд)")
            print("3. Использовать предмет")
            print("4. Попытаться убежать (50% шанс)")
            
            choice = input("Ваш выбор (1-4): ").strip()
            
            if choice == "2":
                print(f"\n{self.player.name} занимает оборонительную позицию!")
                self.player.deff += 2
                self.player.attack(enemy)
                self.player.deff -= 2
            elif choice == "3":
                if self.use_item():
                    pass
                else:
                    self.player.attack(enemy)
            elif choice == "4":
                if random.random() < 0.5:
                    print(f"\n{self.player.name} успешно сбежал!")
                    return "fled"
                else:
                    print(f"\nНе удалось сбежать!")
                    self.player.attack(enemy)
            else:
                self.player.attack(enemy)
            
            if not enemy.is_alive():
                break
            
            input("\nНажмите Enter для продолжения...")
            self.show_stats(enemy)
            
            print(f"\n👾 Ход {enemy.name}!")
            if not enemy.special_ability(self.player):
                enemy.attack(self.player)
            
            input("\nНажмите Enter для продолжения...")
        
        if not self.player.is_alive():
            return "player_dead"
        elif not enemy.is_alive():
            self.score += enemy.exp_value
            self.enemies_killed += 1
            self.player.gain_exp(enemy.exp_value)
            self.player.gold += enemy.gold_drop
            print(f"\n💰 Получено {enemy.gold_drop} монет!")
            
            loot = enemy.generate_loot()
            for loot_item in loot:
                if loot_item["type"] == "gold":
                    self.player.gold += loot_item["amount"]
                    print(f"💰 Найдено еще {loot_item['amount']} монет!")
                elif loot_item["type"] == "item":
                    self.player.add_item(loot_item)
            
            return "enemy_dead"
    
    def visit_shop(self):
        while True:
            self.clear_screen()
            self.shop.show_items(self.player)
            
            try:
                choice = int(input("Выберите товар: "))
                if choice == 0:
                    break
                
                if self.shop.buy(self.player, choice):
                    input("\nНажмите Enter, чтобы продолжить...")
                    
            except ValueError:
                print("Неверный ввод")
                input("Нажмите Enter...")
    
    def rest(self):
        self.clear_screen()
        print("ОТДЫХ У КОСТРА")
        print("-" * 40)
        
        heal_amount = random.randint(20, 40)
        self.player.heal(heal_amount)
        print(f"\nВы отдохнули у костра и восстановили {heal_amount} HP!")
        
        if random.random() < 0.2:
            found_gold = random.randint(5, 20)
            self.player.gold += found_gold
            print(f"🍀 Вы нашли {found_gold} монет!")
        
        input("\nНажмите Enter, чтобы продолжить...")
    
    def save_game(self):
        save_data = {
            "player_name": self.player.name,
            "player_hp": self.player.hp,
            "player_max_hp": self.player.max_hp,
            "player_dmg": self.player.dmg,
            "player_deff": self.player.deff,
            "player_level": self.player.level,
            "player_exp": self.player.exp,
            "player_gold": self.player.gold,
            "score": self.score,
            "enemies_killed": self.enemies_killed,
            "round_count": self.round_count,
            "difficulty": self.difficulty,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        with open("savegame.json", "w", encoding="utf-8") as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
        
        print("💾 Игра сохранена!")
    
    def load_game(self):
        try:
            with open("savegame.json", "r", encoding="utf-8") as f:
                save_data = json.load(f)
            
            self.player = Character(
                save_data["player_name"],
                save_data["player_max_hp"],
                save_data["player_dmg"],
                save_data["player_deff"]
            )
            self.player.hp = save_data["player_hp"]
            self.player.level = save_data["player_level"]
            self.player.exp = save_data["player_exp"]
            self.player.gold = save_data["player_gold"]
            
            self.score = save_data["score"]
            self.enemies_killed = save_data["enemies_killed"]
            self.round_count = save_data["round_count"]
            self.difficulty = save_data["difficulty"]
            
            print("📂 Игра загружена!")
            return True
        except FileNotFoundError:
            print("❌ Сохранение не найдено!")
            return False
    
    def show_main_menu(self):
        self.show_title()
        print("ГЛАВНОЕ МЕНЮ")
        print("-" * 40)
        print("1. Новая игра")
        print("2. Загрузить игру")
        print("3. Выход")
        
        choice = input("\nВаш выбор: ").strip()
        return choice
    
    def game_loop(self):
        while self.player.is_alive():
            if self.enemies_killed > 0 and self.enemies_killed % 3 == 0 and random.random() < 0.3:
                self.visit_shop()
            
            if self.enemies_killed > 0 and self.enemies_killed % 2 == 0 and random.random() < 0.2:
                self.rest()
            
            if self.enemies_killed >= 5 and not self.boss_defeated:
                if random.random() < 0.2:
                    print("\n🔥 ВЫ ЧУВСТВУЕТЕ ПРИСУТСТВИЕ МОЩНОГО ВРАГА! 🔥")
                    enemy = self.generate_enemy(force_boss=True)
                    print(f"\n👾 ВЫ ВСТРЕТИЛИ БОССА: {enemy.name}!")
                    input("Нажмите Enter, чтобы начать битву с боссом...")
                    
                    result = self.battle(enemy)
                    
                    if result == "player_dead":
                        break
                    elif result == "enemy_dead":
                        self.boss_defeated = True
                        print("\n🏆 ВЫ ПОБЕДИЛИ БОССА! 🏆")
                        self.player.gold += 200
                        print("💰 Получено 200 монет за победу над боссом!")
                        self.player.add_item({"name": "Легендарный трофей", "type": "quest_item"})
            
            enemy = self.generate_enemy()
            print(f"\n👾 Вы встретили {enemy.name}!")
            
            choice = input("Начать бой (1), зайти в лавку (2), сохранить игру (3): ").strip()
            
            if choice == "2":
                self.visit_shop()
                continue
            elif choice == "3":
                self.save_game()
                continue
            
            result = self.battle(enemy)
            
            if result == "player_dead":
                break
            elif result == "fled":
                print("\nВы сбежали с поля боя...")
    
    def show_final_stats(self):
        self.clear_screen()
        print("=" * 60)
        print(" " * 20 + "ИГРА ОКОНЧЕНА")
        print("=" * 60)
        print()
        print(f"ИТОГОВАЯ СТАТИСТИКА:")
        print("-" * 40)
        print(f"Имя: {self.player.name}")
        print(f"Уровень: {self.player.level}")
        print(f"Всего раундов: {self.round_count}")
        print(f"Врагов побеждено: {self.enemies_killed}")
        print(f"Всего очков: {self.score}")
        print(f"Монет собрано: {self.player.gold} 🪙")
        
        if self.player.is_alive():
            print(f"\n🏆 ФИНАЛ: ПОБЕДА!")
            if self.boss_defeated:
                print("⭐ ПОБЕЖДЕН БОСС! ИГРА ПРОЙДЕНА! ⭐")
        else:
            print(f"\n💀 Вы пали в бою на {self.round_count} раунде")
            print(f"Последний враг забрал вашу жизнь...")
        
        print("\n" + "=" * 60)
        
        total_score = self.score + self.player.gold + (self.player.level * 50)
        if self.boss_defeated:
            total_score += 500
        
        print(f"ИТОГОВЫЙ СЧЕТ: {total_score}")
        
        if total_score >= 1000:
            print("🏆 РЕЙТИНГ: ЛЕГЕНДА")
        elif total_score >= 500:
            print("⭐ РЕЙТИНГ: ГЕРОЙ")
        elif total_score >= 200:
            print("✨ РЕЙТИНГ: ВОИН")
        else:
            print("📜 РЕЙТИНГ: УЧЕНИК")
        
        print("=" * 60)
    
    def run(self):
        while True:
            choice = self.show_main_menu()
            
            if choice == "1":
                self.create_player()
                self.choose_difficulty()
                self.game_loop()
                self.show_final_stats()
                break
            elif choice == "2":
                if self.load_game():
                    self.game_loop()
                    self.show_final_stats()
                    break
                else:
                    input("Нажмите Enter...")
            else:
                print("\nСпасибо за игру!")
                break
        
        print("\nДо новых встреч!")
        input("\nНажмите Enter для выхода...")


if __name__ == "__main__":
    game = Game()
    game.run()