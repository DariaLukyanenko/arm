#!/bin/bash
set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ALL_DIRS=("schemas" "users" "tables" "indexes" "data" "constraints")

POSTGRES_CONNECTION_STR=""
OPTION=""
ARGS=()

show_help() {
    echo "Использование: ./$(basename "$0") [СТРОКА ПОДКЛЮЧЕНИЯ К БД] [ОПЦИЯ] [ПАРАМЕТРЫ ОПЦИИ]"
    echo ""
    echo "Опции:"
    echo "  -h, --help        Показать справку"
    echo "  -l, --list        Показать доступные директории"
    echo "  -f, --file        Выполнить SQL-скрипт"
    echo "  -d, --dir         Выполнить SQL-скрипты в указанной директории"
    echo "  -b, --build       Собрать базу данных"
    echo ""
}

show_list() {
    echo "Доступные директории для выполнения SQL-скриптов: "
    echo "  users             Настройка пользователей"
    echo "  schemas           Настройка схем"
    echo "  tables            Создание таблиц"
    echo "  constraints       Создание ограничений"
    echo "  indexes           Создание индексов"
    echo "  data              Загрузка первоначальных данных"
}

load_file() {
    local connection_str="$1"
    local filepath="$2"

    if [[ "$filepath" != *.sql ]]; then
        echo -e "${RED}Ошибка: файл "$filepath" имеет не .sql расширение!${NC}"
        exit 1
    fi

    if [ ! -f "$filepath" ]; then
        echo -e "${RED}Ошибка: файл "$filepath" не существует!${NC}"
        exit 1
    fi

    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] - "$filepath"${NC}"
    while IFS= read -r line; do eval "echo \"$line\""; done < "$filepath" | psql "$connection_str"
}

load_dir() {
    local connection_str="$1"
    local dirpath="$2"

    if find "$dirpath" -maxdepth 1 -name "*.sql" -type f | grep -q .; then
        echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] - "$dirpath"${NC}"
        for sql_file in "$dirpath"/*.sql; do
            load_file "$connection_str" "$sql_file"
        done
    fi
}

build() {
    local connection_str="$1"

    for dir in "${ALL_DIRS[@]}"; do
        load_dir $connection_str "${SCRIPT_DIR}/${dir}"
    done
}

get_option() {
    local option_count=0

    for option in "$@"; do
        case "$option" in
            "-h"|"--help"|"-l"|"--list"|"-d"|"--dir"|"-f"|"--file"|"-b"|"--build")
                ((option_count++))
                if [ $option_count -gt 1 ]; then
                    echo -e "${RED}Ошибка: допустипо указывать только одну опцию!${NC}"
                    exit 1
                fi

                OPTION=$option
            ;;
        esac
    done

    if [ "$OPTION" == "" ]; then
        echo -e "${RED}Ошибка: необходимо указать опцию!${NC}"
        exit 1
    fi

    args=("$@")
    ARGS=("${args[@]:1}")
}

get_connection_string() {
    local connection_str="$1"

    if ! psql "$connection_str" -c "\q" 2>/dev/null; then
        echo -e "${RED}Ошибка: невозможно подключиться к "${connection_str}"!${NC}"
        exit 1
    fi

    POSTGRES_CONNECTION_STR="$connection_str"
}

get_option() {
    local option="$2"

    case "$option" in
        "-h"|"--help"|"-l"|"--list"|"-d"|"--dir"|"-f"|"--file"|"-b"|"--build")
            OPTION=$option
            return 0
            ;;
    esac

    echo -e "${RED}Ошибка: неизвестная опция "${option}"!${NC}"
    exit 1
}

get_args() {
    args=("$@")
    ARGS=("${args[@]:2}")
}

main() {
    get_connection_string "$@"
    get_option "$@"
    get_args "$@"

    case "$OPTION" in
        "-h"|"--help")
            show_help
        ;;
        "-l"|"--list")
            show_list
        ;;
        "-d"|"--dir")
            load_dir ${POSTGRES_CONNECTION_STR} ${ARGS}
        ;;
        "-f"|"--file")
            load_file ${POSTGRES_CONNECTION_STR} ${ARGS}
        ;;
        "-b"|"--build")
            build ${POSTGRES_CONNECTION_STR}
        ;;
    esac
}

if [ -f ".env" ]; then
    set -a; source .env; set +a
fi

main "$@"
