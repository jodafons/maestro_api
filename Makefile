
all : build_local


build_local:
	virtualenv -p python ${VIRTUALENV_NAMESPACE}
	source ${MAESTRO_PATH}/${VIRTUALENV_NAMESPACE}/bin/activate && pip install -r requirements.txt && which python


