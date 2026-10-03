#!/system/bin/busybox sh

BB=/system/bin/busybox

echo "Content-Type: application/json"
echo "Cache-Control: no-store"
echo ""

TS="$(date +%s)"
TESTNAME="zoid-${TS}.google.com"

# Unique name forces a real upstream DNS request.
$BB nslookup "$TESTNAME" 127.0.0.1 >/dev/null 2>&1 &

i=0

while [ "$i" -lt 10 ]
do
    LINE="$(netstat -ntp 2>/dev/null | \
        $BB grep ':853' | \
        $BB grep ESTABLISHED | \
        $BB grep '/stubby' | \
        $BB head -n 1)"

    if [ -n "$LINE" ]
    then
        PEER="$(echo "$LINE" | $BB awk '{print $5}')"

        printf '{"established":true,"peer":"%s"}\n' "$PEER"
        exit 0
    fi

    sleep 1
    i=$((i + 1))
done

echo '{"established":false,"peer":""}'
