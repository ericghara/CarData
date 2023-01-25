CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS public.manufacturer (
	manufacturer_id uuid NOT NULL DEFAULT uuid_generate_v4(),
	official_name varchar(255) NOT NULL,
	common_name varchar(255) NOT NULL,
	CONSTRAINT manufacturer_common_name_key UNIQUE (common_name),
	CONSTRAINT manufacturer_official_name_key UNIQUE (official_name),
	CONSTRAINT manufacturer_pkey PRIMARY KEY (manufacturer_id)
);

CREATE TABLE IF NOT EXISTS public.brand (
	brand_id uuid NOT NULL DEFAULT uuid_generate_v4(),
	manufacturer_id uuid NOT NULL REFERENCES public.manufacturer,
	"name" varchar(255) NOT NULL,
	CONSTRAINT brand_name_key UNIQUE (name),
	CONSTRAINT brand_pkey PRIMARY KEY (brand_id)
);

CREATE TABLE IF NOT EXISTS public.model (
	model_id uuid NOT NULL PRIMARY KEY DEFAULT uuid_generate_v4(),
	"name" varchar(255) NOT NULL,
	model_year date NOT NULL,
	brand_id uuid REFERENCES public.brand NOT NULL,
	CONSTRAINT date_is_jan_1 CHECK ( date_trunc('year', model_year) = model_year ),
	CONSTRAINT model_no_dups UNIQUE(brand_id, "name", model_year)
);

CREATE TABLE IF NOT EXISTS public.model_raw_config_data (
	data_id uuid NOT NULL PRIMARY KEY DEFAULT uuid_generate_v4(),
	raw_data jsonb NOT NULL,
	model_id uuid NOT NULL REFERENCES public.model NOT NULL,
	created_at timestamptz NOT NULL DEFAULT current_timestamp,
	CONSTRAINT model_raw_config_no_dups UNIQUE (model_id,created_at)
);

CREATE TYPE public.attribute_type AS ENUM (
	'ENGINE',
    'TRANSMISSION',
    'DRIVE',
    'BODY_STYLE',
    'GRADE',
    'PACKAGE',
    'INTERIOR_COLOR',
    'EXTERIOR_COLOR',
    'ACCESSORY',
    'OPTION',
    'OTHER'
);

CREATE TABLE IF NOT EXISTS public.model_attribute (
	attribute_id uuid NOT NULL DEFAULT uuid_generate_v4(),
	attribute_type attribute_type NOT NULL,
	title TEXT NOT NULL,
	model_id uuid NOT NULL REFERENCES public.model,
	attribute_metadata jsonb NOT NULL,
	updated_at timestamptz NOT NULL DEFAULT current_timestamp,
	CONSTRAINT model_attribute_no_dups UNIQUE(attribute_type, title, model_id)
);