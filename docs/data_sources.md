# Data Sources & Integration Guide

## Government APIs

### CoWIN API
- Base URL: https://cdn-api.co-vin.in/api
- Authentication: Bearer token
- Rate limits: 100 requests/minute
- Documentation: https://apisetu.gov.in/public/marketplace/api/cowin

### IDSP (Integrated Disease Surveillance Programme)
- Weekly outbreak reports
- Data format: JSON/XML
- Update frequency: Weekly
- Access: Requires government approval

## Local Data Storage

### Vaccination Schedule
- Stored in PostgreSQL
- Updated monthly
- Source: National Immunization Schedule (NIS)

### Disease Prevention Information
- Stored as JSON files
- Sources:
  - WHO Guidelines
  - MoHFW Resources
  - Local Health Department Guidelines

## Data Update Process

1. Automated weekly pulls from government APIs
2. Data validation and cleaning
3. Storage in local database
4. Backup creation
5. Monitoring for changes