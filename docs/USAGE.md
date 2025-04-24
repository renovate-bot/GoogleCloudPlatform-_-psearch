# PSearch Usage Guide

This guide provides instructions on how to use the deployed PSearch application.

## Accessing the Application

1.  **Find the Frontend UI URL:** After successfully deploying the platform using Terraform, the URL for the frontend UI should be available.
    *   Check the Terraform output variables (you might need to add an output for the UI service URL in `src/iac/main.tf` or the UI module).
    *   Alternatively, navigate to Cloud Run in your Google Cloud Console and find the service corresponding to the frontend UI (likely named similar to `ps-ui-service` or based on the configuration in `src/iac/modules/ui/main.tf`). The URL will be listed there.

2.  **Open the URL:** Paste the obtained URL into your web browser.

## Searching for Products

1.  **Search Bar:** Locate the search bar, typically displayed prominently at the top of the page.
2.  **Enter Query:** Type your desired search term (e.g., "red running shoes", "organic cotton t-shirt") into the search bar.
3.  **Execute Search:** Press Enter or click the search icon/button.
4.  **View Results:** The search results page will display products matching your query, ranked by relevance based on the hybrid (vector + keyword) search algorithm.

## Filtering Results

The search results page usually offers various filtering options to refine your search:

*   **Categories:** Select specific product categories (e.g., "Apparel", "Electronics", "Shoes").
*   **Brands:** Filter by specific brands.
*   **Price Range:** Adjust sliders or enter minimum/maximum prices.
*   **Other Attributes:** Depending on the indexed data, you might find filters for size, color, ratings, etc.
*   **AI Filter Suggestions:** The platform may suggest relevant filters based on your search query and the available results.

Select the desired filters to narrow down the product list. The results should update automatically or upon clicking an "Apply Filters" button.

## Viewing Product Details

Click on any product card or title in the search results to navigate to its dedicated detail page (if implemented). This page typically shows more information, including:

*   Multiple product images.
*   Detailed description.
*   Price information.
*   Available sizes/colors.
*   Specifications or attributes.
*   Customer reviews (if available).

## Managing Rules (Admin Feature)

*Note: Access to rule management might be restricted to administrators.*

PSearch includes a Rules Engine, likely managed through a separate interface or the Rules API.

1.  **Access Rule Management:** Find the URL for the Rules API or any associated admin UI. This might be another Terraform output or a known endpoint.
2.  **Authenticate:** You may need specific credentials or permissions to access rule management.
3.  **Create/Modify Rules:** Use the interface or API to:
    *   **Boost Products:** Increase the ranking of specific products for certain search terms or conditions.
    *   **Bury Products:** Decrease the ranking of specific products.
    *   Define conditions under which rules apply (e.g., specific query terms, user segments).
4.  **Save Changes:** Ensure your rule configurations are saved. The Search API will automatically apply active rules during subsequent searches.

*(Refer to the specific documentation for the Rules API or admin UI for detailed instructions on rule creation and management.)*
