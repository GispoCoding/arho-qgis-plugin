FROM public.ecr.aws/lambda/python:3.13

# Install Python dependencies
COPY requirements.txt ${LAMBDA_TASK_ROOT}/requirements.txt
RUN pip3 install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

# Copy function code
COPY lambdas/ryhti_client/ryhti_client.py ${LAMBDA_TASK_ROOT}/ryhti_client.py

# Copy database code
COPY \
  database/db_helper.py \
  database/enums.py \
  database/base.py \
  database/codes.py \
  database/models.py \
  ${LAMBDA_TASK_ROOT}/database/

CMD [ "ryhti_client.handler" ]
