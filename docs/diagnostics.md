# Диагностика

## Файлы и процессы

```sh
/data/userdata/zoid-dns/dns_profile.sh status
cat /data/userdata/dns_over_tls
ps | grep '[w]atchdog.sh'
ps | grep '[h]ttpd'
ps | grep '[s]tubby'
ps | grep '[d]nsmasq'
netstat -lnt | grep ':8080'
netstat -ntp | grep ':853'
```

В снимке: watchdog, `httpd -f -vv -p 8080 -h /data/userdata/statusweb`, Stubby с пользовательским YAML, dnsmasq с `/etc/dnsmasq.conf`. Прослушивание отображалось как `:::8080`; адрес интерфейса не ограничен параметром запуска.

## HTTP и CGI

С клиента в доверенной сети:

```text
http://192.168.8.1:8080/status.html
http://192.168.8.1:8080/cgi-bin/status.cgi
http://192.168.8.1:8080/cgi-bin/dotcheck.cgi
```

`status.cgi` должен вернуть JSON. Его живой ответ содержит WAN IP, Cell ID и статистику — храните такой вывод локально и обезличивайте перед публикацией. `dotcheck.cgi` создаёт DNS-запрос и может ждать до 10 секунд.

Не открывайте `dns.cgi?profile=...&adblock=...` как обычную диагностику: этот GET меняет DNS-конфигурацию.

С компьютера:

```text
nslookup example.com 192.168.8.1
```

Успешное разрешение имени не доказывает TLS. `established=true` в dotcheck показывает соединение Stubby на 853, но не проверку сертификата или каждый DNS-запрос. Подробности в [DNS](dns.md).

## Логи

```sh
busybox tail -n 30 /tmp/zoid-status-watchdog.log
busybox tail -n 30 /tmp/zoid-status-httpd.log
busybox tail -n 30 /tmp/zoid-dns.log
busybox tail -n 30 /tmp/zoid-dns-autorun.log
busybox tail -n 10 /tmp/zoid-dns-cgi.out
```

Логи в `/tmp` не переживают reboot. Ошибки запуска Stubby нужно искать в `zoid-dns.log`; ошибка применения может попасть в `zoid-dns-cgi.out` и ответ CGI. Не публикуйте необработанные логи, cookies или токены Huawei API.

## Память и дисковое пространство

```sh
busybox free
cat /proc/meminfo
df -h
ls -lh /system/etc/dnsmasq-adblock-list.conf
wc -l /system/etc/dnsmasq-adblock-list.conf
```

При сборе список имел 58 539 строк и около 1,6 МБ на диске. Это не замер RAM. Не включайте AdBlock ради повторения диагностики на этом устройстве.

## После загрузки

Проверьте обе секции `/app/bin/oled_hijack/autorun.sh`, логи watchdog/DNS autorun, фактические процессы и сохранённый профиль. Профиль в файле и зелёный индикатор режима в панели сами по себе не подтверждают работающий upstream.
