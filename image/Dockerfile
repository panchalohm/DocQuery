FROM public.ecr.aws/lambda/python:3.13

# Copy requirements.txt
COPY requirements.txt ${LAMBDA_TASK_ROOT}

# Necessary to have SQLlite3 work in Chroma
RUN pip install pysqlite3-binary

# Install specified packages
RUN pip install -r requirements.txt --upgrade

# Local testing
EXPOSE 8000

# Environment Variable - Use to check which version should be used
ENV IS_USING_IMAGE_RUNTIME=True

# Copy all files into ./src
COPY src/* ${LAMBDA_TASK_ROOT}
COPY src/rag_app ${LAMBDA_TASK_ROOT}/rag_app
COPY src/data/chroma ${LAMBDA_TASK_ROOT}/data/chroma
