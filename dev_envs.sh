

export VIRTUALENV_NAMESPACE=.maestro
export HOSTNAME=$(hostname).$(dnsdomainname)

# Paths
export MAESTRO_PATH=$PWD
export PYTHONPATH=`pwd`:$PYTHONPATH
export PATH=`pwd`/scripts:$PATH



export PILOT_SERVER_PORT=5003
#export PILOT_SERVER_HOST="http://${HOSTNAME}:${PILOT_SERVER_PORT}"
export PILOT_SERVER_HOST="http://maestro-server.lps.ufrj.br:${PILOT_SERVER_PORT}"



echo "=================================================================================="
echo "PILOT_SERVER_HOST       = ${PILOT_SERVER_HOST}"
echo "=================================================================================="
