# PSearch: AI-Powered Product Search Platform

## Overview

PSearch is an advanced product search platform built on Google Cloud Platform. It leverages **Spanner's native hybrid search capabilities**, combining traditional text search with vector similarity search (using embeddings generated via Vertex AI) to understand the semantic meaning behind user queries. This results in more accurate, contextually relevant product search results stored and queried directly within Spanner.

**Core Features:**

*   **Spanner Hybrid Search:** Blends vector similarity and text search directly within Google Cloud Spanner for relevance and efficiency.
*   **AI Enhancements:** Includes AI-driven filter suggestions, content enrichment (text with Gemini, images with Imagen), and marketing content generation.
*   **Product Filtering:** Supports filtering by various attributes (categories, brands, price, etc.).
*   **Rules Engine:** Allows administrators to configure search behavior (via Rules API).
*   **Scalable Architecture:** Built with microservices on Google Cloud (Cloud Run).
*   **Modern UI:** Responsive React-based user interface with AI feature integration.

## Architecture

PSearch utilizes a microservices architecture deployed on Google Cloud:

*   **Frontend UI (React `src/application/ui/`):** Provides the user interface for searching, filtering, viewing products, and interacting with AI enhancements.
*   **Serving API (Go/Gin `src/psearch/serving-go/`):** Handles search requests, performs hybrid search directly against Spanner using its native vector and text search capabilities, generates query embeddings via Vertex AI, retrieves data from Spanner, and interacts with other services.
*   **Rules API (FastAPI/Python `src/application/rules_api/`):** Manages business rules for search results, stored in Firestore.
*   **Ingestion Pipeline (Cloud Run Job/Python `src/psearch/ingestion/`):** Processes product data (e.g., from BigQuery), generates embeddings using Vertex AI, and stores both structured data and embeddings directly into Spanner.
*   **GenAI Service (Cloud Run/Python `src/psearch/gen_ai/`):** Provides generative AI capabilities (content enrichment with Gemini, image enhancement with Gemini, conversational search features).
*   **Datastores:**
    *   **Spanner:** Primary storage for structured product data *and* vector embeddings. Enables integrated hybrid search.
    *   **Firestore:** Stores rules configurations and potentially other semi-structured or real-time data.
    *   **BigQuery:** Used for analytics and potentially as a source for the ingestion pipeline.

## Technology Stack

*   **Frontend:** React, Material-UI, Axios
*   **Backend:** Go (Gin) for Serving API, Python (FastAPI) for other services (Ingestion, GenAI, Rules).
*   **Databases:** Google Cloud Spanner (with vector search), Google Cloud BigQuery.
*   **AI/ML:** Google Vertex AI (Gemini for text and images, Embedding APIs via SDK).
*   **Infrastructure:** Google Cloud Platform (Cloud Run, Cloud Build), Terraform, Docker.

## Repository Structure

```
├── docs/             # Project documentation (contributing, usage)
├── memory-bank/      # Internal context documentation (project brief, tech context, etc.)
├── src/
│   ├── analytics/       # Analytics components (if any)
│   ├── application/     # Frontend UI and Rules API source code
│   ├── iac/             # Infrastructure as Code (Terraform)
│   ├── psearch/         # Backend services (ingestion, serving-go, gen_ai)
│   └── tooling/         # Development and operational tools/scripts
├── .gitignore
├── LICENSE              # Apache 2.0 License file
├── license-add.py       # Script to add license headers
```

## Tutorial/Documentação

### Como subir a plataforma (How to Set Up the Platform)

1.  **Prerequisites:**
    *   Google Cloud SDK (`gcloud`) installed and authenticated.
    *   Terraform installed.
    *   Terraform installed.
    *   Docker installed.
    *   Go 1.21+ installed (for Serving API).
    *   Python 3.9+ installed (for other services).
    *   Node.js and npm/yarn installed (for UI development/deployment).
    *   A Google Cloud Project with billing enabled and required APIs enabled (Spanner, Cloud Run, Cloud Build, Vertex AI, etc.).

2.  **Clone Repository:**
    ```bash
    git clone <repository-url>
    cd psearch
    ```

3.  **Configure Infrastructure:**
    *   Navigate to the IaC directory: `cd src/iac`
    *   Create a `terraform.tfvars` file (or set environment variables `TF_VAR_project_id`, `TF_VAR_region`, `TF_VAR_project_number`). Define at least:
        ```hcl
        project_id     = "your-gcp-project-id"
        region         = "your-gcp-region"        # e.g., "us-central1"
        project_number = "your-gcp-project-number"
        # Other variables as needed (see variables.tf files in modules)
        # Ensure Spanner instance meets minimum PU requirements for vector search (>=1000)
        ```
    *   *Note:* You can find your project number using `gcloud projects describe your-gcp-project-id --format='value(projectNumber)'`. The Spanner schema (`src/iac/modules/spanner/schema.sql`) defines the necessary tables, vector columns, and indexes for hybrid search.

