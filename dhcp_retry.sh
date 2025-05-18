#!/bin/bash

# Script untuk meminta ulang DHCP jika tidak mendapatkan IP address dalam 5 menit

MAX_WAIT=300  # 5 menit = 300 detik
INTERFACE="eth0"  # Ganti dengan interface jaringan Anda
LOG_FILE="/var/log/dhcp-retry.log"

# Fungsi untuk mengecek IP address
has_ip_address() {
    if ip addr show $INTERFACE | grep -q 'inet '; then
        return 0  # true - memiliki IP
    else
        return 1  # false - tidak memiliki IP
    fi
}

# Fungsi untuk meminta ulang DHCP
renew_dhcp() {
    echo "$(date) - Mencoba memperbarui DHCP pada $INTERFACE..." >> $LOG_FILE
    nmcli connection down "$INTERFACE" && nmcli connection up "$INTERFACE"
    sleep 10  # Beri waktu untuk proses DHCP
}

# Catat waktu mulai
START_TIME=$(date +%s)
TIMEOUT=false
ATTEMPTED_RENEW=false

# Tunggu hingga mendapatkan IP atau timeout
while ! has_ip_address; do
    CURRENT_TIME=$(date +%s)
    ELAPSED_TIME=$((CURRENT_TIME - START_TIME))
    
    if [ $ELAPSED_TIME -ge $MAX_WAIT ]; then
        if ! $ATTEMPTED_RENEW; then
            renew_dhcp
            ATTEMPTED_RENEW=true
            START_TIME=$(date +%s)  # Reset timer setelah mencoba renew
            continue
        else
            TIMEOUT=true
            break
        fi
    fi
    
    sleep 5  # Cek setiap 5 detik
done

# Log hasil
if $TIMEOUT; then
    echo "$(date) - Gagal mendapatkan IP address setelah $MAX_WAIT detik dan 1x percobaan renew DHCP." >> $LOG_FILE
else
    IP_ADDR=$(ip -4 addr show $INTERFACE | grep -oP '(?<=inet\s)\d+(\.\d+){3}')
    echo "$(date) - Berhasil mendapatkan IP: $IP_ADDR setelah $ELAPSED_TIME detik." >> $LOG_FILE
fi