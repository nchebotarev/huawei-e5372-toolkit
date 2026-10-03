#!/system/bin/busybox sh

BB=/system/bin/busybox
CURL=/system/bin/curl
ATC=/sbin/atc

LD_LIBRARY_PATH=/app/lib:/system/lib:/system/lib/glibc
export LD_LIBRARY_PATH

echo "Content-Type: application/json"
echo "Cache-Control: no-store"
echo ""

xmlval() {
    echo "$1" | $BB sed -n "s:.*<$2>\(.*\)</$2>.*:\1:p" | $BB head -n 1
}

SESTOK="$($CURL -s http://192.168.8.1/api/webserver/SesTokInfo)"
SESSION="$(echo "$SESTOK" | $BB sed -n 's:.*<SesInfo>SessionID=\(.*\)</SesInfo>.*:\1:p')"

STATUS="$($CURL -s -H "Cookie: SessionID=$SESSION" \
    http://192.168.8.1/api/monitoring/status)"

SIGNAL="$($CURL -s -H "Cookie: SessionID=$SESSION" \
    http://192.168.8.1/api/device/signal)"

PLMN="$($CURL -s -H "Cookie: SessionID=$SESSION" \
    http://192.168.8.1/api/net/current-plmn)"

NETMODE="$($CURL -s -H "Cookie: SessionID=$SESSION" \
    http://192.168.8.1/api/net/net-mode)"

LTEBAND="$(xmlval "$NETMODE" LTEBand)"

TRAFFIC="$($CURL -s -H "Cookie: SessionID=$SESSION" \
    http://192.168.8.1/api/monitoring/traffic-statistics)"

MONTH="$($CURL -s -H "Cookie: SessionID=$SESSION" \
    http://192.168.8.1/api/monitoring/month_statistics)"

CERSSI="$($ATC "AT^CERSSI?" 2>/dev/null | $BB sed -n '/\^CERSSI:/p' | $BB head -n 1)"

RSRP=""
RSRQ=""
RADIO_SINR=""

if [ -n "$CERSSI" ]; then
    VALUES="${CERSSI#*:}"
    OLDIFS="$IFS"
    IFS=','
    set -- $VALUES
    IFS="$OLDIFS"

    RSRP="$(echo "$6" | $BB tr -d ' ')"
    RSRQ="$(echo "$7" | $BB tr -d ' ')"
    RADIO_SINR="$(echo "$8" | $BB tr -d ' ')"
fi

RSSI="$(xmlval "$SIGNAL" rssi | $BB sed 's/&amp;gt;=/>=/g;s/&gt;=/>=/g')"
PCI="$(xmlval "$SIGNAL" pci)"
CELLID="$(xmlval "$SIGNAL" cell_id)"

WANIP="$(xmlval "$STATUS" WanIPAddress)"
WANIP6="$(xmlval "$STATUS" WanIPv6Address)"
DNS1="$(xmlval "$STATUS" PrimaryDns)"
DNS2="$(xmlval "$STATUS" SecondaryDns)"
BATTERY="$(xmlval "$STATUS" BatteryPercent)"
WIFI_USERS="$(xmlval "$STATUS" CurrentWifiUser)"
WIFI_MAX="$(xmlval "$STATUS" TotalWifiUser)"
NETWORK="$(xmlval "$STATUS" CurrentNetworkType)"
CONNECTION="$(xmlval "$STATUS" ConnectionStatus)"
ROAMING="$(xmlval "$STATUS" RoamingStatus)"
SIMSTATUS="$(xmlval "$STATUS" SimStatus)"
SERVICE="$(xmlval "$STATUS" ServiceStatus)"

OPERATOR="$(xmlval "$PLMN" Numeric)"
OPERATOR_NAME="$(xmlval "$PLMN" FullName)"
[ -z "$OPERATOR_NAME" ] && OPERATOR_NAME="$(xmlval "$PLMN" ShortName)"

SESSION_TIME="$(xmlval "$TRAFFIC" CurrentConnectTime)"
SESSION_UP="$(xmlval "$TRAFFIC" CurrentUpload)"
SESSION_DOWN="$(xmlval "$TRAFFIC" CurrentDownload)"
UP_RATE="$(xmlval "$TRAFFIC" CurrentUploadRate)"
DOWN_RATE="$(xmlval "$TRAFFIC" CurrentDownloadRate)"
TOTAL_UP="$(xmlval "$TRAFFIC" TotalUpload)"
TOTAL_DOWN="$(xmlval "$TRAFFIC" TotalDownload)"

