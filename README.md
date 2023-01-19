# CarData

## Overview
CarData is an ETL pipeline that aims to scrape model information about cars (technically all automobiles)
directly from the websites of auto manufacturers.  The information targeted, is configuration options,
such as interior colors, performance packages, wheel options, trim levels etc. 

The ultimate goal of CarData is to create a dataset of model information with a common schema across different manufacturers.

CarData is composed of 2 units:
- **Extractor** - scrapes JSON data from auto manufacturers' websites, by interacting directly with their *public* APIs
- **Transformer** - translates data retrieved by the extractor into a brand-agnostic schema

## Project Status
- **Extractor**
  - Toyota
  - Lexus
  - Chevrolet
  - Cadillac
  - Buick
  - GMC
- **Transformer** - Work in progress
  - Toyota/Lexus
  - General Motors brands - Work in progress

### Currently Accessible Data
- 406 car models
- 24,400 configuration options