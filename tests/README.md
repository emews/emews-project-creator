# Tests

This directory includes example ME etc. that can be copied into 
workflows projects created by templates in order to test them.

## Sweep ##

1. Run the sweep template using sweep.yaml
2. Copy upf.txt to swift_proj/data 
3. Update the scripts/run_my_model_sweep_workflow.sh with the MODEL_CMD etc. in run_my_model.sh (lines 43 - 48)
4. Copy my_model.py to swift_proj/scripts
5. Run the workflow and check for errors. Should be two instances with no errors in standard err or out. The model
just echos the commmand line passed to it.

## EQPY ##
1. Run the eqpy template using eqpy.yaml.
2. Copy me_config.json to swift_proj/data
3. Copy me.py to swift_proj/python
4. Update the scripts/run_my_model_eqpy_workflow.sh with the MODEL_CMD etc. in run_my_model.sh (lines 43 - 48)
5. Copy my_model.py to swift_proj/scripts (if you haven't already)
6. Run the workflow and check for errors. You should see 0.0;0.0 printed out twice (printed from the ME), and
four instance directories, each containing two runs.

## EQR ##
1. Run the eqr template using eqr.yaml.
2. Copy me_config.R to swift_proj/data.
3. Copy me.R to swift_proj/R
4. Update the scripts/run_my_model_eqpy_workflow.sh with the MODEL_CMD etc. in run_my_model.sh (lines 43 - 48)
5. Copy my_model.py to swift_proj/scripts (if you haven't already)
6. Compile the eqr extension.
7. Run the workflow and check for errors. The R ME will print theconfig file name printed out 
and "0.0;0.0" twice. There should be four instance directories, each containing two runs."
