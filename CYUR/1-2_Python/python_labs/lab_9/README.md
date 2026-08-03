# 🛒 PC Store - Lab 9

Магазин компьютерных комплектующих с интерактивной корзиной на Flask.

## 🚀 Запуск

```bash
pip install flask flask-sqlalchemy
cd lab_9/programm
python main.py
```

Приложение: **http://127.0.0.1:5000**

## 📋 Endpoints

| Метод | Маршрут | Описание |
|-------|---------|---------|
| GET | `/` | Главная страница |
| POST | `/add_to_cart/<id>` | Добавить в корзину |
| POST | `/remove_from_cart/<id>` | Удалить из корзины |
| POST | `/clear_cart` | Очистить корзину |
| POST | `/add_custom_product` | Добавить товар |

## 💾 База данных

**SQLite** (`pc_store.db`)

```
Product:
  - id (PK)
  - name
  - category
  - price
  - description
  - is_custom

CartItem:
  - id (PK)
  - product_id (FK)
  - quantity
```

## 📦 Стек

| Компонент | Технология |
|-----------|-----------|
| Backend | Flask, SQLAlchemy |
| Frontend | HTML5, CSS3, Vanilla JS |
| Database | SQLite |
| API | REST, AJAX |

## ✨ Функции

- ✅ Магазин с предзагруженными товарами
- ✅ AJAX корзина без перезагрузок
- ✅ Форма для добавления пользовательских товаров
- ✅ Glassmorphism дизайн
- ✅ Темно-зеленая палитра
- ✅ Responsive интерфейс

