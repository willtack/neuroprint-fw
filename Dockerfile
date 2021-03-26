FROM willtack/wscore-ct-heatmap:0.0.2

MAINTAINER Will Tackett <William.Tackett@pennmedicine.upenn.edu>

# Install basic dependencies
RUN apt-get update && apt-get -y install \
    jq \
    tar \
    zip \
    curl \
    nano \
    build-essential
#RUN rm -f /usr/bin/python && ln -s /usr/bin/python /usr/bin/python3

## Install conda environment
#RUN curl -sSLO https://repo.continuum.io/miniconda/Miniconda3-4.5.11-Linux-x86_64.sh && \
#    bash Miniconda3-4.5.11-Linux-x86_64.sh -b -p /usr/local/miniconda && \
#    rm Miniconda3-4.5.11-Linux-x86_64.sh
#
#ENV PATH=/usr/local/miniconda/bin:$PATH \
#    LANG=C.UTF-8 \
#    LC_ALL=C.UTF-8 \
#    PYTHONNOUSERSITE=1

#RUN conda install -y python=3.7.1 \
#    chmod -R a+rX /usr/local/miniconda; sync && \
#    chmod +x /usr/local/miniconda/bin/*; sync && \
#    conda build purge-all; sync && \
#    conda clean -tipsy && sync

# Install python packages
RUN pip install flywheel-sdk==12.4.0 \
                heudiconv==0.9.0 \
                fw-heudiconv==0.3.3 \
                pybids==0.12.4

# Make directory for flywheel spec (v0)
ENV FLYWHEEL /flywheel/v0
RUN mkdir -p ${FLYWHEEL}
#COPY run ${FLYWHEEL}/run
COPY run.py ${FLYWHEEL}/run.py
COPY manifest.json ${FLYWHEEL}/manifest.json
RUN chmod a+rx ${FLYWHEEL}/*

# Set the entrypoint
ENTRYPOINT ["/flywheel/v0/run.py"]

# ENV preservation for Flywheel Engine
RUN env -u HOSTNAME -u PWD | \
  awk -F = '{ print "export " $1 "=\"" $2 "\"" }' > ${FLYWHEEL}/docker-env.sh

WORKDIR /flywheel/v0