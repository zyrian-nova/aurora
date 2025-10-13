from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "users" (
    "id" UUID NOT NULL PRIMARY KEY,
    "email" VARCHAR(100) NOT NULL UNIQUE,
    "username" VARCHAR(100) NOT NULL UNIQUE,
    "hashed_password" VARCHAR(255) NOT NULL,
    "full_name" VARCHAR(255),
    "is_active" BOOL NOT NULL DEFAULT True,
    "is_superuser" BOOL NOT NULL DEFAULT False,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "last_login" TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS "idx_users_email_133a6f" ON "users" ("email");
CREATE INDEX IF NOT EXISTS "idx_users_usernam_266d85" ON "users" ("username");
COMMENT ON TABLE "users" IS 'User account model.';
CREATE TABLE IF NOT EXISTS "monitored_sites" (
    "id" UUID NOT NULL PRIMARY KEY,
    "url" VARCHAR(500) NOT NULL,
    "name" VARCHAR(255) NOT NULL,
    "check_interval_minutes" INT NOT NULL DEFAULT 30,
    "is_active" BOOL NOT NULL DEFAULT True,
    "expected_status_code" INT NOT NULL DEFAULT 200,
    "timeout_in_seconds" INT NOT NULL DEFAULT 10,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "user_id" UUID NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_monitored_s_user_id_83366b" UNIQUE ("user_id", "url")
);
COMMENT ON COLUMN "monitored_sites"."url" IS 'Full URL to monitor (e.g., https://example.com)';
COMMENT ON COLUMN "monitored_sites"."name" IS 'Friendly name for display';
COMMENT ON COLUMN "monitored_sites"."check_interval_minutes" IS 'How often to check (in minutes)';
COMMENT ON COLUMN "monitored_sites"."is_active" IS 'Whether monitoring is enabled';
COMMENT ON COLUMN "monitored_sites"."expected_status_code" IS 'Expected HTTP status code';
COMMENT ON COLUMN "monitored_sites"."timeout_in_seconds" IS 'Request timeout in seconds';
COMMENT ON TABLE "monitored_sites" IS 'Websites that users want to monitor for uptime.';
CREATE TABLE IF NOT EXISTS "site_status" (
    "id" UUID NOT NULL PRIMARY KEY,
    "is_up" BOOL NOT NULL DEFAULT True,
    "status_code" INT,
    "response_time_ms" INT,
    "checked_at" TIMESTAMPTZ NOT NULL DEFAULT '2025-10-13T06:41:42.076179+00:00',
    "site_id" UUID NOT NULL REFERENCES "monitored_sites" ("id") ON DELETE CASCADE,
    "user_id" UUID NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_site_status_checked_fc32ff" ON "site_status" ("checked_at");
CREATE INDEX IF NOT EXISTS "idx_site_status_site_id_cd7378" ON "site_status" ("site_id", "checked_at");
CREATE INDEX IF NOT EXISTS "idx_site_status_user_id_627203" ON "site_status" ("user_id", "checked_at");
COMMENT ON COLUMN "site_status"."response_time_ms" IS 'Response time in miliseconds';
COMMENT ON TABLE "site_status" IS 'Historical status checks for monitored websites.';
CREATE TABLE IF NOT EXISTS "user_preferences" (
    "id" UUID NOT NULL PRIMARY KEY,
    "word_languages" JSONB NOT NULL,
    "preferred_language" VARCHAR(10) NOT NULL DEFAULT 'en',
    "theme" VARCHAR(20) NOT NULL DEFAULT 'auto',
    "background_rotation" BOOL NOT NULL DEFAULT True,
    "location" VARCHAR(255),
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "user_id" UUID NOT NULL UNIQUE REFERENCES "users" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "user_preferences"."word_languages" IS 'Languages for word of the day (ISO 639-1 codes)';
COMMENT ON COLUMN "user_preferences"."preferred_language" IS 'Primary UI language';
COMMENT ON COLUMN "user_preferences"."theme" IS 'Theme: light, dark, auto';
COMMENT ON COLUMN "user_preferences"."background_rotation" IS 'Enable daily background image rotation';
COMMENT ON COLUMN "user_preferences"."location" IS 'City name or coordinates for weather (e.g., ''Helsinki'' or ''60.1699,24.9384'')';
COMMENT ON TABLE "user_preferences" IS 'User-specific preferences and settings.';
CREATE TABLE IF NOT EXISTS "rss_feeds" (
    "id" UUID NOT NULL PRIMARY KEY,
    "url" VARCHAR(500) NOT NULL UNIQUE,
    "title" VARCHAR(255),
    "description" TEXT,
    "site_url" VARCHAR(500),
    "favicon_url" VARCHAR(500),
    "language" VARCHAR(10),
    "is_active" BOOL NOT NULL DEFAULT True,
    "last_fetched_at" TIMESTAMPTZ,
    "last_error" TEXT,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS "idx_rss_feeds_url_1d29b0" ON "rss_feeds" ("url");
COMMENT ON COLUMN "rss_feeds"."is_active" IS 'Whether this feed is still valid';
COMMENT ON TABLE "rss_feeds" IS 'Catalog of RSS feeds available in the system.';
CREATE TABLE IF NOT EXISTS "user_rss_feeds" (
    "id" UUID NOT NULL PRIMARY KEY,
    "custom_name" VARCHAR(255),
    "is_active" BOOL NOT NULL DEFAULT True,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "feed_id" UUID NOT NULL REFERENCES "rss_feeds" ("id") ON DELETE CASCADE,
    "user_id" UUID NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_user_rss_fe_user_id_5b55ee" UNIQUE ("user_id", "feed_id")
);
COMMENT ON COLUMN "user_rss_feeds"."custom_name" IS 'User''s custom name for this feed';
COMMENT ON COLUMN "user_rss_feeds"."is_active" IS 'User can pause individual feeds';
COMMENT ON TABLE "user_rss_feeds" IS 'Junction table: User subscriptions to RSS feeds';
CREATE TABLE IF NOT EXISTS "subreddits" (
    "id" UUID NOT NULL PRIMARY KEY,
    "name" VARCHAR(100) NOT NULL UNIQUE,
    "display_name" VARCHAR(100),
    "description" TEXT,
    "subscriber_count" INT,
    "icon_url" VARCHAR(500),
    "is_active" BOOL NOT NULL DEFAULT True,
    "is_nsfw" BOOL NOT NULL DEFAULT False,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS "idx_subreddits_name_9b12f7" ON "subreddits" ("name");
COMMENT ON COLUMN "subreddits"."name" IS 'Subreddit name (without r/ prefix)';
COMMENT ON COLUMN "subreddits"."subscriber_count" IS 'Number of subscribers on Reddit';
COMMENT ON COLUMN "subreddits"."is_active" IS 'Whether this subreddit still exists';
COMMENT ON COLUMN "subreddits"."is_nsfw" IS 'Whether this subreddit content is +18';
COMMENT ON TABLE "subreddits" IS 'Catalog of subreddits available in the system.';
CREATE TABLE IF NOT EXISTS "user_subreddits" (
    "id" UUID NOT NULL PRIMARY KEY,
    "is_active" BOOL NOT NULL DEFAULT True,
    "sort_by" VARCHAR(20) NOT NULL DEFAULT 'hot',
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "subreddit_id" UUID NOT NULL REFERENCES "subreddits" ("id") ON DELETE CASCADE,
    "user_id" UUID NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_user_subred_user_id_a2114b" UNIQUE ("user_id", "subreddit_id")
);
COMMENT ON COLUMN "user_subreddits"."is_active" IS 'Usee can pause individual subreddits';
COMMENT ON COLUMN "user_subreddits"."sort_by" IS 'Sort preference: hot, new, top, rising';
COMMENT ON TABLE "user_subreddits" IS 'Junction table: User subscriptions to subreddits.';
CREATE TABLE IF NOT EXISTS "daily_cache" (
    "id" UUID NOT NULL PRIMARY KEY,
    "cache_date" DATE NOT NULL UNIQUE,
    "motivational_quote" TEXT,
    "quote_author" VARCHAR(255),
    "quote_source" VARCHAR(100),
    "word_en" JSONB,
    "word_es" JSONB,
    "word_fi" JSONB,
    "weather_data" JSONB,
    "generated_by_ollama" BOOL NOT NULL DEFAULT False,
    "generation_model" VARCHAR(100),
    "generation_duration_ms" INT,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS "idx_daily_cache_cache_d_ca0c98" ON "daily_cache" ("cache_date");
COMMENT ON COLUMN "daily_cache"."cache_date" IS 'Date this cache entry is valid for';
COMMENT ON COLUMN "daily_cache"."quote_source" IS 'Source: ollama, api, static';
COMMENT ON COLUMN "daily_cache"."word_en" IS 'English: {word, definition, example, pronunciation}';
COMMENT ON COLUMN "daily_cache"."word_es" IS 'Spanish: {word, definition, example, pronunciation}';
COMMENT ON COLUMN "daily_cache"."word_fi" IS 'Finnish: {word, definition, example, pronunciation}';
COMMENT ON COLUMN "daily_cache"."weather_data" IS 'Last fetched global weather data (if applicable)';
COMMENT ON COLUMN "daily_cache"."generated_by_ollama" IS 'Whether content was AI-generated';
COMMENT ON COLUMN "daily_cache"."generation_model" IS 'Ollama model used (e.g., llama3, mistral)';
COMMENT ON COLUMN "daily_cache"."generation_duration_ms" IS 'Time taken to generate content (milliseconds)';
COMMENT ON TABLE "daily_cache" IS 'Cache for daily generated content shared across all users.';
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """


MODELS_STATE = (
    "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"
)
