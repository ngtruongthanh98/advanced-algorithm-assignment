# Advanced Algorithm Assignment

## How to run

* Requirements
```
pip install -r requirements.txt
```

* Run **cplex**
To show all available options
```
python3 run_cplex.py -h
python3 run_cplex_general.py -h # For more general running cplex
```
Example command for running a single testcase by cplex
```
python3 run_cplex.py \
    -in input.txt \
    -ol output_log.txt \
    -of output_fig.png 
```
Example command for running many testcases by cplex
```
python3 run_cplex_general.py \
    -st 1 \
    -et 60 \
    -if input \
    -olf cplex_result \
    -off cplex_fig
```

* Run **heuristic**

To show all available options
```
python3 bap.py -h
```

Example command
```
python3 bap.py \
    --log_res true \
    --res_dest "custom-result-dir" \
    --log_fig true \
    --figs_dest "custom-fig-dir" \
    --start_test 1 \
    --end_test 20 \
    --with_heuristic
```

Link report: https://www.overleaf.com/project/6358d9922a66754f5963bc56
Link slide: https://www.overleaf.com/project/636bb3773357b950facf6227
