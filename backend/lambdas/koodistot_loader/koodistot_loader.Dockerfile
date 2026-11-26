FROM public.ecr.aws/lambda/python:3.13

# Install Python dependencies
COPY lambdas/koodistot_loader/requirements.txt ${LAMBDA_TASK_ROOT}
RUN pip install -r requirements.txt

# Copy function code
COPY lambdas/koodistot_loader/koodistot_loader.py ${LAMBDA_TASK_ROOT}

# Copy database python package
COPY database ${LAMBDA_TASK_ROOT}/database

CMD [ "koodistot_loader.handler" ]
