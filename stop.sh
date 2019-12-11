#! /bin/sh
ps -ax |grep manage.py|awk '{print $1}'|xargs -I {} kill -9 {}
