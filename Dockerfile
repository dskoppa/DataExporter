# Use the official Python base image with Alpine OS
FROM python:3.9-alpine

# Set the working directory inside the container
WORKDIR /app

# Copy the script and YAML file to the container
COPY data_exporter.py /app/data_exporter.py
COPY tables.yaml /app/tables.yaml

# Install the required dependencies
RUN apk add --no-cache libpq
RUN pip install psycopg2 boto3 pyyaml

# Set the required environment variables
ENV RDS_HOST <your_postgresql_host>
ENV RDS_DB_PORT <your_postgresql_port>
ENV RDS_USERNAME <your_postgresql_username>
ENV RDS_PASSWORD <your_postgresql_password>
ENV RDS_DBNAME <your_postgresql_dbname>
ENV DESTINATION_BUCKET <your_s3_bucket>
ENV DESTINATION_ACCOUNT_ID <your_destination_account_id>
ENV CROSS_ACCOUNT_ROLE_NAME <your_cross_account_role_name>

# Run the script
CMD ["python", "data_exporter.py"]
