FROM public.ecr.aws/lambda/python:3.13

# Install Python dependencies
COPY requirements.txt ${LAMBDA_TASK_ROOT}/requirements.txt
RUN pip3 install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"



# Copy function code
COPY lambdas/db_manager/db_manager.py ${LAMBDA_TASK_ROOT}/db_manager.py

# Copy database code
COPY database/migrations ${LAMBDA_TASK_ROOT}/migrations
COPY database/alembic.ini ${LAMBDA_TASK_ROOT}/alembic.ini
COPY database/db_helper.py  ${LAMBDA_TASK_ROOT}/db_helper.py
COPY database/enums.py ${LAMBDA_TASK_ROOT}/enums.py
COPY database/base.py ${LAMBDA_TASK_ROOT}/base.py
COPY database/codes.py ${LAMBDA_TASK_ROOT}/codes.py
COPY database/models.py ${LAMBDA_TASK_ROOT}/models.py
COPY database/triggers.py ${LAMBDA_TASK_ROOT}/triggers.py
COPY database/validation.py ${LAMBDA_TASK_ROOT}/validation.py

CMD [ "db_manager.handler" ]
