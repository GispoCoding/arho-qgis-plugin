FROM public.ecr.aws/lambda/python:3.13

# Install Python dependencies
COPY requirements.txt ${LAMBDA_TASK_ROOT}
RUN pip install -r requirements.txt

# Copy function code
COPY lambdas/mml_loader/mml_loader.py ${LAMBDA_TASK_ROOT}

# Copy database python package
COPY database ${LAMBDA_TASK_ROOT}/database


CMD [ "mml_loader.handler" ]
