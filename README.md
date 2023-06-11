Certainly! Here's an updated version of the README.md file for running the code with Alpine OS using Docker:

# Data Exporter

This script allows you to export tables from a PostgreSQL database to CSV files and upload them to an Amazon S3 bucket. It supports parallel processing using multiple threads to improve performance.

## Prerequisites

Before running the script, make sure you have Docker installed on your system. You can download Docker from the official website: [https://www.docker.com](https://www.docker.com)

## Usage

1. Clone this repository or download the script and the `tables.yaml` file.

2. Open the `tables.yaml` file and specify the tables and columns to export in the following format:
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
    Eg.
    ```
    destination_prefix: MMYYYY/TABLE_NAME.CSV
    ```

3. Set the required environment variables in the Dockerfile:
    - `RDS_HOST`: PostgreSQL database host
    - `RDS_DB_PORT`: PostgreSQL database port
    - `RDS_USERNAME`: PostgreSQL database username
    - `RDS_PASSWORD`: PostgreSQL database password
    - `RDS_DBNAME`: PostgreSQL database name
    - `DESTINATION_BUCKET`: Amazon S3 bucket name for destination storage
    - `DESTINATION_ACCOUNT_ID`: AWS account ID for the destination account
    - `CROSS_ACCOUNT_ROLE_NAME`: Name of the cross-account role in the destination account

4. Build the Docker image:
    ```bash
    docker build -t data-exporter .
    ```

5. Run the Docker container:
    ```bash
    docker run --rm data-exporter
    ```

The script will run inside the Docker container, export the specified tables to CSV files, and upload them to the configured Amazon S3 bucket.

## Notes

- The script uses the Alpine version of the official Python Docker image to minimize the image size and improve efficiency.

- The script and the `tables.yaml` file are copied into the Docker image during the build process.

- The required Python dependencies (`psycopg2`, `boto3`, `pyyaml`) are installed inside the Docker image.

- Ensure that you have replaced the environment variables in the Dockerfile with the actual values specific to your PostgreSQL database and Amazon S3 bucket.

- Make sure to have proper network connectivity and access permissions to the PostgreSQL database and Amazon S3 bucket from within the Docker container.

- For security reasons, it is recommended to restrict the access permissions to the Docker image and any sensitive configuration files.

## License

This script is licensed under the [MIT License](LICENSE).

For more information on using Docker, refer to the official Docker documentation: [https://docs.docker.com](https://docs.docker.com)

Enjoy exporting your PostgreSQL data to CSV files and uploading them to Amazon S3 using this convenient Dockerized solution!
    
