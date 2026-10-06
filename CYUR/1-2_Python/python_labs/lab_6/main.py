import random

class VideoGameCharacter:

    def __init__(self, name, health, damage):

        self.name = name
        self.max_health = health
        self.health = health
        self.damage = damage
        self.shield = 0  # Текущий щит
        self.is_alive = True

    def __add__(self, other):
        if isinstance(other, VideoGameCharacter):
            new_name = f"{self.name}+{other.name}"
            new_health = self.max_health + other.max_health
            new_damage = self.damage + other.damage
            # Если хотя бы один — Boss, итог тоже Boss
            if isinstance(self, Boss) or isinstance(other, Boss):
                crit_damage = getattr(self, 'crit_damage', 0) + getattr(other, 'crit_damage', 0)
                return Boss(new_name, new_health, new_damage, crit_damage)
            elif isinstance(self, WeakEnemy) or isinstance(other, WeakEnemy):
                regen_rate = getattr(self, 'regen_rate', 0) + getattr(other, 'regen_rate', 0)
                return WeakEnemy(new_name, new_health, new_damage, regen_rate)
            else:
                return VideoGameCharacter(new_name, new_health, new_damage)
        return NotImplemented

    def use_shield(self, shield_amount=30):

        self.shield += shield_amount
        return f"{self.name} использует щит! Щит: +{shield_amount} (всего: {self.shield})"

    def heal(self, heal_amount=25):

        old_health = self.health
        self.health = min(self.health + heal_amount, self.max_health)
        actual_heal = self.health - old_health
        return f"{self.name} лечится! Здоровье: +{actual_heal} (текущее: {self.health}/{self.max_health})"

    def attack(self, target):

        if not target.is_alive:
            return f"{self.name} пытается атаковать мёртвого {target.name}!"

        actual_damage = self.damage

        # Если у цели есть щит
        if target.shield > 0:
            if target.shield >= actual_damage:
                target.shield -= actual_damage
                return f"{self.name} атакует {target.name} на {actual_damage} урона! Щит поглотил весь урон. Щит цели: {target.shield}"
            else:
                # Щит поглощает часть урона
                remaining_damage = actual_damage - target.shield
                target.shield = 0
                target.health -= remaining_damage
                result = f"{self.name} атакует {target.name} на {actual_damage} урона! Щит поглотил {actual_damage - remaining_damage}, нанесено {remaining_damage} урона."
        else:
            target.health -= actual_damage
            result = f"{self.name} атакует {target.name} на {actual_damage} урона!"

        # Проверка смерти
        if target.health <= 0:
            target.health = 0
            target.is_alive = False
            result += f" {target.name} повержен!"
        else:
            result += f" HP {target.name}: {target.health}/{target.max_health}"

        return result

    def choose_action(self, warriors):

        # Получаем живых противников
        enemies = [w for w in warriors if w != self and w.is_alive]

        if not enemies:
            return f"{self.name} не имеет целей для атаки"

        # Логика выбора действия
        health_percent = (self.health / self.max_health) * 100

        # Если здоровье меньше 30% - лечимся
        if health_percent < 30 and self.health < self.max_health:
            return self.heal()

        # Если здоровье между 30% и 60% и нет щита - ставим щит
        if health_percent < 60 and self.shield == 0:
            return self.use_shield()

        # Иначе атакуем противника с наибольшим HP
        target = max(enemies, key=lambda w: w.health)
        return self.attack(target)

    def __str__(self):
        status = "ЖИВ" if self.is_alive else "МЁРТВ"
        return f"{self.name}: HP={self.health}/{self.max_health}, Урон={self.damage}, Щит={self.shield} [{status}]"


class WeakEnemy(VideoGameCharacter):


    def __init__(self, name, health, damage, regen_rate):

        super().__init__(name, health, damage)
        self.regen_rate = regen_rate

    def heal(self, heal_amount=None):

        if heal_amount is None:
            heal_amount = 20 + self.regen_rate
        return super().heal(heal_amount)

    def choose_action(self, warriors):

        enemies = [w for w in warriors if w != self and w.is_alive]

        if not enemies:
            return f"{self.name} не имеет целей для атаки"

        health_percent = (self.health / self.max_health) * 100

        # Слабые враги лечатся при HP < 40%
        if health_percent < 40 and self.health < self.max_health:
            return self.heal()

        # Чаще используют щит (при HP < 70%)
        if health_percent < 70 and self.shield < 20:
            return self.use_shield(25)

        # Атакуем врага с наибольшим HP
        target = max(enemies, key=lambda w: w.health)
        return self.attack(target)


