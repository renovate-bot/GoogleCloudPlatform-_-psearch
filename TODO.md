# PSearch TODO List

---
## Feature/Enhancement: Generic Data Ingestion

**Goal:** Allow the ingestion pipeline (`src/psearch/ingestion/`) to read product data from various sources (e.g., GCS files, different BigQuery tables, databases) instead of being hardcoded to a specific BigQuery table, loading data directly into **Spanner** (including generated embeddings).

**Tasks:**

1.  **Refactor Ingestion Logic:**
    *   Modify the `IngestionController` (`src/psearch/ingestion/main.py`) to accept data source configuration dynamically (e.g., through environment variables or command-line arguments).
    *   Possible configuration options:
        *   Data Source Type (e.g., `bigquery`, `gcs`, `database`)
        *   Source Location/Identifier (e.g., BigQuery table ID, GCS bucket/file path, database connection string/query)
        *   Schema/Column Mapping (optional, to map source columns to expected **Spanner** fields defined in `src/iac/modules/spanner/schema.sql`).

2.  **Implement Data Connectors:**
    *   Create connector classes or functions to handle reading data from different sources (BigQuery, GCS, potentially others like PostgreSQL, MySQL).
    *   Ensure connectors handle data extraction, basic validation, and potentially schema mapping to the **Spanner** schema.

3.  **Update Terraform:**
    *   Modify the Terraform configuration for the ingestion job (`src/iac/modules/ingestion/main.tf`) to accept the new data source configuration as variables (e.g., `TF_VAR_ingestion_source_type`, `TF_VAR_ingestion_source_location`).
    *   Pass these variables as environment variables to the Cloud Run Job container. Ensure correct **Spanner** connection details are passed.

4.  **Update Documentation:**
    *   Update the `README.md` and `docs/USAGE.md` to reflect the new configuration options for data ingestion, referencing the **Spanner** target. Explain how users can configure the pipeline for different data sources.
    *   Provide clear examples for common data sources (BigQuery, GCS).

5.  **Add Tests:**
    *   Implement unit and integration tests for the new data connectors and the refactored ingestion logic targeting **Spanner**.

**Priority:** High - Core functionality enhancement for broader usability.

**Estimated Effort:** Medium - Requires significant changes to the ingestion pipeline and Terraform configuration.
