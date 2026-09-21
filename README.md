# Эмулятор UNIX-подобной оболочки — вариант 16

Учебная работа по дисциплине «Конфигурационное управление».
Программа реализует графический эмулятор командной строки, работающий
с виртуальной файловой системой (VFS), загружаемой из JSON.

## Что реализовано

- GUI на Tkinter.
- Имя VFS в заголовке окна.
- Простой парсер: команда и аргументы разделяются пробелами.
- Ошибки неизвестных команд и неверных аргументов.
- Параметры запуска `--vfs` и `--script`.
- Стартовый скрипт останавливается при первой ошибке.
- VFS загружается из JSON и изменяется только в памяти.
- Текстовые файлы и base64 для двоичных данных.
- Команды `ls`, `cd`, `cal`, `head`, `tac`, `mkdir`, `exit`.
- Набор VFS разных размеров и глубины.
- BAT/SH-скрипты для проверки параметров запуска.
- Unit-тесты.

## Структура

```text
.
├── README.md
├── .gitignore
├── run.bat
├── run.sh
├── src/
│   ├── main.py
│   ├── app.py
│   ├── shell.py
│   └── vfs.py
├── tests/
│   └── test_shell.py
├── fixtures/
│   ├── vfs_minimal.json
│   ├── vfs_demo.json
│   └── vfs_files.json
└── scripts/
    ├── startup_all.txt
    ├── startup_ok.txt
    ├── test_minimal.bat
    ├── test_demo.bat
    ├── test_startup.bat
    ├── test_minimal.sh
    ├── test_demo.sh
    └── test_startup.sh
```

## Запуск

Windows:

```bat
run.bat
```

Или явно:

```bat
python src\main.py --vfs fixtures\vfs_demo.json
```

Со стартовым скриптом:

```bat
python src\main.py --vfs fixtures\vfs_demo.json ^
  --script scripts\startup_all.txt
```

Linux/macOS:

```sh
./run.sh
```

## Тесты

```bash
python -m unittest discover -s tests -v
```

## Команды эмулятора

### `ls [PATH]`
Показывает содержимое текущей или указанной директории.

### `cd PATH`
Переходит в другую директорию VFS. Поддерживаются `/`, `.`, `..`.

### `cal [YEAR]` и `cal MONTH YEAR`
Печатает календарь текущего месяца, указанного года или месяца.

### `head [-n N] FILE`
Показывает первые 10 строк файла либо первые `N` строк.

### `tac FILE`
Показывает строки файла в обратном порядке.

### `mkdir DIRECTORY`
Создаёт директорию только в памяти. Исходный JSON не меняется.

### `exit`
Закрывает приложение.

## Формат VFS

```json
{
  "name": "demo-vfs",
  "root": {
    "type": "dir",
    "children": {
      "hello.txt": {
        "type": "file",
        "encoding": "text",
        "content": "Hello"
      }
    }
  }
}
```

Для двоичных данных используется `"encoding": "base64"`.

## Как показать преподавателю

1. Запустить `scripts/test_demo.bat`.
2. Показать `ls`, `cd`, ошибочную команду и неверные аргументы.
3. Запустить `scripts/test_startup.bat` и показать, что выполнение
   останавливается на `unknown_command`.
4. Показать разные JSON VFS из `fixtures`.
5. Показать `cal`, `head`, `tac`.
6. Выполнить `mkdir test`, затем `ls`.
7. Закрыть приложение и показать, что JSON на диске не изменился.
8. Запустить unit-тесты.

## Рекомендуемая история коммитов

Работа должна быть разбита на этапы. Примеры Conventional/Scoped Commits:

```text
feat(repl): add GUI shell prototype
feat(config): add CLI options and startup scripts
feat(vfs): load JSON virtual file system in memory
feat(commands): implement ls cd cal head and tac
feat(mkdir): add in-memory mkdir command
```

Если проект уже готов целиком, не делайте пять фиктивных коммитов с одним
и тем же состоянием. Лучше переносить изменения по этапам или использовать
эти сообщения во время последовательной разработки.
