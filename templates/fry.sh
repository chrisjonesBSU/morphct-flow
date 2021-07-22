{% extends "base_script.sh" %}
{% block header %}
{% set gpus = operations|map(attribute='directives.ngpu')|sum %}
{% set cpus = operations|map(attribute='directives.n')|sum %}
{% set nodes = operations|map(attribute='directives.N')|sum %}
#!/bin/bash
#SBATCH --job-name="{{ id }}"
{% if partition %}
#SBATCH --partition={{ partition }}
{% endif %}
{% if nodelist %}
#SBATCH --nodelist={{ nodelist }}
{% endif %}
{% if walltime %}
#SBATCH -t {{ 48|format_timedelta }}
{% endif %}
{% if gpus %}
#SBATCH --gres gpu:{{ gpus }}
{% endif %}
{% if cpus %}
#SBATCH -n {{ cpus }}
{% endif %}
{% if nodes %}
#SBATCH -N {{ nodes }}
{% endif %}
#SBATCH --output=workspace/{{operations[0]._jobs[0]}}/job_%j.o
#SBATCH --error=workspace/{{operations[0]._jobs[0]}}/job_%j.e
#SBATCH --exclusive
{% block tasks %}
#SBATCH --ntasks={{ np_global }}
{% endblock %}
{% endblock %}
