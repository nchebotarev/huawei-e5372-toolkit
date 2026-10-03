#!/system/bin/busybox sh

BB=/system/bin/busybox
DNSCTL=/data/userdata/zoid-dns/dns_profile.sh
PROFILES=/data/userdata/zoid-dns/profiles

echo "Content-Type: application/json"
echo "Cache-Control: no-store"
echo ""

urldecode() {
    printf '%b' "$(echo "$1" | $BB sed 's/+/ /g;s/%/\\x/g')"
}

json_escape() {
    echo "$1" | $BB sed 's/\\/\\\\/g;s/"/\\"/g'
}

QUERY="${QUERY_STRING:-}"

PROFILE=""
ADBLOCK="0"

OLDIFS="$IFS"
IFS='&'
set -- $QUERY
IFS="$OLDIFS"

for pair in "$@"
do
    key="${pair%%=*}"
    val="${pair#*=}"

    key="$(urldecode "$key")"
    val="$(urldecode "$val")"

    case "$key" in
        profile)
            PROFILE="$val"
            ;;
        adblock)
            ADBLOCK="$val"
            ;;
    esac
done

case "$ADBLOCK" in
    0|1) ;;
    *) ADBLOCK=0 ;;
esac

if [ -z "$PROFILE" ]; then
    echo '{"ok":false,"error":"missing profile"}'
    exit 0
fi

if ! $BB awk -F'|' -v p="$PROFILE" '$1==p {found=1} END{exit !found}' "$PROFILES"
then
    echo '{"ok":false,"error":"unknown profile"}'
    exit 0
fi

"$DNSCTL" apply "$PROFILE" "$ADBLOCK" >/tmp/zoid-dns-cgi.out 2>&1
RC=$?

STATUS="$("$DNSCTL" status 2>/dev/null)"

PROFILE_NOW="$(echo "$STATUS" | $BB sed -n 's/^profile=//p')"
ADBLOCK_NOW="$(echo "$STATUS" | $BB sed -n 's/^adblock=//p')"
DOT_NOW="$(echo "$STATUS" | $BB sed -n 's/^dot=//p')"
STUBBY_NOW="$(echo "$STATUS" | $BB sed -n 's/^stubby=//p')"
DNSMASQ_NOW="$(echo "$STATUS" | $BB sed -n 's/^dnsmasq=//p')"

if [ "$RC" -eq 0 ]; then
    printf '{'
    printf '"ok":true,'
    printf '"profile":"%s",' "$(json_escape "$PROFILE_NOW")"
    printf '"adblock":"%s",' "$(json_escape "$ADBLOCK_NOW")"
    printf '"dot":"%s",' "$(json_escape "$DOT_NOW")"
    printf '"stubby":"%s",' "$(json_escape "$STUBBY_NOW")"
    printf '"dnsmasq":"%s"' "$(json_escape "$DNSMASQ_NOW")"
    printf '}\n'
else
    ERR="$(cat /tmp/zoid-dns-cgi.out 2>/dev/null | $BB tail -n 10 | $BB tr '\n' ' ')"

    printf '{'
    printf '"ok":false,'
    printf '"rc":%s,' "$RC"
    printf '"error":"%s"' "$(json_escape "$ERR")"
    printf '}\n'
fi
