FROM continuumio/miniconda3
COPY files /files/
SHELL ["conda", "run", "-n", "base", "/bin/bash", "-c"]
RUN mv files/dedalus2 /opt/conda/envs
