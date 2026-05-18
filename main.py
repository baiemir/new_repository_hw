# Привозим коробку с деталями LEGO (Flet) для сборки интерфейса
import flet as ft
# Достаем наш умный блокнот (базу данных), чтобы сохранять задачи навсегда
from db import main_db

import datetime as dt

# Это главная функция — инструкция по сборке нашей "комнаты" (экрана приложения)
def main_page(page: ft.Page):
    page.title = "To-Do List"  # Вешаем вывеску с названием на верхушку окошка
    page.theme_mode = ft.ThemeMode.DARK  # Включаем "ночной режим", чтобы глазам было приятно

    # Создаем пустой вертикальный стеллаж (столбик), куда будем один за другим складывать наши задания
    task_list = ft.Column()

    # Это фабрика по созданию красивых строчек с задачами. 
    # Ей дают "номер" задачи из блокнота и сам "текст" задачи.
    def view_tasks(task_id, task_text, date_time=''):
        # Создаем текстовое поле, пишем туда нашу задачу, растягиваем на всю ширину (expand=True) 
        # и "замораживаем" (read_only=True), чтобы случайно нельзя было стереть букву
        task_field = ft.TextField(value=task_text, expand=True, read_only=True)
        # Создаем красивый серый текст для времени создания задачи и делаем его поменьше (size=12)
        time_label = ft.Text(value=date_time, size=12)  # Маленькая табличка с временем создания задачи

        # Секретная кнопка-сохранялка. Срабатывает, когда мы закончили редактировать текст
        def save_edit(_):
            # Открываем блокнот (БД) и перезаписываем старый текст на новый
            main_db.update_task(task_id=task_id, new_task=task_field.value)
            # Снова "замораживаем" поле (делаем только для чтения)
            task_field.read_only = True
            # Говорим приложению: "Обнови экран, мы закончили!"
            page.update()

        # Создаем саму кнопочку с картинкой дискеты (сохранение) и привязываем к ней функцию выше
        save_button = ft.IconButton(icon=ft.Icons.SAVE, on_click=save_edit)

        # Функция-обработчик, которая срабатывает при нажатии на кнопку удаления
        def delete_task(e):
            # 1. Удаляем задачу из базы данных по её уникальному ID
            main_db.delete_task(task_id=task_id)
            # 2. Удаляем визуальный контейнер (строку) с задачей из списка элементов Flet.
            # e.control — это сама кнопка, а .parent — это строка (Row), в которой она находится.
            task_list.controls.remove(e.control.parent)  
            # 3. Обновляем виджет списка, чтобы изменения сразу отобразились на экране
            task_list.update()
            # Создаем кнопку-иконку (корзину) и привязываем к ней функцию delete_task
        delete_button = ft.IconButton(icon=ft.Icons.DELETE, on_click=delete_task)

        # Кнопка-переключатель "Карандаш". Включает и выключает режим редактирования
        def enable_edit(_):
            # Если поле сейчас заморожено — размораживаем его для печати
            if task_field.read_only == True:
                task_field.read_only = False
            # Если оно уже было открыто — замораживаем обратно
            else:
                task_field.read_only = True
            # Обновляем экран, чтобы увидеть изменения (например, появление курсора)
            page.update()

        # Создаем кнопку с картинкой карандаша (редактирование)
        edit_button = ft.IconButton(icon=ft.Icons.EDIT, on_click=enable_edit)
        
        # Склеиваем всё в одну горизонтальную линию: [ Текст задачи | Карандаш | Дискета ]
        return ft.Row([task_field, edit_button, save_button, time_label, delete_button])
    
    


    # Функция-помощник: срабатывает, когда мы написали новую задачу и нажали Enter
    def add_task_flet(_):
        # Проверяем: мы точно что-то написали, или там пусто?
        if task_input.value:
            task_text = task_input.value.strip()  # Убираем лишние пробелы по бокам
            # Записываем задачу в наш блокнот (БД). Блокнот возвращает нам уникальный номер (id) задачи
            task_id = main_db.add_task(task=task_text)
            # 1. 🕒 Спрашиваем у Python текущее время и форматируем его (Часы:Минуты)
            current_time = dt.datetime.now().strftime("%y-%m-%d %H:%M")
            # Очищаем поле ввода, чтобы оно снова стало пустым для новой задачи
            task_input.value = None
            # Собираем красивую строчку с кнопками через фабрику `view_tasks` 
            # и вешаем её на наш вертикальный стеллаж (task_list)
            task_list.controls.append(view_tasks(task_id=task_id, task_text=task_text, date_time=current_time))
            # Просим приложение перерисовать экран, чтобы новая задача сразу появилась
            page.update()
 
    # Создаем большую коробку-поле для ввода вверху экрана с подсказкой "Введите задачу"
    # Если нажать Enter в этом поле (on_submit), сработает функция добавления
    task_input = ft.TextField(label="Введите задачу", on_submit=add_task_flet)

    # Выставляем на наш главный экран сначала поле ввода, а под ним — стеллаж со всеми задачами
    page.add(task_input, task_list)

# Главный пусковой рубильник программы
if __name__ == "__main__":
    main_db.init_db()  # Сначала сдуваем пыль с блокнота (базы данных) и готовим его к работе
    ft.app(main_page)  # А теперь запускаем само LEGO-приложение с нашей инструкцией сборки!