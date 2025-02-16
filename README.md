# TODO<!-- omit from toc -->
![Static Badge](https://img.shields.io/badge/python-3.11-brightgreen?style=flat&logo=python)
![Static Badge](https://img.shields.io/badge/coverage-0%25-red?logo=pytest)
![Static Badge](https://img.shields.io/badge/tests-failing-red?style=flat&logo=pytest)
![Static Badge](https://img.shields.io/badge/flake8-passing-brightgreen?style=flat&logo=python)
![Static Badge](https://img.shields.io/badge/mypy-failing-red?style=flat&logo=python)
![Static Badge](https://img.shields.io/badge/isort-passing-brightgreen?style=flat&logo=python)
![Static Badge](https://img.shields.io/badge/black-passing-brightgreen?style=flat&logo=python)

## Оглавление<!-- omit from toc -->
* [Запуск тестов](#запуск-тестов)
    * [Вне Docker-контейнера](#вне-docker-контейнера)
* [Запуск flake8](#запуск-flake8)
    * [Вне Docker-контейнера](#вне-docker-контейнера-1)
* [Запуск mypy](#запуск-mypy)
    * [Вне Docker-контейнера](#вне-docker-контейнера-2)
* [Разработка](#разработка)
    * [Форматирование кода](#форматирование-кода)
    * [Git хуки](#git-хуки)
- [Запуск тестов](#запуск-тестов)
- [Запуск Flake8](#запуск-flake8)
- [Запуск mypy](#запуск-mypy)
- [Разработка](#разработка)
  - [Форматирование кода](#форматирование-кода)
  - [Git хуки](#git-хуки)
    - [Pre-commit хуки](#pre-commit-хуки)
    - [Pre-push хуки](#pre-push-хуки)
  - [Git хуки](#git-хуки-1)
    - [Pre-commit хуки](#pre-commit-хуки-1)
    - [Pre-push хуки](#pre-push-хуки-1)
  - [Make](#make)
  - [CHANGELOG.md](#changelogmd)

## Запуск тестов
1. Перейти в директорию с [конфигурационным файлом](./pyproject.toml)
2. Начать выполнение тестов через команду

    ```bash
    poetry run pytest .
    ```

    или 

    ```bash
    make test
    ```

## Запуск Flake8
1. Перейти в директорию с [конфигурационным файлом](./.flake8)
2. Начать выполнение `flake8` через команду

    ```bash
    poetry run flake8 .
    ```

    или 

    ```bash
    make lint
    ```

## Запуск mypy
1. Перейти в директорию с [конфигурационным файлом](./pyproject.toml)
2. Начать выполнение `mypy` через команду

    ```bash
    poetry run mypy .
    ```

    или 

    ```bash
    make typecheck
    ```

## Разработка
### Форматирование кода
При разработке рекомендуется использовать [black](https://pypi.org/project/black/), чтобы поддерживать чистоту кода и избегать лишних изменений при работе с гитом.<br>
Пример конфигурационного файла для Visual Studio Code `.vscode/settings.json`:
```json
{
    "python.analysis.autoImportCompletions": true,
    "[python]": {
        "editor.defaultFormatter": "ms-python.black-formatter",
        "editor.formatOnSave": true
    }
}
```

### Git хуки
При разработке рекомендуется использовать [pre-commit](https://pre-commit.com/), чтобы перед формированием МР код был уже подготовленным и поверхностно проверенным (например, через `flake8`)<br><br>
**Для использования должны быть установлены dev-зависимости**

#### Pre-commit хуки
Установка
```bash
poetry run pre-commit install
```
Удаление
```bash
poetry run pre-commit uninstall
```
После установки, при каждом коммите будут отрабатывать хуки из [конфигурационного файла](./.pre-commit-config.yaml), предназначенные для коммитов (`stages: [commit]`)

#### Pre-push хуки
Установка
```bash
poetry run pre-commit install --hook-type pre-push
```
Удаление
```bash
poetry run pre-commit uninstall -t pre-push
```
После установки, при каждом пуше будут отрабатывать хуки из [конфигурационного файла](./.pre-commit-config.yaml), предназначенные для пушей (`stages: [push]`)

### Git хуки
При разработке рекомендуется использовать [pre-commit](https://pre-commit.com/), чтобы перед формированием МР код был уже подготовленным и поверхностно проверенным (например, через `flake8`)<br><br>
**Для использования должны быть установлены dev-зависимости**

#### Pre-commit хуки
Установка
```bash
poetry run pre-commit install
```
Удаление
```bash
poetry run pre-commit uninstall
```
После установки, при каждом коммите будут отрабатывать хуки из [конфигурационного файла](./.pre-commit-config.yaml), предназначенные для коммитов (`stages: [commit]`)

#### Pre-push хуки
Установка
```bash
poetry run pre-commit install --hook-type pre-push
```
Удаление
```bash
poetry run pre-commit uninstall -t pre-push
```
После установки, при каждом пуше будут отрабатывать хуки из [конфигурационного файла](./.pre-commit-config.yaml), предназначенные для пушей (`stages: [push]`)

### Make
Для удобного запуска тестов и т.п. в проекте есть [Makefile](./Makefile)

Для выполнения инструкции, на примере запуска тестов, нужно выполнить команду
```bash
make test
```

### CHANGELOG.md
По готовности релиза в `release/*` ветке или при хотфиксе в `hotfix/*` ветке, нужно обновить файл [CHANGELOG.md](./CHANGELOG.md).  

Заметки о новом релизе добавляются в начало файла, т.е. до предыдущего релиза.
Шаблон заметки о релизе
```md
## 1.1.0 (2024-01-01)

Security:

  -   

Features:

  - 

Bugfixes:

  - 

```

При необходимости, можно вести заметки о будущем релизе прямо в ветке `develop`. В таком случае, вместо даты релиза нужно писать `unreleased`, который потом следует заменить на фактическую дату релиза
```md
## 1.2.0 (unreleased)

Security:

  -   

Features:

  - 

Bugfixes:

  - 

```