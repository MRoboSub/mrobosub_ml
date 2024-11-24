#!/bin/bash

git reset --hard origin/master
git pull
chmod +x ./*.sh
git config core.filemode false