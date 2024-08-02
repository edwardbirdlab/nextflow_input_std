FROM python:3.11.5
LABEL authors="edwardbird"

WORKDIR /work
COPY requirements.txt .
RUN pip install -r requirements.txt

WORKDIR /work
# COPY data_validator.py .
RUN wget -O data_validator.py https://raw.githubusercontent.com/edwardbirdlab/nextflow_input_std/main/data_validator.py
RUN chmod +x data_validator.py

ENV PATH="/work:${PATH}"

ENTRYPOINT ["python", "/work/data_validator.py"]