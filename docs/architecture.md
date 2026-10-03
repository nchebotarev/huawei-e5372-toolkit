# Архитектура

```text
Штатный WebUI → deviceinformation.html.gz → кнопка zoid LTE Diagnostics
                                                   ↓
                           http://192.168.8.1:8080/status.html
                                                   ↓
                 status.cgi      dns.cgi       dotcheck.cgi
                      ↓              ↓                ↓
               Huawei API + AT   dns_profile.sh   nslookup + netstat
                                     ↓
                            /etc/dns_over_tls.sh
                                     ↓
                        dnsmasq :5353 → Stubby :5354 → DoT :853

/system/etc/autorun.sh → /app/bin/oled_hijack/autorun.sh
                              ├─ statusweb/watchdog.sh → busybox httpd :8080
                              └─ zoid-dns/dns_autorun.sh → восстановление DNS
```

## Назначение файлов

| Путь на устройстве | Назначение |
| --- | --- |
| `/data/userdata/statusweb/status.html` | Интерфейс панели, автоматическое обновление и управление DNS |
| `/data/userdata/statusweb/cgi-bin/status.cgi` | Чтение Huawei API, `AT^CERSSI?`, статистики и файлов состояния |
| `/data/userdata/statusweb/cgi-bin/dns.cgi` | Разбор GET-параметров, проверка профиля, вызов переключения DNS |
| `/data/userdata/statusweb/cgi-bin/dotcheck.cgi` | Запрос уникального имени и поиск установленного соединения Stubby на порт 853 |
| `/data/userdata/statusweb/watchdog.sh` | Запуск `busybox httpd -f -vv -p 8080`; повторный запуск после выхода |
| `/data/userdata/zoid-dns/dns_profile.sh` | Генерация Stubby YAML, остановка/запуск DNS, сохранение профиля |
| `/data/userdata/zoid-dns/dns_autorun.sh` | Ожидание штатного DNS и восстановление сохранённого профиля |
| `/data/userdata/zoid-dns/profiles` | Таблица профилей `id|название|IP через запятую|TLS hostname` |
| `/data/userdata/zoid-dns/profile` | Сохранённый идентификатор профиля |
| `/data/userdata/zoid-dns/adblock` | Пожелание DNS-AdBlock: `0` или `1` |
| `/data/userdata/zoid-dns/stubby.original.yml` | Шаблон: генератор сохраняет часть до `upstream_recursive_servers:` включительно |
| `/data/userdata/zoid-dns/stubby.yml` | Итоговый YAML выбранного профиля |
| `/data/userdata/dns_over_tls` | Штатный режим: `0` — Off, `1` — DoT, `2` — DoT + AdBlock |
| `/app/bin/oled_hijack/autorun.sh` | Две добавленные секции запуска watchdog и восстановления DNS |
| `/app/webroot/WebApp/common/html/deviceinformation.html.gz` | Сжатая страница со встроенной кнопкой |
| `/etc/dns_over_tls.sh` | Штатный запуск DNS и настройка перенаправления запросов |
| `/etc/dnsmasq.conf` | DNS без AdBlock, слушает `br0:5353`, upstream `127.0.0.1#5354` |
| `/etc/dnsmasq-adblock.conf` | Аналогичный стек с подключением списка блокировки |

`/etc` является ссылкой на `/system/etc`. При сборе `/system` был смонтирован read-only, `/app` и `/app/webroot` — read-write. Пользовательские доработки не требуют записи в `/system`.

## Watchdog

HTTP-сервер работает в foreground. Watchdog возобновляет его через 5 секунд после выхода. После более чем трёх выходов в окне 600 секунд watchdog прекращает работу. Окно отсчитывается от `window_start`, это не скользящий счётчик.

Если HTTP-лог превышает 128 КиБ, перед очередным запуском httpd оставляются последние 64 КиБ. Во время длительной работы httpd обрезка не выполняется. Собственный лог watchdog не имеет ограничения размера.

## Зависимости

Нужны BusyBox с `httpd`, `sh`, `awk`, `sed`, `grep`, `nslookup` и другими стандартными applets, Huawei API на `192.168.8.1`, `/system/bin/curl`, `/sbin/atc`, Stubby/getdns, dnsmasq, `netstat -ntp`, `pkill`, библиотечные пути `/app/lib:/system/lib:/system/lib/glibc` и штатный `/etc/dns_over_tls.sh`.

Панель сама не задаёт TTL и LTE-диапазоны. Она показывает настроенную маску диапазонов, а не измеряет текущий LTE band/частоту.
