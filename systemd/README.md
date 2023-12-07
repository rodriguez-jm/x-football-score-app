# Run api-football-api with systemd timers
They are much easier to use and troubleshoot than cron jobs.

Read more at: [Working with systemd Timers](https://documentation.suse.com/smart/systems-management/html/systemd-working-with-timers/index.html)

## Create x-clean and x-main services and timers
1) Copy services and timers to /etc/systemd/system/
```
# X-clean
$ cp systemd/x-clean/x-clean.* /etc/systemd/systemd/

# X-main
$ cp systemd/x-main/x-main.* /etc/systemd/systemd/
```
2) Start timers!
```
# Reload daemon
$ sudo systemctl daemon-reload

# Start timers
$ sudo systemctl start x-clean.timer
$ sudo systemctl start x-main.timer

# Enable timers
$ sudo systemctl enable x-clean.timer
$ sudo systemctl enable x-main.timer

```
## Monitor timers
```
$ sudo systemctl status x-main.timer
$ sudo systemctl status x-clean.timer

```
## See service and timer logs
```
$ sudo journalctl -u  x-main.*
$ sudo journalctl -u  x-clean.*
```
## Check syntax of service and timer files
```
# No output means your file is valid
$ systemd-analyze verify filename
```
## Check validity of calender entry
```
$ systemd-analyze calendar "Mon..Fri 10:00"

  Original form: Mon..Fri 10:00
Normalized form: Mon..Fri *-*-* 10:00:00
    Next elapse: Thu 2023-12-07 10:00:00 PST
       (in UTC): Thu 2023-12-07 18:00:00 UTC
       From now: 11h left
```
