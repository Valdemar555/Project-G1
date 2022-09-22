FROM python:latest
EXPOSE 5000
COPY . /black_mamba_project_final

WORKDIR /black_mamba_project_final

RUN pip install -r /black_mamba_project_final/requirements.txt
#RUN flask db init
#RUN flask db migrate

ENTRYPOINT ["python"]
CMD ["app.py", "--host=0.0.0.0"]