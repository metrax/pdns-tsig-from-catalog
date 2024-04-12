#!/bin/bash
cp pdns-tsig-from-catalog.service pdns-tsig-from-catalog.timer /etc/systemd/system/
systemctl daemon-reload
systemctl enable pdns-tsig-from-catalog.timer
systemctl start pdns-tsig-from-catalog.timer
