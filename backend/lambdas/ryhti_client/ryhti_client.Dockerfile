FROM public.ecr.aws/lambda/python:3.13

# Install Python dependencies
COPY requirements.txt ${LAMBDA_TASK_ROOT}
RUN pip install -r requirements.txt

# Copy function code
COPY lambdas/ryhti_client/ryhti_client.py ${LAMBDA_TASK_ROOT}

# Copy database python package
COPY database ${LAMBDA_TASK_ROOT}/database

CMD [ "ryhti_client.handler" ]
