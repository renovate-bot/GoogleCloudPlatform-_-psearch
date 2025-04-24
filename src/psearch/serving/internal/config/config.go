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

package config

import (
	"fmt"
	"os"
	"strconv"

	"github.com/joho/godotenv"
)

// Config holds all configuration for the application
type Config struct {
	// Server configuration
	Port        int
	Environment string

	// Google Cloud configuration
	ProjectID          string
	Region             string
	SpannerInstanceID  string
	SpannerDatabaseID  string
	GeminiModelName    string
	EmbeddingDimension int

	// Application defaults
	DefaultAlpha  float64
	DefaultLimit  int
	MinScoreValue float64
}

// Load loads configuration from environment variables with fallbacks to defaults
func Load() (*Config, error) {
	// Load .env file if it exists
	godotenv.Load()

	// Default configuration
	config := &Config{
		Port:              8080,
		Environment:       "development",
		GeminiModelName:   "text-multilingual-embedding-002",
		EmbeddingDimension: 768,
		DefaultAlpha:      0.5,
		DefaultLimit:      100,
		MinScoreValue:     0.0,
	}

	// Override with environment variables if set
	if port, err := strconv.Atoi(getEnv("PORT", "8080")); err == nil {
		config.Port = port
	}

	config.Environment = getEnv("ENVIRONMENT", config.Environment)
	config.ProjectID = getEnv("PROJECT_ID", "")
	config.Region = getEnv("REGION", "us-central1")
	config.SpannerInstanceID = getEnv("SPANNER_INSTANCE_ID", "")
	config.SpannerDatabaseID = getEnv("SPANNER_DATABASE_ID", "")
	config.GeminiModelName = getEnv("GEMINI_MODEL_NAME", config.GeminiModelName)

	// Parse numeric values with defaults
	if dim, err := strconv.Atoi(getEnv("EMBEDDING_DIMENSION", "768")); err == nil {
		config.EmbeddingDimension = dim
	}

	if alpha, err := strconv.ParseFloat(getEnv("DEFAULT_HYBRID_ALPHA", "0.5"), 64); err == nil {
		config.DefaultAlpha = alpha
	}

	if limit, err := strconv.Atoi(getEnv("DEFAULT_LIMIT", "10")); err == nil {
		config.DefaultLimit = limit
	}

	if minScore, err := strconv.ParseFloat(getEnv("MIN_SCORE_VALUE", "0.0"), 64); err == nil {
		config.MinScoreValue = minScore
	}

	// Validate required configuration
	if config.ProjectID == "" {
		return nil, fmt.Errorf("PROJECT_ID environment variable is required")
	}

	if config.SpannerInstanceID == "" {
		return nil, fmt.Errorf("SPANNER_INSTANCE_ID environment variable is required")
	}

	if config.SpannerDatabaseID == "" {
		return nil, fmt.Errorf("SPANNER_DATABASE_ID environment variable is required")
	}

	return config, nil
}

// getEnv gets an environment variable or returns a default value
func getEnv(key, defaultValue string) string {
	value := os.Getenv(key)
	if value == "" {
		return defaultValue
	}
	return value
}
