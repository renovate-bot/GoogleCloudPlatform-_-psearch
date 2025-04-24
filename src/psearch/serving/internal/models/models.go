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

package models

// SearchRequest represents a search query request
type SearchRequest struct {
	Query     string   `json:"query" binding:"required"`
	Limit     *int     `json:"limit,omitempty"`
	MinScore  *float64 `json:"min_score,omitempty"`
	Alpha     *float64 `json:"alpha,omitempty"`
}

// SearchResponse represents the response to a search query
type SearchResponse struct {
	Results    []SearchResult `json:"results"`
	TotalFound int            `json:"total_found"`
}

// SearchResult represents a single product search result
type SearchResult struct {
	ID               string        `json:"id"`
	Name             string        `json:"name"`
	Title            string        `json:"title"`
	Brands           []string      `json:"brands"`
	Categories       []string      `json:"categories"`
	PriceInfo        PriceInfo     `json:"priceInfo"`
	ColorInfo        *ColorInfo    `json:"colorInfo,omitempty"`
	Availability     string        `json:"availability"`
	AvailableQuantity *int         `json:"availableQuantity,omitempty"`
	AvailableTime    *string       `json:"availableTime,omitempty"`
	Images           []Image       `json:"images"`
	Sizes            []string      `json:"sizes"`
	RetrievableFields string       `json:"retrievableFields"`
	Attributes       []Attribute   `json:"attributes"`
	URI              string        `json:"uri"`
	Score            map[string]float64 `json:"score"`
}

// Image represents a product image
type Image struct {
	Height string `json:"height"`
	Width  string `json:"width"`
	URI    string `json:"uri"`
}

// PriceInfo represents product pricing information
type PriceInfo struct {
	Cost             string `json:"cost"`
	CurrencyCode     string `json:"currencyCode"`
	OriginalPrice    string `json:"originalPrice"`
	Price            string `json:"price"`
	PriceEffectiveTime string `json:"priceEffectiveTime"`
	PriceExpireTime  string `json:"priceExpireTime"`
}

// ColorInfo represents product color information
type ColorInfo struct {
	ColorFamilies []string `json:"colorFamilies,omitempty"`
	Colors        []string `json:"colors,omitempty"`
}

// AttributeValue represents the value of a product attribute
type AttributeValue struct {
	Indexable  *string   `json:"indexable,omitempty"`
	Searchable *string   `json:"searchable,omitempty"`
	Text       []string  `json:"text,omitempty"`
	Numbers    []float64 `json:"numbers,omitempty"`
}

// Attribute represents a product attribute
type Attribute struct {
	Key   string         `json:"key"`
	Value AttributeValue `json:"value"`
}

// HealthResponse represents the response from the health check endpoint
type HealthResponse struct {
	Status string `json:"status"`
}
