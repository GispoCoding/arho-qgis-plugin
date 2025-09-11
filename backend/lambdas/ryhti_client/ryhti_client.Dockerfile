FROM public.ecr.aws/lambda/python:3.13

RUN dnf install -y git && \
    dnf clean all && \
    rm -rf /var/cache/dnf

# Install Python dependencies
COPY lambdas/ryhti_client/requirements.txt ${LAMBDA_TASK_ROOT}
RUN pip install -r requirements.txt

# Copy function code
COPY lambdas/ryhti_client/lambda_function.py ${LAMBDA_TASK_ROOT}
COPY lambdas/ryhti_client/ryhti_client ${LAMBDA_TASK_ROOT}/ryhti_client

# Copy database python package
COPY database ${LAMBDA_TASK_ROOT}/database

CMD [ "lambda_function.handler" ]
