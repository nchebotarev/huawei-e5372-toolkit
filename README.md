# Huawei E5372 Toolkit

Архив итоговых пользовательских доработок Huawei E5372: панель **zoid LTE Diagnostics**, CGI, watchdog, DNS-профили, DNS over TLS и кнопка в штатном WebUI. Исходники скопированы с работающего устройства **4 октября 2026 года**; SHA-256 всех 12 файлов пользовательских каталогов сверены с роутером.

Публичный репозиторий: [nchebotarev/huawei-e5372-toolkit](https://github.com/nchebotarev/huawei-e5372-toolkit). Он сохраняет установленную реализацию, включая её ограничения. Инструкция повторной установки составлена по фактическим файлам, но установка на чистое устройство и откат ещё не испытывались.

## Возможности

- LTE-диагностика: оператор, сеть, настроенная маска LTE-диапазонов, PCI, Cell ID, RSSI, RSRP, RSRQ и SINR.
- Состояние соединения, WAN-адреса, батарея, клиенты Wi-Fi, uptime и статистика трафика.
- Обычное обновление каждые 60 секунд; режим диагностики — каждые 3 секунды.
- Выбор из 16 сохранённых DoT-профилей или DNS оператора.
- Восстановление выбранного DNS-профиля после загрузки.
- Проверка наличия установленного TCP-соединения Stubby на порт 853.
- Перезапуск HTTP-сервера через watchdog с ограничением частоты перезапусков.
- Кнопка **zoid LTE Diagnostics** рядом с Refresh на странице информации об устройстве штатного WebUI.

Панель: `http://192.168.8.1:8080/status.html`.

## Состояние при архивировании

| Параметр | Значение и источник |
| --- | --- |
| Модификация прошивки | ValdikSS v1.5.2 из `/system/etc/huawei_mod_version` |
| Версия прошивки | `21.290.23.00.00`, подтверждена `AT+CGMR`; в CGI эта строка задана вручную |
| WebUI | `17.100.19.01.03` из `config/version.xml` |
| Архитектура / BusyBox | `armv7l` / `1.29.3` |
| DNS-профиль | `yandex` |
| Режим DNS | `1`: DoT без DNS-AdBlock |
| AdBlock | Off |
| Anticensorship | Disabled по статусу CGI; файл настройки пуст |
| TTL | `64` из `/data/userdata/fix_ttl` |
| Stubby / dnsmasq / панель | Работают; HTTP и DoT проверены при сборе |
| Fast Boot / USB | В прошлом разговоре: Enabled / Stock; при сборе не перепроверены |
| Remote access / ADB | По экранному меню: Web + Telnet, ADB выключен. Процесс `adbd` работает, но это не подтверждает доступность ADB через USB |
| Telnet | Был доступен для сбора; пароль и сведения для входа в репозиторий не включены |

**Ограничения безопасности:** у панели нет собственной авторизации; CGI изменения DNS вызывается через GET. Сохранённая конфигурация Stubby использует TLS без проверки сертификата (`GETDNS_AUTHENTICATION_NONE`). Подробности: [ограничения](docs/limitations.md).

## Структура

```text
src/
  statusweb/
    status.html
    watchdog.sh
    cgi-bin/{status,dns,dotcheck}.cgi
  zoid-dns/
    dns_profile.sh
    dns_autorun.sh
    profiles
    profile
    adblock
    stubby.original.yml
    stubby.yml
integration/
  oled-autorun.append.sh
  deviceinformation-button.html
config/firmware-reference/
  dnsmasq.conf
  dnsmasq-adblock.conf
config/device-state/
  dns_over_tls
  fix_ttl
  anticensorship
tools/
  patch-webui.py
docs/
  architecture.md
  installation.md
  recovery.md
  diagnostics.md
  dns.md
  webui-button.md
  limitations.md
  source-inventory.md
  source-manifest.json
  verification.md
  publication.md
reference/
  confirmed-html-changes.md
```

## С чего начать

1. [Архитектура и назначение файлов](docs/architecture.md).
2. [DNS-профили и порядок переключения](docs/dns.md).
3. [Установка](docs/installation.md) и [кастомная кнопка](docs/webui-button.md).
4. [Диагностика](docs/diagnostics.md), [восстановление](docs/recovery.md) и [ограничения](docs/limitations.md).
5. [Происхождение файлов](docs/source-inventory.md) и [результаты проверки](docs/verification.md).

## Происхождение

Базовые возможности TTL, DoT, dnsmasq, LTE-диапазонов и расширенного OLED-меню предоставляет модифицированная прошивка. Пользовательская часть — панель, её CGI, watchdog, выбор/восстановление DNS-профиля и кнопка WebUI. Общий upstream: [Huawei LTE routers modifications](https://github.com/Huawei-LTE-routers-mods/README); инструменты сборки: [Huawei Balong modfw kitchen](https://github.com/Huawei-LTE-routers-mods/huawei_balong_modfw_kitchen).

Это не полный образ прошивки. Исполняемые файлы прошивки, дампы, парольные файлы, настройки SIM/Wi-Fi, история чата, живые ответы API и полный штатный WebUI не включены. Кнопка и autorun сохранены как отдельные пользовательские фрагменты, чтобы не заменять целиком системные файлы другой версии. Шаблон Stubby и DNS-конфигурации происходят из установленной прошивки; единая лицензия для всего набора пока не назначена. См. [происхождение и права](docs/source-inventory.md).
