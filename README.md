# Data Exporter

This script allows you to export tables from a PostgreSQL database to CSV files and upload them to an Amazon S3 bucket [same or different aws account]. It supports parallel processing using multiple threads to improve performance.

## Prerequisites

Before running the script, make sure you have the following:

- Python 3 installed
- `psycopg2` library for connecting to PostgreSQL (`pip install psycopg2`)
- `boto3` library for interacting with Amazon S3 (`pip install boto3`)
- YAML file (`tables.yaml`) containing the tables and columns to export

Additionally, you need to set up the following environment variables:

- `RDS_HOST`: PostgreSQL database host
- `RDS_DB_PORT`: PostgreSQL database port
- `RDS_USERNAME`: PostgreSQL database username
- `RDS_PASSWORD`: PostgreSQL database password
- `RDS_DBNAME`: PostgreSQL database name
- `DESTINATION_BUCKET`: Amazon S3 bucket name for destination storage
- `DESTINATION_ACCOUNT_ID`: AWS account ID for the destination account
- `CROSS_ACCOUNT_ROLE_NAME`: Name of the cross-account role in the destination account

## Usage

1. Clone this repository or download the script.

2. Install the required Python libraries by running the following command:
    ```
    pip install psycopg2 boto3
    ```

3. Create a YAML file named `tables.yaml` and specify the tables and columns to export in the following format:
    ```yaml
    tables:
      - name: table1
        columns:
          - column1
          - column2
      - name: table2
        columns:
          - column1
          - column2
          - column3
    destination_prefix: optional_prefix
    ```

4. Set the required environment variables mentioned in the Prerequisites section.

5. Run the script:
    ```
    python data_exporter.py
    ```

## Notes

- The script uses a thread pool to process multiple tables in parallel. You can adjust the `max_workers` parameter in the `ThreadPoolExecutor` to control the number of parallel tasks.

- The script appends the exported data to CSV files. If a CSV file with the same name already exists, it will be deleted before exporting the table data.

- The exported CSV files are uploaded to the specified Amazon S3 bucket in the destination account using assumed cross-account role credentials.

- Error handling is implemented to log any errors that occur during the export process. If an error occurs, the script will exit with a non-zero exit code.

- The script logs the progress and number of rows processed for each table.

- For security reasons, make sure to restrict the access permissions to the script and the YAML file.

Feel free to customize the script or YAML file based on your specific requirements.

## License

This script is licensed under the [MIT License](LICENSE).
