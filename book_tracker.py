import json
import os
from abc import ABC, abstractmethod


class Book:
    def __init__(self, title: str, author: str, genre: str, pages: int):
        self._title = title
        self._author = author
        self._genre = genre
        self._pages = pages

    @property
    def title(self):
        return self._title

    @property
    def author(self):
        return self._author

    @property
    def genre(self):
        return self._genre

    @property
    def pages(self):
        return self._pages

    def to_dict(self):
        return {
            "title": self._title,
            "author": self._author,
            "genre": self._genre,
            "pages": self._pages
        }

    @staticmethod
    def from_dict(data: dict):
        return Book(data["title"], data["author"], data["genre"], data["pages"])

    def __str__(self):
        return f'"{self._title}" — {self._author} ({self._genre}, {self._pages} стр.)'


class ActionHistory:
    def __init__(self):
        self._stack = []

    def push(self, action: str):
        self._stack.append(action)

    def get_all(self):
        return list(self._stack)

    def clear(self):
        self._stack.clear()


class BookRepository:
    def __init__(self, filepath="books.json"):
        self.filepath = filepath
        self.books = []
        self.load()

    def load(self):
        if os.path.exists(self.filepath):
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.books = [Book.from_dict(item) for item in data]
        else:
            self.books = []
            self.save()

    def save(self):
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump([book.to_dict() for book in self.books], f, indent=2, ensure_ascii=False)

    def add(self, book: Book):
        self.books.append(book)
        self.save()

    def update(self, index: int, book: Book):
        self.books[index] = book
        self.save()

    def delete(self, index: int):
        del self.books[index]
        self.save()


class BookView:
    @staticmethod
    def show_menu():
        print("\n=== Меню Book Tracker ===")
        print("1. Добавить книгу")
        print("2. Редактировать книгу")
        print("3. Удалить книгу")
        print("4. Показать все книги")
        print("5. Фильтр книг")
        print("6. История действий")
        print("7. Выход")

    @staticmethod
    def get_choice():
        return input("Введите номер действия: ").strip()

    @staticmethod
    def get_book_input():
        title = input("Введите название: ").strip()
        author = input("Введите автора: ").strip()
        genre = input("Введите жанр: ").strip()
        pages_str = input("Введите количество страниц: ").strip()
        return title, author, genre, pages_str

    @staticmethod
    def show_message(msg: str):
        print(msg)

    @staticmethod
    def show_books(books: list[Book], header="Ваши книги:"):
        if not books:
            print("Книги не найдены.")
            return
        print(header)
        for i, book in enumerate(books, start=1):
            print(f"{i}. {book}")

    @staticmethod
    def get_book_index(max_index: int, action: str):
        idx_str = input(f"Введите номер книги для {action} (1-{max_index}): ").strip()
        return idx_str

    @staticmethod
    def show_filter_menu():
        print("\nФильтровать по:")
        print("1. Жанру")
        print("2. Количеству страниц")
        return input("Выберите тип фильтра: ").strip()

    @staticmethod
    def get_genre_filter():
        return input("Введите жанр: ").strip()

    @staticmethod
    def get_page_filter():
        print("Операторы сравнения: >, <, =")
        comp = input("Введите оператор сравнения: ").strip()
        pages_str = input("Введите количество страниц: ").strip()
        return comp, pages_str

    @staticmethod
    def show_history(history: list[str]):
        if not history:
            print("История пуста.")
            return
        print("История действий:")
        for i, action in enumerate(history, start=1):
            print(f"{i}. {action}")


class BaseCommand(ABC):
    @abstractmethod
    def execute(self):
        pass


class AddBookCommand(BaseCommand):
    def __init__(self, repository, view, history):
        self.repo = repository
        self.view = view
        self.history = history

    def execute(self):
        title, author, genre, pages_str = self.view.get_book_input()
        if not title or not author or not genre:
            self.view.show_message("Ошибка: название, автор и жанр не могут быть пустыми.")
            return
        if not pages_str.isdigit() or int(pages_str) <= 0:
            self.view.show_message("Ошибка: количество страниц должно быть положительным целым числом.")
            return
        pages = int(pages_str)
        book = Book(title, author, genre, pages)
        self.repo.add(book)
        self.history.push(f"Добавлена книга: {title}")
        self.view.show_message("Книга успешно добавлена.")


