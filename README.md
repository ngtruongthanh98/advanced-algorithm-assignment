# Advanced Algorithm Assignment

## How to run:

* Requirements
```
pip install -r requirements.txt
```

* Run
```
python3 run_cplex.py < input.txt
```
The output file will export in output.txt

* Run heuristic

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
