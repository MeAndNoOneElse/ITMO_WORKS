# Лабораторная работа №6
## Объектно-ориентированное программирование
**Вариант 9 — Персонаж видеоигры с боевой системой**

---

## Описание задачи

Создать иерархию классов для симуляции боя между персонажами видеоигры с использованием наследования, полиморфизма и перегрузки операторов. Каждый персонаж может выполнять три действия: атаковать, использовать щит или лечиться.

---

## Реализованные классы

### 1. VideoGameCharacter (базовый класс)
**Поля:**
- `name` — имя персонажа
- `max_health` — максимальное здоровье
- `health` — текущее здоровье
- `damage` — урон за удар
- `shield` — текущее значение щита
- `is_alive` — флаг состояния (жив/мёртв)

**Методы:**
- `use_shield(shield_amount=30)` — добавить щит
- `heal(heal_amount=25)` — восстановить здоровье
- `attack(target)` — атаковать цель (урон поглощается щитом)
- `choose_action(warriors)` — AI для выбора действия
- `__add__(other)` — **перегрузка оператора +** для объединения двух персонажей

**Логика AI базового персонажа:**
- HP < 30% → лечение
- HP < 60% и щит = 0 → щит
- Иначе → атака врага с наибольшим HP

### 2. WeakEnemy (наследник)
**Уникальные поля:**
- `regen_rate` — регенерация здоровья при лечении

**Переопределённые методы:**
- `heal()` — эффективность: 20 + regen_rate HP
- `choose_action()` — более осторожная тактика

**Особенности:** Более слабый, но использует щит чаще (HP < 70%)

### 3. Boss (наследник)
**Уникальные поля:**
- `crit_damage` — дополнительный урон при критических ударах

**Переопределённые методы:**
- `attack()` — 30% шанс критического удара
- `use_shield()` — более мощный щит (50 HP)
- `heal()` — эффективнее (35 HP)
- `choose_action()` — агрессивная тактика

**Особенности:** Максимальные ресурсы, редко защищается, часто атакует

---

## Перегрузка оператора + (`__add__`)

```python
def __add__(self, other):
    if isinstance(other, VideoGameCharacter):
        new_name = f"{self.name}+{other.name}"
        new_health = self.max_health + other.max_health
        new_damage = self.damage + other.damage
        
        # Определение класса объединённого персонажа
        if isinstance(self, Boss) or isinstance(other, Boss):
            crit_damage = getattr(self, 'crit_damage', 0) + getattr(other, 'crit_damage', 0)
            return Boss(new_name, new_health, new_damage, crit_damage)
        elif isinstance(self, WeakEnemy) or isinstance(other, WeakEnemy):
            regen_rate = getattr(self, 'regen_rate', 0) + getattr(other, 'regen_rate', 0)
            return WeakEnemy(new_name, new_health, new_damage, regen_rate)
        else:
            return VideoGameCharacter(new_name, new_health, new_damage)
    return NotImplemented
```

**Применение:** Два самых слабых персонажа объединяются в одного с суммированными характеристиками.

