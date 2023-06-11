import logging
import psycopg2
import boto3
import yaml
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor

# Set up logging
logging.basicConfig(level=logging.INFO)

# Load the tables and columns from the YAML file
try:
    with open('tables.yaml', 'r') as f:
        tables_data = yaml.safe_load(f)
        tables = tables_data['tables']
        destination_prefix = tables_data.get('destination_prefix', '')
    logging.info('Loaded tables.yaml successfully.')
except Exception as e:
    logging.error(f'Error loading tables.yaml: {str(e)}')
    sys.exit(1)

# Set up the S3 client with AWS credentials
s3_client = boto3.client('s3')

# Retrieve the values from environment variables
HOST = os.environ.get('RDS_HOST')
PORT = int(os.environ.get('RDS_DB_PORT'))
USERNAME = os.environ.get('RDS_USERNAME')
PASSWORD = os.environ.get('RDS_PASSWORD')
DBNAME = os.environ.get('RDS_DBNAME')
DESTINATION_BUCKET = os.environ.get('DESTINATION_BUCKET')
DESTINATION_ACCOUNT_ID = os.environ.get('DESTINATION_ACCOUNT_ID')
CROSS_ACCOUNT_ROLE_NAME = os.environ.get('CROSS_ACCOUNT_ROLE_NAME')

# Set a flag to track if any errors occur
error_occurred = False

# Function to process a batch of rows
def process_batch(name, columns, batch_size, offset):
    try:
        # Connect to the database and execute the query
        conn = psycopg2.connect(
            host=HOST,
            port=PORT,
            user=USERNAME,
            password=PASSWORD,
            dbname=DBNAME
        )
        cur = conn.cursor()

        query = f"SELECT {columns} FROM {name} LIMIT {batch_size} OFFSET {offset}"
        cur.execute(query)
        rows = cur.fetchall()

        # Process the batch of rows
        csv_rows = []
        for row in rows:
            row = [str(col) if col is not None else '' for col in row]
            escaped_row = []
            for col in row:
                if ',' in col:
                    escaped_row.append(f'"{col}"')
                else:
                    escaped_row.append(col)
            csv_rows.append(','.join(' '.join(col.split()) if col else '' for col in escaped_row))
        csv_data = '\n'.join(csv_rows)


        # Append to the CSV file
        with open(f'{name}.csv', 'a') as f:
            f.write(csv_data + '\n')

        # Close the database connection
        cur.close()
        conn.close()

        return len(rows)

    except Exception as e:
        logging.error(f'An error occurred while exporting table {name}: {str(e)}')
        return 0


# Loop through the tables and export them to CSV
for table in tables:
    name = table['name']
    columns = ','.join(table['columns'])
    batch_size = 150000

    logging.info(f'Exporting table {name}...')

    # Delete the earlier CSV file from storage if it exists
    if os.path.exists(f'{name}.csv'):
        os.remove(f'{name}.csv')

    try:
        # Connect to the database and execute the query
        conn = psycopg2.connect(
            host=HOST,
            port=PORT,
            user=USERNAME,
            password=PASSWORD,
            dbname=DBNAME
        )
        cur = conn.cursor()

        # Get the total count of rows in the table
        cur.execute(f"SELECT COUNT(*) FROM {name}")
        total_rows = cur.fetchone()[0]
        logging.info(f'Total rows in {name}: {total_rows}')

        # Set up a thread pool for parallel processing
        executor = ThreadPoolExecutor(max_workers=10)

        # Process the rows in parallel using multiple threads
        offset = 0
        rows_processed = 0
        while offset < total_rows:
            futures = []

            # Submit parallel tasks for processing batches
            for _ in range(3):  # Number of parallel tasks
                future = executor.submit(process_batch, name, columns, batch_size, offset)
                futures.append(future)
                offset += batch_size

            # Wait for the parallel tasks to complete
            for future in futures:
                rows_processed += future.result()

            logging.info(f'Processed {rows_processed}/{total_rows} rows in {name}...')

        # Close the database connection
        cur.close()
        conn.close()

        # Upload the CSV file to S3 in the destination account
        logging.info(f'Uploading {name}.csv to S3 in the destination account...')

        try:
            # Assume the aws account IAM role in the destination account
            sts_client = boto3.client('sts')
            role_arn = f'arn:aws:iam::{DESTINATION_ACCOUNT_ID}:role/{CROSS_ACCOUNT_ROLE_NAME}'  # aws account role for the destination account
            assumed_role = sts_client.assume_role(
                RoleArn=role_arn,
                RoleSessionName='AssumeRoleSession'
            )
            credentials = assumed_role['Credentials']

            # Create a new S3 client with the assumed role credentials
            s3_client_dest = boto3.client(
                's3',
                aws_access_key_id=credentials['AccessKeyId'],
                aws_secret_access_key=credentials['SecretAccessKey'],
                aws_session_token=credentials['SessionToken']
            )

            # Upload the CSV file to the destination S3 bucket
            destination_key = f'{destination_prefix}/{name}.csv'
            s3_client_dest.upload_file(f'{name}.csv', DESTINATION_BUCKET, destination_key)

            logging.info(f'{name}.csv uploaded successfully.')
        except Exception as e:
            logging.error(f'An error occurred while uploading {name}.csv to S3 in the destination account: {str(e)}')
            error_occurred = True

        # Log the number of rows processed for the table
        logging.info(f'Number of rows processed for table {name}: {rows_processed}')

    except Exception as e:
        logging.error(f'An error occurred while exporting table {name}: {str(e)}')
        error_occurred = True
    finally:
        # Close the database connection
        if cur:
            cur.close()
        if conn:
            conn.close()

# Check if any errors occurred and exit with appropriate code
if error_occurred:
    logging.error('Export failed.')
    sys.exit(1)
else:
    logging.info('Export complete.')
    sys.exit(0)
