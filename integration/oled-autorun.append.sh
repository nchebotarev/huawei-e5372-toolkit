# zoid LTE status page
ps | grep '[w]atchdog.sh' >/dev/null || \
/data/userdata/statusweb/watchdog.sh &

# zoid DNS profile restore
ps | grep '[d]ns_autorun.sh' >/dev/null || \
/data/userdata/zoid-dns/dns_autorun.sh &