4.  **Provision Infrastructure:**
    *   Initialize Terraform:
        ```bash
        terraform init
        ```
    *   Apply the Terraform configuration (this will create all GCP resources):
        ```bash
        terraform apply
        ```
        Review the plan and type `yes` to confirm. This process may take several minutes.

5.  **Deploy Application Services:**
    *   The `terraform apply` command provisions infrastructure and triggers Cloud Build pipelines defined in the respective service directories (`src/psearch/serving-go/cloudbuild.yaml`, `src/psearch/ingestion/cloudbuild.yaml`, etc.) via `local-exec` provisioners within the Terraform modules (e.g., `src/iac/modules/search_api/main.tf` for the Go service).
    *   This builds the Docker images and deploys them to Cloud Run.
    *   The Frontend UI (`src/application/ui/`) is typically also deployed via Cloud Build, triggered similarly by its Terraform module (`src/iac/modules/ui/main.tf`).
    *   Monitor build progress in the Google Cloud Console under Cloud Build. Service accounts created by Terraform have the necessary permissions.

### Como inserir dados (How to Insert Data)

The ingestion process uses a Cloud Run Job (`src/psearch/ingestion/`) to read product data (default: from a BigQuery table), generate embeddings using the Vertex AI SDK, and load both structured data and embeddings directly into **Spanner**. (Note: The goal is to make the source configurable, see `TODO.md`).

1.  **Prepare Source Data (e.g., BigQuery):**
    *   Ensure your product data is available in the configured source. By default, this might be a BigQuery table like `your-gcp-project-id.products_dataset.products_table`. Check the ingestion service configuration (`src/psearch/ingestion/main.py`) or Terraform variables (`src/iac/modules/ingestion/variables.tf`) for the exact source configuration.
    *   The required schema should align with the target Spanner table defined in `src/iac/modules/spanner/schema.sql`. Key fields typically include `id`, `title`, `description`, `images`, `categories`, `brands`, etc.

2.  **Execute the Cloud Run Ingestion Job:**
    *   The ingestion job (likely named `product-ingestion` or similar) created by Terraform needs to be manually executed to load data into Spanner.
    *   You can execute the job using the Google Cloud Console:
        1.  Navigate to Cloud Run in the Google Cloud Console.
        2.  Select the "Jobs" tab.
        3.  Find the job named `product-ingestion`.
        4.  Click "Execute" to start the job run.
    *   Alternatively, execute the job using the `gcloud` command line:
        ```bash
        # Ensure you replace 'product-ingestion' if the job name differs
        gcloud run jobs execute product-ingestion --region your-gcp-region --project your-gcp-project-id --wait
        ```
        *(Replace `your-gcp-region` and `your-gcp-project-id` with your specific values)*. The `--wait` flag makes the command wait for the job to complete.
    *   Monitor the job's progress and logs in the Cloud Run section of the Google Cloud Console.

### Como acessar a api com os dados ingeridos (How to Access the API)

1.  **Find API URL:** The **Go Serving API** URL is an output of the Terraform deployment. Retrieve it using:
    ```bash
    cd src/iac
    terraform output -raw search_api_service_url # Or the specific output name for the Go service URL
    ```
    Alternatively, find the deployed Cloud Run service (likely named `search-api-service` or similar) in your Google Cloud Console.

2.  **Make API Requests:** Use `curl`, Postman, or any HTTP client to interact with the Go API.
    *   **Example Search Request (POST):**
        ```bash
        API_URL=$(terraform output -raw search_api_service_url)
        curl -X POST "${API_URL}/search" \
             -H "Content-Type: application/json" \
             -d '{
                   "query": "your search term",
                   "limit": 10,
                   "query": "stylish red running shoes",
                   "limit": 10,
                   "hybrid_search_config": {
                       "alpha": 0.6 # Example: Weighting vector vs text score
                   }
                 }'
        ```
    *   *Note:* The endpoint is likely `/search` (verify in `src/psearch/serving-go/internal/api/routes.go`). It expects a JSON body. Check the Go source code (`src/psearch/serving-go/internal/models/models.go` and `handlers.go`) for the exact request/response schema and available parameters (like `limit`, `hybrid_search_config`, etc.). The Go service does not automatically generate OpenAPI/Swagger docs like FastAPI; documentation relies on code comments or separate documentation efforts.

## Contributing

Please see [docs/contributing.md](docs/contributing.md) for details on how to contribute to this project.

## License

This project is licensed under the Apache License, Version 2.0. See the [LICENSE](LICENSE) file for details.

## Disclaimer

This is not an officially supported Google product. This project is not eligible for the [Google Open Source Software Vulnerability Rewards Program](https://bughunters.google.com/open-source-security).
