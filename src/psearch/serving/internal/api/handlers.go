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

package api

import (
	"context"
	"fmt"
	"log"
	"net/http"

	"github.com/gin-gonic/gin"
	"psearch/serving-go/internal/config"
	"psearch/serving-go/internal/models"
	"psearch/serving-go/internal/services"
)

// Controller handles the API endpoints and connects to services
type Controller struct {
	config      *config.Config
	spannerSvc  *services.SpannerService
	embeddingSvc *services.EmbeddingService
}

// NewController creates a new controller instance
func NewController(cfg *config.Config) (*Controller, error) {
	ctx := context.Background()

	// Create the embedding service
	embeddingSvc, err := services.NewEmbeddingService(ctx, cfg)
	if err != nil {
		return nil, fmt.Errorf("failed to create embedding service: %v", err)
	}

	// Create the Spanner service
	spannerSvc, err := services.NewSpannerService(ctx, cfg, embeddingSvc)
	if err != nil {
		return nil, err
	}

	return &Controller{
		config:      cfg,
		spannerSvc:  spannerSvc,
		embeddingSvc: embeddingSvc,
	}, nil
}

// HealthCheck handles the health check endpoint
func (c *Controller) HealthCheck(ctx *gin.Context) {
	ctx.JSON(http.StatusOK, models.HealthResponse{
		Status: "healthy",
	})
}

// Search handles the search endpoint
func (c *Controller) Search(ctx *gin.Context) {
	// Parse the request body
	var req models.SearchRequest
	if err := ctx.ShouldBindJSON(&req); err != nil {
		ctx.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// Set default values if not provided
	limit := c.config.DefaultLimit
	if req.Limit != nil {
		limit = *req.Limit
	}

	minScore := c.config.MinScoreValue
	if req.MinScore != nil {
		minScore = *req.MinScore
	}

	alpha := c.config.DefaultAlpha
	if req.Alpha != nil {
		alpha = *req.Alpha
	}

	log.Printf("Search request: query=%s, limit=%d, minScore=%.2f, alpha=%.2f", 
		req.Query, limit, minScore, alpha)

	// Perform the hybrid search
	results, err := c.spannerSvc.HybridSearch(ctx, req.Query, limit, minScore, alpha)
	if err != nil {
		log.Printf("Search error: %v", err)
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": "Search failed"})
		return
	}

	// Return the results
	ctx.JSON(http.StatusOK, models.SearchResponse{
		Results:    results,
		TotalFound: len(results),
	})
}
