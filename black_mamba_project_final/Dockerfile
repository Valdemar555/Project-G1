FROM python:latest

COPY . /black_mamba_project_final

WORKDIR /black_mamba_project_final

RUN pip install -r /HW_3/requirements.txt
RUN flask db init
RUN flask bd migrate

ENTRYPOINT ["python"]
CMD ["app.py"]