MONTH_UP="$(xmlval "$MONTH" CurrentMonthUpload)"
MONTH_DOWN="$(xmlval "$MONTH" CurrentMonthDownload)"
MONTH_TIME="$(xmlval "$MONTH" MonthDuration)"
MONTH_CLEAR="$(xmlval "$MONTH" MonthLastClearTime)"

UPSEC="$($BB awk '{print int($1)}' /proc/uptime)"
DAYS=$((UPSEC / 86400))
HOURS=$(((UPSEC % 86400) / 3600))
MINUTES=$(((UPSEC % 3600) / 60))

WEBUI="$($BB sed -n 's:.*<webui>\(.*\)</webui>.*:\1:p' \
    /app/webroot/WebApp/common/config/version.xml | $BB head -n 1)"


DNS_PROFILE="$(cat /data/userdata/zoid-dns/profile 2>/dev/null)"
DNS_ADBLOCK="$(cat /data/userdata/zoid-dns/adblock 2>/dev/null)"
DNS_DOT="$(cat /data/userdata/dns_over_tls 2>/dev/null)"
DNS_ANTICENSORSHIP="$(cat /data/userdata/anticensorship 2>/dev/null)"

if ps | grep '[s]tubby' >/dev/null
then
    DNS_STUBBY="running"
else
    DNS_STUBBY="stopped"
fi

[ -n "$DNS_PROFILE" ] || DNS_PROFILE="stock"
[ "$DNS_ADBLOCK" = "1" ] || DNS_ADBLOCK="0"
[ "$DNS_ANTICENSORSHIP" = "1" ] || DNS_ANTICENSORSHIP="0"

printf '{'
printf '"operator":"%s",' "$OPERATOR"
printf '"operator_name":"%s",' "$OPERATOR_NAME"
printf '"network":"%s",' "$NETWORK"
printf '"lte_band":"%s",' "$LTEBAND"
printf '"connection":"%s",' "$CONNECTION"
printf '"roaming":"%s",' "$ROAMING"
printf '"sim_status":"%s",' "$SIMSTATUS"
printf '"service_status":"%s",' "$SERVICE"
printf '"pci":"%s",' "$PCI"
printf '"cell_id":"%s",' "$CELLID"
printf '"rssi":"%s",' "$RSSI"
printf '"rsrp":"%s",' "$RSRP"
printf '"rsrq":"%s",' "$RSRQ"
printf '"sinr":"%s",' "$RADIO_SINR"
printf '"wan_ip":"%s",' "$WANIP"
printf '"wan_ipv6":"%s",' "$WANIP6"
printf '"dns1":"%s",' "$DNS1"
printf '"dns2":"%s",' "$DNS2"
printf '"battery":"%s",' "$BATTERY"
printf '"wifi_users":"%s",' "$WIFI_USERS"
printf '"wifi_max":"%s",' "$WIFI_MAX"
printf '"uptime":"%sd %sh %sm",' "$DAYS" "$HOURS" "$MINUTES"
printf '"session_time":"%s",' "$SESSION_TIME"
printf '"session_up":"%s",' "$SESSION_UP"
printf '"session_down":"%s",' "$SESSION_DOWN"
printf '"up_rate":"%s",' "$UP_RATE"
printf '"down_rate":"%s",' "$DOWN_RATE"
printf '"total_up":"%s",' "$TOTAL_UP"
printf '"total_down":"%s",' "$TOTAL_DOWN"
printf '"month_up":"%s",' "$MONTH_UP"
printf '"month_down":"%s",' "$MONTH_DOWN"
printf '"month_time":"%s",' "$MONTH_TIME"
printf '"dns_profile":"%s",' "$DNS_PROFILE"
printf '"dns_adblock":"%s",' "$DNS_ADBLOCK"
printf '"dns_dot":"%s",' "$DNS_DOT"
printf '"dns_stubby":"%s",' "$DNS_STUBBY"
printf '"dns_anticensorship":"%s",' "$DNS_ANTICENSORSHIP"
printf '"month_clear":"%s",' "$MONTH_CLEAR"
printf '"firmware":"21.290.23.00.00",'
printf '"webui":"%s"' "$WEBUI"
printf '}\n'
