#!/usr/bin/env bash

# power menu via fuzzel

choice=$(printf "lock\nlogout\nsuspend\nreboot\nshutdown" | fuzzel -d -p "power: ")

case "$choice" in
    lock) swaylock ;;
    logout) swaymsg exit ;;
    suspend) systemctl suspend ;;
    reboot) systemctl reboot ;;
    shutdown) systemctl poweroff ;;
esac
