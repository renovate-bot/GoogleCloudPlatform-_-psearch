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
import config from '../config';

const API_BASE_URL = `${config.apiUrl}/api/rules`;

// Create axios instance with default configuration
const apiClient = axios.create({
  baseURL: config.apiUrl,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add response interceptor for error handling
apiClient.interceptors.response.use(
  response => response,
  error => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export const firestoreService = {
  async getRules() {
    try {
      const response = await apiClient.get('/api/rules');
      return response.data;
    } catch (error) {
      console.error('Error fetching rules:', error);
      throw error;
    }
  },

  async createRule(rule) {
    try {
      const response = await apiClient.post('/api/rules', rule);
      return response.data;
    } catch (error) {
      console.error('Error creating rule:', error);
      throw error;
    }
  },

  async updateRule(ruleId, rule) {
    try {
      const response = await apiClient.put(`/api/rules/${ruleId}`, rule);
      return response.data;
    } catch (error) {
      console.error('Error updating rule:', error);
      throw error;
    }
  },

  async deleteRule(ruleId) {
    try {
      await apiClient.delete(`/api/rules/${ruleId}`);
    } catch (error) {
      console.error('Error deleting rule:', error);
      throw error;
    }
  },

  async checkHealth() {
    try {
      const response = await apiClient.get('/api/health');
      return response.data;
    } catch (error) {
      console.error('Health check failed:', error);
      throw error;
    }
  }
}; 