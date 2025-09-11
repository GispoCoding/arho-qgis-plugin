FROM public.ecr.aws/lambda/python:3.13

# Install Python dependencies
COPY lambdas/db_manager/requirements.txt ${LAMBDA_TASK_ROOT}
RUN pip install -r requirements.txt

# Copy function code
COPY lambdas/db_manager/db_manager.py ${LAMBDA_TASK_ROOT}

# Copy alembic migrations
COPY alembic.ini ${LAMBDA_TASK_ROOT}/
COPY migrations ${LAMBDA_TASK_ROOT}/migrations

# Copy database python package
COPY database ${LAMBDA_TASK_ROOT}/database

CMD [ "db_manager.handler" ]
