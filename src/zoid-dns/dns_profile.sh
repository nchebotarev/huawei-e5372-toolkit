#!/system/bin/busybox sh

BB=/system/bin/busybox
BASE=/data/userdata/zoid-dns
PROFILES=$BASE/profiles
PROFILE_FILE=$BASE/profile
ADBLOCK_FILE=$BASE/adblock
ORIGINAL=$BASE/stubby.original.yml
CONFIG=$BASE/stubby.yml
LOG=/tmp/zoid-dns.log

LD_LIBRARY_PATH=/app/lib:/system/lib:/system/lib/glibc
export LD_LIBRARY_PATH

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') $*" >> "$LOG"
}

get_profile() {
    cat "$PROFILE_FILE" 2>/dev/null
}

get_adblock() {
    v=$(cat "$ADBLOCK_FILE" 2>/dev/null)
    [ "$v" = "1" ] && echo 1 || echo 0
}

find_profile() {
    $BB awk -F'|' -v p="$1" '$1==p {print; exit}' "$PROFILES"
}

generate_config() {
    profile="$1"
    entry="$(find_profile "$profile")"

    [ -z "$entry" ] && return 1

    OLDIFS="$IFS"
    IFS='|'
    set -- $entry
    IFS="$OLDIFS"

    ips="$3"
    auth="$4"

    $BB awk '
        /^upstream_recursive_servers:/ {
            print
            exit
        }
        { print }
    ' "$ORIGINAL" > "$CONFIG"

    OLDIFS="$IFS"
    IFS=','
    set -- $ips
    IFS="$OLDIFS"

    for ip in "$@"
    do
        [ -z "$ip" ] && continue
        echo "  - address_data: $ip" >> "$CONFIG"
        [ -n "$auth" ] && echo "    tls_auth_name: \"$auth\"" >> "$CONFIG"
    done
}

stop_dns_stack() {
    log "Stopping current DNS stack"

    /etc/dns_over_tls.sh 0 >> "$LOG" 2>&1

    pkill stubby 2>/dev/null
    pkill dnsmasq 2>/dev/null

    sleep 1
}

start_stock_dns() {
    mode="$1"

    log "Starting stock DNS stack mode=$mode"

    echo "$mode" > /data/userdata/dns_over_tls
    /etc/dns_over_tls.sh "$mode" >> "$LOG" 2>&1

    sleep 1
}

start_custom_stubby() {
    log "Replacing stock Stubby with custom config"

    pkill stubby 2>/dev/null
    sleep 1

    stubby -C "$CONFIG" -g >> "$LOG" 2>&1 &

    sleep 2

    ps | grep '[s]tubby' >/dev/null
}

restart_dns() {
    profile="$1"
    adblock="$2"

    [ "$adblock" = "1" ] || adblock=0

    if [ "$profile" = "operator" ]; then
        stop_dns_stack

        echo 0 > /data/userdata/dns_over_tls
        echo operator > "$PROFILE_FILE"
        echo "$adblock" > "$ADBLOCK_FILE"

        log "SUCCESS operator DNS enabled"
        return 0
    fi

    generate_config "$profile" || {
        log "ERROR unknown profile: $profile"
        return 2
    }

    mode=1
    [ "$adblock" = "1" ] && mode=2

    stop_dns_stack
    start_stock_dns "$mode"

    start_custom_stubby || {
        log "ERROR custom Stubby failed to start"
        return 3
    }

    echo "$profile" > "$PROFILE_FILE"
    echo "$adblock" > "$ADBLOCK_FILE"

    log "SUCCESS profile=$profile adblock=$adblock"
    return 0
}

case "$1" in
    apply)
        profile="$2"
        adblock="$3"
        restart_dns "$profile" "$adblock"
        ;;

    status)
        echo "profile=$(get_profile)"
        echo "adblock=$(get_adblock)"
        echo "dot=$(cat /data/userdata/dns_over_tls 2>/dev/null)"

        if ps | grep '[s]tubby' >/dev/null
        then
            echo "stubby=running"
        else
            echo "stubby=stopped"
        fi

        if ps | grep '[d]nsmasq' >/dev/null
        then
            echo "dnsmasq=running"
        else
            echo "dnsmasq=stopped"
        fi
        ;;

    *)
        echo "Usage:"
        echo "  $0 status"
        echo "  $0 apply PROFILE 0|1"
        exit 1
        ;;
esac