class EditBookCommand(BaseCommand):
    def __init__(self, repository, view, history):
        self.repo = repository
        self.view = view
        self.history = history

    def execute(self):
        if not self.repo.books:
            self.view.show_message("Нет книг для редактирования.")
            return
        self.view.show_books(self.repo.books)
        idx_str = self.view.get_book_index(len(self.repo.books), "редактирования")
        if not idx_str.isdigit():
            self.view.show_message("Неверный ввод.")
            return
        idx = int(idx_str) - 1
        if idx < 0 or idx >= len(self.repo.books):
            self.view.show_message("Неверный номер книги.")
            return
        old_title = self.repo.books[idx].title
        self.view.show_message("Введите новые данные (оставьте поле пустым, чтобы сохранить старое значение):")
        title, author, genre, pages_str = self.view.get_book_input()
        book = self.repo.books[idx]
        new_title = title if title else book.title
        new_author = author if author else book.author
        new_genre = genre if genre else book.genre
        new_pages = book.pages
        if pages_str:
            if not pages_str.isdigit() or int(pages_str) <= 0:
                self.view.show_message("Количество страниц не изменено (некорректный ввод).")
            else:
                new_pages = int(pages_str)
        updated_book = Book(new_title, new_author, new_genre, new_pages)
        self.repo.update(idx, updated_book)
        self.history.push(f"Отредактирована книга: {old_title}")
        self.view.show_message("Книга обновлена.")


class DeleteBookCommand(BaseCommand):
    def __init__(self, repository, view, history):
        self.repo = repository
        self.view = view
        self.history = history

    def execute(self):
        if not self.repo.books:
            self.view.show_message("Нет книг для удаления.")
            return
        self.view.show_books(self.repo.books)
        idx_str = self.view.get_book_index(len(self.repo.books), "удаления")
        if not idx_str.isdigit():
            self.view.show_message("Неверный ввод.")
            return
        idx = int(idx_str) - 1
        if idx < 0 or idx >= len(self.repo.books):
            self.view.show_message("Неверный номер книги.")
            return
        title = self.repo.books[idx].title
        self.repo.delete(idx)
        self.history.push(f"Удалена книга: {title}")
        self.view.show_message("Книга удалена.")


class ViewAllBooksCommand(BaseCommand):
    def __init__(self, repository, view):
        self.repo = repository
        self.view = view

    def execute(self):
        self.view.show_books(self.repo.books)


class FilterBooksCommand(BaseCommand):
    def __init__(self, repository, view):
        self.repo = repository
        self.view = view

    def execute(self):
        filter_type = self.view.show_filter_menu()
        if filter_type == "1":
            genre = self.view.get_genre_filter()
            if not genre:
                self.view.show_message("Жанр не может быть пустым.")
                return
            filtered = [b for b in self.repo.books if b.genre.lower() == genre.lower()]
            self.view.show_books(filtered, f"Книги в жанре '{genre}':")
        elif filter_type == "2":
            comp, pages_str = self.view.get_page_filter()
            if comp not in (">", "<", "=") or not pages_str.isdigit():
                self.view.show_message("Неверные параметры фильтра.")
                return
            pages = int(pages_str)
            if comp == ">":
                filtered = [b for b in self.repo.books if b.pages > pages]
            elif comp == "<":
                filtered = [b for b in self.repo.books if b.pages < pages]
            else:
                filtered = [b for b in self.repo.books if b.pages == pages]
            self.view.show_books(filtered, f"Книги с количеством страниц {comp} {pages}:")
        else:
            self.view.show_message("Неверный выбор.")


class ShowHistoryCommand(BaseCommand):
    def __init__(self, history, view):
        self.history = history
        self.view = view

    def execute(self):
        self.view.show_history(self.history.get_all())


class ExitCommand(BaseCommand):
    def __init__(self, view):
        self.view = view

    def execute(self):
        self.view.show_message("До свидания!")
        exit(0)


class BookController:
    def __init__(self):
        self.repository = BookRepository()
        self.view = BookView()
        self.history = ActionHistory()
        self.commands = {
            "1": AddBookCommand(self.repository, self.view, self.history),
            "2": EditBookCommand(self.repository, self.view, self.history),
            "3": DeleteBookCommand(self.repository, self.view, self.history),
            "4": ViewAllBooksCommand(self.repository, self.view),
            "5": FilterBooksCommand(self.repository, self.view),
            "6": ShowHistoryCommand(self.history, self.view),
            "7": ExitCommand(self.view)
        }

    def run(self):
        while True:
            self.view.show_menu()
            choice = self.view.get_choice()
            command = self.commands.get(choice)
            if command:
                command.execute()
            else:
                self.view.show_message("Неверный номер действия. Попробуйте снова.")


if __name__ == "__main__":
    app = BookController()
    app.run()