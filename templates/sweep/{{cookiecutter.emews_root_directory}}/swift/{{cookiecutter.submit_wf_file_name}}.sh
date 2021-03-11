{% include 'common/submission_prefix.j2' %}
echo "UPF FILE:              $CFG_UPF"
echo "--------------------------"


{% include 'common/submission_job_exports.j2' %}

# Copies UPF file to experiment directory
U_UPF_FILE=$EMEWS_PROJECT_ROOT/$CFG_UPF
UPF_FILE=$TURBINE_OUTPUT/upf.txt
cp $U_UPF_FILE $UPF_FILE

CMD_LINE_ARGS="$* -f=$UPF_FILE "
{% include 'common/submission_args.j2' %}
