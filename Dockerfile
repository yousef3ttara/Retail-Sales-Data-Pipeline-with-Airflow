FROM apache/airflow:2.9.0

USER root

# تثبيت المتطلبات الأساسية + مفتاح مايكروسوفت
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gnupg2 \
    apt-transport-https \
    unixodbc \
    unixodbc-dev \
    && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/12/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql17 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER airflow

# تثبيت مكتبات بايثون المطلوبة
RUN pip install --no-cache-dir pyodbc sqlalchemy python-dotenv pandas