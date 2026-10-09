# Эмулятор командной оболочки — вариант 16

## Этап 4. Основные команды

Реализован графический эмулятор UNIX-подобной командной оболочки,
работающий с виртуальной файловой системой из JSON-файла.

## Возможности

- графический интерфейс на Tkinter;
- параметры запуска `--vfs` и `--script`;
- выполнение стартового скрипта до первой ошибки;
- VFS загружается из JSON и хранится в оперативной памяти;
- поддержка текстовых и base64-данных;
- навигация по абсолютным и относительным путям;
- команды `ls`, `cd`, `cal`, `head`, `tac`, `exit`;
- обработка неизвестных команд и неверных аргументов.

Команда `mkdir` на данном этапе ещё не реализована. Она будет добавлена
на этапе 5.

## Запуск

На Windows:

```bash
run.bat
```

Или вручную:

```bash
python src/main.py --vfs fixtures/vfs_demo.json
```

Со стартовым скриптом:

```bash
python src/main.py --vfs fixtures/vfs_demo.json --script scripts/startup_all.txt
```

## Команды

- `ls [PATH]` — показать содержимое директории;
- `cd PATH` — перейти в директорию;
- `cal` — показать календарь текущего месяца;
- `cal YEAR` — показать календарь указанного года;
- `cal MONTH YEAR` — показать календарь указанного месяца;
- `head FILE` — показать первые 10 строк файла;
- `head -n COUNT FILE` — показать указанное число первых строк;
- `tac FILE` — показать строки файла в обратном порядке;
- `exit` — завершить работу эмулятора.

## Пример

```text
demo-vfs:/$ ls
binary.dat
hello.txt
home

demo-vfs:/$ cd home/student/docs

demo-vfs:/home/student/docs$ head -n 2 notes.txt
line 1
line 2
```

## Тестовые VFS

В каталоге `fixtures` находятся несколько вариантов VFS:

- `vfs_minimal.json` — минимальная файловая система;
- `vfs_files.json` — файловая система с несколькими файлами;
- `vfs_demo.json` — вложенная структура с несколькими уровнями папок.

## Тесты

```bash
python -m unittest discover -s tests -v
```

## Структура проекта

```text
src/
    main.py
    app.py
    shell.py
    vfs.py
fixtures/
    vfs_minimal.json
    vfs_files.json
    vfs_demo.json
scripts/
    startup_ok.txt
    startup_error.txt
    startup_all.txt
    test_startup.bat
tests/
    test_shell.py
    test_vfs.py
README.md
.gitignore
run.bat
run.sh
```
