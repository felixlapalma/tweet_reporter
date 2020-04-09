FROM python:3.8-slim-buster

############## PIP #################################
# Add environment file
ADD requirements.txt /tmp/requirements.txt
# update base env
RUN pip install -r /tmp/requirements.txt 
############## PIP  #################################


############## DIRS #######################################
# Setup DATA_DIR directory
ENV DATA_DIR="/opt/data"
# Make
RUN mkdir $DATA_DIR

# Setup SRC_DIR directory
ENV SRC_DIR="/opt/src"
# Make
RUN mkdir $SRC_DIR
############## VOLS #######################################










