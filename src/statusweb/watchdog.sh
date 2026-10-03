#!/system/bin/busybox sh

LOG=/tmp/zoid-status-watchdog.log
HTTPLOG=/tmp/zoid-status-httpd.log

MAX_RESTARTS=3
WINDOW=600
MAX_HTTP_LOG=131072

restart_count=0
window_start=0

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') $*" >> "$LOG"
}

trim_http_log() {
    if [ -f "$HTTPLOG" ]; then
        size=$(busybox wc -c < "$HTTPLOG")

        if [ "$size" -gt "$MAX_HTTP_LOG" ]; then
            busybox tail -c 65536 "$HTTPLOG" > "$HTTPLOG.tmp"
            mv "$HTTPLOG.tmp" "$HTTPLOG"
            log "httpd log trimmed to 64 KB"
        fi
    fi
}

log "Supervisor started"

while true
do
    trim_http_log

    now=$(date +%s)

    if [ "$window_start" -eq 0 ] || [ $((now - window_start)) -gt "$WINDOW" ]; then
        window_start=$now
        restart_count=0
    fi

    log "Starting httpd, free_mem_kb=$(busybox free | busybox awk '/Mem:/{print $4}')"

    busybox httpd -f -vv \
        -p 8080 \
        -h /data/userdata/statusweb \
        >> "$HTTPLOG" 2>&1

    rc=$?

    log "httpd exited rc=$rc"

    restart_count=$((restart_count + 1))

    if [ "$restart_count" -gt "$MAX_RESTARTS" ]; then
        log "ERROR: more than $MAX_RESTARTS httpd exits within $WINDOW seconds, supervisor stopped"
        exit 1
    fi

    log "Restarting httpd in 5 seconds ($restart_count/$MAX_RESTARTS)"
    sleep 5
done
