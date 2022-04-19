#!/bin/bash

# echo "Today is just great"

python -c 'import app; print app.db.create_all()'
