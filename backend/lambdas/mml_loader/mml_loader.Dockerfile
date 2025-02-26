FROM public.ecr.aws/lambda/python:3.13

# Install Python dependencies
COPY requirements.txt ${LAMBDA_TASK_ROOT}/requirements.txt
RUN pip3 install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

# Copy function code
COPY lambdas/mml_loader/mml_loader.py ${LAMBDA_TASK_ROOT}/mml_loader.py

# Copy database code
COPY \
  database/db_helper.py \
  database/enums.py \
  database/base.py \
  database/codes.py \
  database/models.py \
  ${LAMBDA_TASK_ROOT}/database/


CMD [ "mml_loader.handler" ]
