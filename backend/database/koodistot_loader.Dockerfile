FROM public.ecr.aws/lambda/python:3.12

# Copy function code
COPY database/koodistot_loader/koodistot_loader.py ${LAMBDA_TASK_ROOT}/koodistot_loader.py
COPY database/base.py ${LAMBDA_TASK_ROOT}/base.py
COPY database/codes.py ${LAMBDA_TASK_ROOT}/codes.py
COPY database/models.py ${LAMBDA_TASK_ROOT}/models.py
COPY requirements.txt ${LAMBDA_TASK_ROOT}/requirements.txt

RUN pip3 install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

CMD [ "koodistot_loader.handler" ]
