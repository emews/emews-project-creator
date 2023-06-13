{% include 'common/submission_prefix.j2' %}
{% include 'common/eqsql_submission_prefix.j2' %}

{% include 'common/submission_job_exports.j2' %}

{% include 'common/submission_r_paths.j2' %}

# EQ/Py location
EQSQL={{cookiecutter.eqsql_dir}}
export PYTHONPATH=$EMEWS_PROJECT_ROOT/python:$EQSQL

# TODO: If Python cannot be found or there are "Cannot find 
# X package" type errors then these two environment variables
# will need to be uncommented and set correctly.
# export PYTHONHOME=/path/to/python

# Resident task workers and ranks
export TURBINE_RESIDENT_WORK_WORKERS=1
export RESIDENT_WORK_RANK=$(( PROCS - 2 ))

# TODO: Set MACHINE to your schedule type (e.g. pbs, slurm, cobalt etc.),
# or empty for an immediate non-queued unscheduled run
MACHINE=""

if [ -n "$MACHINE" ]; then
  MACHINE="-m $MACHINE"
else
  echo "Logging output to $TURBINE_OUTPUT/output.txt"
  # Redirect stdout and stderr to output.txt
  # if running without a scheduler.
  exec &> "$TURBINE_OUTPUT/output.txt"
fi

EMEWS_EXT=$EMEWS_PROJECT_ROOT/ext/emews

export DB_HOST=$CFG_DB_HOST
export DB_USER=$CFG_DB_USER
export DB_PORT=${CFG_DB_PORT:-}
export DB_NAME=$CFG_DB_NAME

CMD_LINE_ARGS="--trials=$CFG_TRIALS --task_type=$CFG_TASK_TYPE --batch_size=$CFG_BATCH_SIZE "
CMD_LINE_ARGS+="--batch_threshold=$CFG_BATCH_THRESHOLD --worker_pool_id=$CFG_POOL_ID $*"

{% include 'common/submission_args.j2' %}
{% include 'common/eqsql_submission.j2' %}
