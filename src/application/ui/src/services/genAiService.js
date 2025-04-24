/*
 * Copyright 2025 Google LLC
 * 
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 * 
 *     https://www.apache.org/licenses/LICENSE-2.0
 * 
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import axios from 'axios';
import { GEN_AI_URL } from '../config';

/**
 * Service for handling interactions with the Gen AI API
 */

// Function to handle conversational search
export const getConversationalSearch = async (query, conversationHistory, productContext, maxResults = 5) => {
    try {
        const response = await axios.post(`${GEN_AI_URL}/conversational-search`, {
            query,
            conversation_history: conversationHistory,
            product_context: productContext,
            max_results: maxResults
        }, {
            timeout: 25000, // 25 second timeout
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        });

        // Validate the response data
        if (!response.data || !response.data.answer) {
            throw new Error('Incomplete data received from AI service');
        }

        return response.data;
    } catch (error) {
        console.error('Error in conversational search:', error);

        // Enhance error message based on error type
        if (error.code === 'ECONNABORTED') {
            throw new Error('Connection timeout. The search request took too long to process.');
        } else if (error.response) {
            // Server responded with a non-2xx status code
            const status = error.response.status;
            const message = error.response.data?.message || 'Unknown server error';
            throw new Error(`Server error (${status}): ${message}`);
        } else if (error.request) {
            // Request was made but no response received
            throw new Error('No response received from server. Please check your connection.');
        }

        throw error;
    }
};

// Function to handle product enrichment
export const getProductEnrichment = async (productId, productData, fieldsToEnrich) => {
    try {
        // Set a timeout for the API request to prevent hanging UI
        const response = await axios.post(`${GEN_AI_URL}/enrichment`, {
            product_id: productId,
            product_data: productData,
            fields_to_enrich: fieldsToEnrich
        }, {
            timeout: 25000, // 25 second timeout - shorter than the UI timeout
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        });

        // Debug logging of the entire response
        console.log('API Response from enrichment service:', response.data);
        console.log('Fields to enrich requested:', fieldsToEnrich);

        if (!response.data) {
            console.error('No data received from enrichment API');
            throw new Error('No data received from AI service');
        }

        if (!response.data.enriched_fields) {
            console.error('No enriched_fields found in response:', response.data);
            throw new Error('Response missing enriched_fields property');
        }

        // Log specific fields for debugging
        console.log('Enriched fields received:', Object.keys(response.data.enriched_fields));

        // Detailed validation with specific error messages
        if (fieldsToEnrich.includes('technical_specs') && !response.data.enriched_fields.technical_specs) {
            console.error('Missing technical_specs in enriched_fields:', response.data.enriched_fields);
            throw new Error('Technical specifications data missing from AI response');
        }

        if (fieldsToEnrich.includes('description') && !response.data.enriched_fields.description) {
            console.error('Missing description in enriched_fields:', response.data.enriched_fields);
            throw new Error('Description data missing from AI response');
        }

        return response.data;
    } catch (error) {
        console.error('Error in product enrichment:', error);
        // Enhance error message based on error type
        if (error.code === 'ECONNABORTED') {
            throw new Error('Connection timeout. The server took too long to respond.');
        } else if (error.response) {
            // Server responded with a non-2xx status code
            const status = error.response.status;
            const message = error.response.data?.message || 'Unknown server error';
            throw new Error(`Server error (${status}): ${message}`);
        } else if (error.request) {
            // Request was made but no response received
            throw new Error('No response received from server. Please check your connection.');
        }
        // For other errors, pass through the original error
        throw error;
    }
};

// Function to generate marketing content
export const generateMarketingContent = async (
    productId,
    productData,
    contentType,
    tone = 'professional',
    targetAudience = null,
    maxLength = 500
) => {
    try {
        const response = await axios.post(`${GEN_AI_URL}/marketing`, {
            product_id: productId,
            product_data: productData,
            content_type: contentType,
            tone,
            target_audience: targetAudience,
            max_length: maxLength
        }, {
            timeout: 25000, // 25 second timeout
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        });

        // Validate response data
        if (!response.data || !response.data.content) {
            throw new Error('Incomplete data received from marketing AI service');
        }

        return response.data;
    } catch (error) {
        console.error('Error generating marketing content:', error);

        // Enhance error message based on error type
        if (error.code === 'ECONNABORTED') {
            throw new Error('Connection timeout. Marketing content generation took too long.');
        } else if (error.response) {
            // Server responded with a non-2xx status code
            const status = error.response.status;
            const message = error.response.data?.message || 'Unknown server error';
            throw new Error(`Server error (${status}): ${message}`);
        } else if (error.request) {
            // Request was made but no response received
            throw new Error('No response received from server. Please check your connection.');
        }

        throw error;
    }
};

// Function to generate enhanced images using Gemini
export const generateEnhancedImage = async (payload) => {
    // payload should contain: { product_id, product_data, image_base64, background_prompt, person_description, style }
    try {
        const response = await axios.post(`${GEN_AI_URL}/generate-enhanced-image`, payload, {
            timeout: 40000, // 40 second timeout (image generation takes longer)
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        });

        // Validate response data
        if (!response.data || !response.data.generated_image_base64) {
            throw new Error('Incomplete image data received from AI service');
        }

        return response.data;
    } catch (error) {
        console.error('Error generating enhanced image:', error);

        // Enhance error message based on error type
        if (error.code === 'ECONNABORTED') {
            throw new Error('Connection timeout. Image generation took too long to complete.');
        } else if (error.response) {
            // Server responded with a non-2xx status code
            const status = error.response.status;
            const message = error.response.data?.message || 'Unknown server error';
            throw new Error(`Server error (${status}): ${message}`);
        } else if (error.request) {
            // Request was made but no response received
            throw new Error('No response received from server. Please check your connection.');
        }

        throw error;
    }
};

// Old function to generate images (removed as it's replaced by generateEnhancedImage)
/*
export const generateProductImage = async (
    productId,
    productData,
    prompt = null,
    imageType = 'lifestyle',
    style = 'photorealistic'
) => {
    try {
        const response = await axios.post(`${GEN_AI_URL}/imagen`, {
            product_id: productId,
            product_data: productData,
            prompt,
            image_type: imageType,
            style
        });
        return response.data;
    } catch (error) {
        console.error('Error generating image:', error);
        throw error;
    }
};
*/
