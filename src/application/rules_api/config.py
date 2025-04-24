# 
# Copyright 2025 Google LLC
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     https://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration class
class Config:
    PROJECT_ID = os.getenv('REACT_APP_PROJECT_ID', 'psearch-dev')
    FIRESTORE_DATABASE = os.getenv('REACT_APP_FIRESTORE_DATABASE', '(default)')
    FIRESTORE_COLLECTION = os.getenv('REACT_APP_FIRESTORE_COLLECTION', 'backend_rules')

    @classmethod
    def validate(cls):
        missing = []
        for key, value in cls.__dict__.items():
            if not key.startswith('_') and value is None:
                missing.append(key)
        if missing:
            raise ValueError(f"Missing configuration values: {', '.join(missing)}")
        return True

# Create and validate config instance
config = Config()
config.validate() 