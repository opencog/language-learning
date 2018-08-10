FROM continuumio/miniconda3

RUN useradd -ms /bin/bash  opencog-ull

ENV PYTHONUNBUFFERED 1

ADD https://github.com/singnet/language-learning/raw/master/environment.yml /tmp/environment.yml

WORKDIR /tmp

RUN conda update -y -q conda && conda env create -f environment.yml -q
RUN chown -R opencog-ull:opencog-ull /opt/conda

USER opencog-ull

CMD /bin/bash

WORKDIR /home/opencog-ull

ONBUILD USER root