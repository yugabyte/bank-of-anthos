# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#FROM postgres:12-alpine
#FROM postgres:11-stretch
FROM postgres:11.2-alpine

# Files for initializing the database.
COPY initdb/0-accounts-schema.sql /docker-entrypoint-initdb.d/0-accounts-schema.sql
RUN chmod 755  /docker-entrypoint-initdb.d/0-accounts-schema.sql
COPY initdb/1-load-testdata.sh /docker-entrypoint-initdb.d/1-load-testdata.sh
RUN chmod 755  /docker-entrypoint-initdb.d/1-load-testdata.sh

# trick postgres container into performing YugabyteDB schema creation at runtime
COPY initdb.sh /docker-entrypoint-initdb.d/initdb.sh
RUN chmod 755 /docker-entrypoint-initdb.d/initdb.sh
