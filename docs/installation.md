# Установка пользовательских доработок

Инструкция составлена по итоговым файлам установленного устройства. Повторная установка на чистый E5372 не испытана. Она предполагает уже установленную совместимую модифицированную прошивку ValdikSS v1.5.2 и WebUI `17.100.19.01.03`; установка базовой прошивки в этот набор не входит.

## Подготовка

Нужны административная консоль, передача файлов на роутер и зависимости из [архитектуры](architecture.md). Пакет содержит только пользовательские файлы и фрагменты интеграции. Для другой версии WebUI/прошивки сначала сверяйте точки интеграции и поведение штатного DNS-скрипта.

Сначала скопируйте на компьютер текущие каталоги `/data/userdata/statusweb` и `/data/userdata/zoid-dns`, файлы `/app/bin/oled_hijack/autorun.sh`, `/app/webroot/WebApp/common/html/deviceinformation.html.gz`, `/data/userdata/dns_over_tls`, их права и владельцев. Отсутствие файла тоже нужно зафиксировать. Резервные копии храните локально вне GitHub.

## Передача файлов

На компьютере подготовьте архив из корня репозитория:

```sh
tar -czf e5372-custom.tar.gz -C src statusweb zoid-dns
```

Передайте его в `/tmp/e5372-custom.tar.gz` удобным способом. Telnet сам не предоставляет команду копирования файлов. Можно использовать локальный сервер HTTP, доступный только в доверенной сети, и `curl` роутера; конкретные адреса зависят от компьютера. Закройте сервер после передачи.

На роутере, после проверки резервных копий и при отсутствии работающей старой панели:

```sh
tar -tzf /tmp/e5372-custom.tar.gz
tar -xzf /tmp/e5372-custom.tar.gz -C /data/userdata
chmod 755 /data/userdata/statusweb /data/userdata/statusweb/cgi-bin /data/userdata/zoid-dns
chmod 755 /data/userdata/statusweb/watchdog.sh /data/userdata/statusweb/cgi-bin/*.cgi
chmod 755 /data/userdata/zoid-dns/dns_profile.sh /data/userdata/zoid-dns/dns_autorun.sh
chmod 644 /data/userdata/statusweb/status.html /data/userdata/zoid-dns/profiles
chmod 644 /data/userdata/zoid-dns/profile /data/userdata/zoid-dns/adblock /data/userdata/zoid-dns/*.yml
```

Эти права — предложенные при архивировании; на исходном устройстве часть файлов имела `666/777`. Содержимое файлов сохраняется без изменения. Shell и CGI должны иметь LF и исполняемый бит. При обновлении уже работающей панели сначала остановите её по [восстановлению](recovery.md).

## Проверка shell

```sh
busybox sh -n /data/userdata/statusweb/watchdog.sh
busybox sh -n /data/userdata/statusweb/cgi-bin/status.cgi
busybox sh -n /data/userdata/statusweb/cgi-bin/dns.cgi
busybox sh -n /data/userdata/statusweb/cgi-bin/dotcheck.cgi
busybox sh -n /data/userdata/zoid-dns/dns_profile.sh
busybox sh -n /data/userdata/zoid-dns/dns_autorun.sh
```

## Запуск и интеграция

Для первого запуска, если watchdog ещё не работает:

```sh
/data/userdata/statusweb/watchdog.sh &
```

Откройте `http://192.168.8.1:8080/status.html`. Сначала проверьте чтение состояния. Для применения архивного Yandex-профиля без AdBlock:

```sh
/data/userdata/zoid-dns/dns_profile.sh apply yandex 0
/data/userdata/zoid-dns/dns_profile.sh status
```

Переключение меняет DNS роутера и кратковременно прерывает разрешение имён. Значение `profile` в архиве само по себе не применяет профиль до запуска команды/autorun.

Добавьте содержимое [`integration/oled-autorun.append.sh`](../integration/oled-autorun.append.sh) в конец `/app/bin/oled_hijack/autorun.sh`, сохранив существующие команды. Перед добавлением проверьте, нет ли уже секций `# zoid LTE status page` и `# zoid DNS profile restore`. Сверьте файл и выполните `busybox sh -n /app/bin/oled_hijack/autorun.sh`. Не заменяйте autorun целиком пользовательским фрагментом.

Установите кнопку по [отдельной инструкции](webui-button.md). При изменении IP роутера обновите также все обращения Huawei API в `status.cgi` и URL кнопки; в исходниках адрес `192.168.8.1` задан явно.

## Приёмка

Проверьте панель, CGI, установленное DoT-соединение и разрешение обычного имени с компьютера. После согласованной перезагрузки повторите проверку процессов, DNS-профиля и кнопки. AdBlock оставьте Off. При архивировании перезагрузка, переустановка и смена DNS-профиля не выполнялись; восстановление после reboot ранее подтверждалось в исходном разговоре.

TTL 64, Fast Boot, USB mode и ADB относятся к базовой прошивке и не устанавливаются этим пакетом. История первоначальной прошивки пока недоступна; не используйте эту инструкцию как руководство записи разделов или восстановления загрузчика.
