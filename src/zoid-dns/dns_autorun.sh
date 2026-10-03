#!/system/bin/busybox sh

LOG=/tmp/zoid-dns-autorun.log
DNSCTL=/data/userdata/zoid-dns/dns_profile.sh
PROFILE_FILE=/data/userdata/zoid-dns/profile
ADBLOCK_FILE=/data/userdata/zoid-dns/adblock

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') $*" >> "$LOG"
}

log "DNS autorun started"

# Wait until Huawei stock DNS stack has initialized.
i=0
while [ "$i" -lt 30 ]
do
    if ps | grep '[d]nsmasq' >/dev/null || ps | grep '[s]tubby' >/dev/null
    then
        log "Stock DNS stack detected"
        break
    fi

    sleep 2
    i=$((i + 1))
done

# Give the firmware a little extra time to finish initialization.
sleep 5

PROFILE="$(cat "$PROFILE_FILE" 2>/dev/null)"
ADBLOCK="$(cat "$ADBLOCK_FILE" 2>/dev/null)"

[ -n "$PROFILE" ] || PROFILE="stock"
[ "$ADBLOCK" = "1" ] || ADBLOCK=0

log "Saved profile=$PROFILE adblock=$ADBLOCK"

case "$PROFILE" in
    stock)
        log "Stock profile selected, nothing to restore"
        exit 0
        ;;
    *)
        "$DNSCTL" apply "$PROFILE" "$ADBLOCK" >> "$LOG" 2>&1
        RC=$?
        log "Restore finished rc=$RC"
        exit "$RC"
        ;;
esac
