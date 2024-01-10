FROM public.ecr.aws/lambda/python:3.12

# Copy function code
COPY db_manager/db_manager.py ${LAMBDA_TASK_ROOT}/db_manager.py
COPY migrations ${LAMBDA_TASK_ROOT}/migrations
COPY alembic.ini ${LAMBDA_TASK_ROOT}/alembic.ini
COPY base.py ${LAMBDA_TASK_ROOT}/base.py
COPY codes.py ${LAMBDA_TASK_ROOT}/codes.py
COPY models.py ${LAMBDA_TASK_ROOT}/models.py

RUN pip3 install  \
    psycopg2-binary \
    alembic \
    --target "${LAMBDA_TASK_ROOT}"

CMD [ "db_manager.handler" ]