class Boss(VideoGameCharacter):


    def __init__(self, name, health, damage, crit_damage):

        super().__init__(name, health, damage)
        self.crit_damage = crit_damage

    def attack(self, target):

        # 30% шанс критического удара
        if random.random() < 0.3:
            old_damage = self.damage
            self.damage += self.crit_damage
            result = super().attack(target)
            result = f"⚡ КРИТИЧЕСКИЙ УДАР! " + result
            self.damage = old_damage
            return result
        else:
            return super().attack(target)

    def use_shield(self, shield_amount=50):
        return super().use_shield(shield_amount)

    def heal(self, heal_amount=35):
        return super().heal(heal_amount)

    def choose_action(self, warriors):
        enemies = [w for w in warriors if w != self and w.is_alive]

        if not enemies:
            return f"{self.name} не имеет целей для атаки"

        health_percent = (self.health / self.max_health) * 100

        # Босс лечится только при критическом HP < 25%
        if health_percent < 25 and self.health < self.max_health:
            return self.heal()

        # Редко использует щит (только при HP < 40%)
        if health_percent < 40 and self.shield == 0:
            return self.use_shield()

        # Обычно атакует врага с наибольшим HP
        target = max(enemies, key=lambda w: w.health)
        return self.attack(target)


def battle_simulation():



    # Создание трёх воинов разных типов
    warrior1 = VideoGameCharacter(name="Воин", health=20, damage=15)
    warrior2 = WeakEnemy(name="Разбойник", health=80, damage=40, regen_rate=5)
    warrior3 = Boss(name="Чемпион", health=150, damage=80, crit_damage=15)

    warriors = [warrior1, warrior2, warrior3]

    # Объединение двух самых слабых
    two_weakest = sorted(warriors, key=lambda w: w.max_health)[:2]
    combined = two_weakest[0] + two_weakest[1]
    print(f"\nСоздан новый воин объединением: {combined}")
    warriors.append(combined)

    print("НАЧАЛЬНОЕ СОСТОЯНИЕ:")
    print("-" * 70)
    for warrior in warriors:
        print(f"  {warrior}")
    print()

    # Битва по раундам
    round_num = 1
    max_rounds = 50  # Ограничение на количество раундов

    while round_num <= max_rounds:
        alive_warriors = [w for w in warriors if w.is_alive]

        # Проверка условия окончания битвы
        if len(alive_warriors) <= 1:
            break

        print(f"{'═' * 70}")
        print(f"РАУНД {round_num}")
        print(f"{'═' * 70}")

        # Каждый живой воин делает ход
        for warrior in warriors:
            if warrior.is_alive:
                action_result = warrior.choose_action(warriors)
                print(f"  {action_result}")



        round_num += 1

    # Результаты битвы
    print("=" * 70)
    print("БИТВА ЗАВЕРШЕНА!")
    print("=" * 70)
    print()

    alive_warriors = [w for w in warriors if w.is_alive]

    if len(alive_warriors) == 1:
        winner = alive_warriors[0]
        print(f"🏆 ПОБЕДИТЕЛЬ: {winner.name}!")
        print(f"   Оставшееся HP: {winner.health}/{winner.max_health}")
        print(f"   Щит: {winner.shield}")
    elif len(alive_warriors) == 0:
        print("⚔️ ВСЕ ВОИНЫ ПАЛИ В БОЮ!")
    else:
        print(f"⏱️ БИТВА НЕ ЗАВЕРШЕНА (достигнут лимит в {max_rounds} раундов)")
        print("Выжившие воины:")
        for warrior in alive_warriors:
            print(f"  - {warrior.name}: HP={warrior.health}/{warrior.max_health}")




# Запуск симуляции
if __name__ == "__main__":
    battle_simulation()