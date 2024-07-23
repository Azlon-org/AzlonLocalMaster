#!/bin/bash

# COMPETITION="titanic"
COMPETITION="predict_future_sales"
START_TIMES=0
END_TIMES=1
STORE_HISTORY=True

python strong_baseline.py \
    --competition $COMPETITION \
    --start_times $START_TIMES \
    --end_times $END_TIMES \
    --store_history $STORE_HISTORY