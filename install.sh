#!/bin/bash

CWD=$(dirname -- "$0")
SCRIPT_DIR=$(dirname -- "$0")

TARGET=/run/media/anitschk/CIRCUITPY

cp $SCRIPT_DIR/README.md $TARGET

rm -f $TARGET/code.py

cp $SCRIPT_DIR/display.py $TARGET
cp $SCRIPT_DIR/main.py $TARGET
cp $SCRIPT_DIR/time_conversion.py $TARGET
cp $SCRIPT_DIR/train_predictor.py $TARGET

cp $SCRIPT_DIR/background.bmp $TARGET
cp $SCRIPT_DIR/trainSprite/train.bmp $TARGET


# This file is ignored by .gitignore because it contains secrets. It must be recreated in the root directory of the project before running the install.sh script.
cp $SCRIPT_DIR/settings.toml $TARGET

cp -r $SCRIPT_DIR/fonts $TARGET/fonts