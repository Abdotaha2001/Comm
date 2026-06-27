-- TT-OS — core database schema (Postgres) — realizes BUILD_ORDER #3 / MASTER_SPEC Part 27.
-- Starter DDL for the P1 flagship MVP (players → analysis → profiles → game plans).
-- Enums are grounded in MASTER_SPEC Parts 19 (skills), 20 (equipment), 24 (para), 19-B8 (styles).
-- Convention: UUID PKs, timestamptz, jsonb for nested/flexible data, numeric(4,3) for 0..1 confidence.

BEGIN;

CREATE EXTENSION IF NOT EXISTS pgcrypto;  -- gen_random_uuid()

-- Auto-maintain updated_at on UPDATE
CREATE OR REPLACE FUNCTION set_updated_at() RETURNS trigger AS $$
BEGIN NEW.updated_at = now(); RETURN NEW; END;
$$ LANGUAGE plpgsql;

-- ─────────────────────────────────────────────────────────────
-- Tenancy & auth
-- ─────────────────────────────────────────────────────────────
CREATE TABLE organizations (
    id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    name        text NOT NULL,
    type        text NOT NULL CHECK (type IN ('federation','club','academy','individual')),
    settings    jsonb NOT NULL DEFAULT '{}'::jsonb,   -- locale, retention_days, default flags (Part 15)
    created_at  timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE users (
    id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id      uuid NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    email         text NOT NULL UNIQUE,
    full_name     text,
    role          text NOT NULL CHECK (role IN ('admin','coach','player','umpire','medical','scout')),
    password_hash text,                                  -- null when using an external IdP
    status        text NOT NULL DEFAULT 'active' CHECK (status IN ('active','disabled')),
    last_login_at timestamptz,
    created_at    timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX idx_users_org ON users(org_id);

-- Service / programmatic auth (hashed API keys)
CREATE TABLE api_keys (
    id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id      uuid NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name        text NOT NULL,
    key_hash    text NOT NULL,
    scopes      text[] NOT NULL DEFAULT '{}',
    last_used_at timestamptz,
    revoked_at  timestamptz,
    created_at  timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX idx_apikeys_org ON api_keys(org_id);

-- ─────────────────────────────────────────────────────────────
-- Players (pro / junior / para) + equipment
-- ─────────────────────────────────────────────────────────────
CREATE TABLE players (
    id                uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id            uuid NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    full_name         text NOT NULL,
    type              text NOT NULL DEFAULT 'pro' CHECK (type IN ('pro','junior')),
    handedness        text NOT NULL DEFAULT 'unknown' CHECK (handedness IN ('left','right','unknown')),
    grip              text NOT NULL DEFAULT 'unknown'
                       CHECK (grip IN ('shakehand','penhold_chinese','penhold_japanese','seemiller','other','unknown')),
    date_of_birth     date,
    sex               text CHECK (sex IN ('m','f','x')),
    country           text,
    -- Para (MASTER_SPEC Part 24); null = able-bodied
    para_class        smallint CHECK (para_class BETWEEN 1 AND 11),
    impairment_type   text CHECK (impairment_type IN (
                          'impaired_muscle_power','impaired_passive_rom','limb_deficiency',
                          'leg_length_difference','short_stature','hypertonia','ataxia',
                          'athetosis','intellectual')),
    mobility_mode     text NOT NULL DEFAULT 'na' CHECK (mobility_mode IN ('standing','wheelchair','na')),
    disability_notes  text,
    -- Talent (Part 23)
    maturation_status text CHECK (maturation_status IN ('early','average','late','unknown')),
    -- lifecycle & audit
    status            text NOT NULL DEFAULT 'active' CHECK (status IN ('active','archived')),
    archived_at       timestamptz,
    created_by        uuid REFERENCES users(id) ON DELETE SET NULL,
    created_at        timestamptz NOT NULL DEFAULT now(),
    updated_at        timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX idx_players_org ON players(org_id);
CREATE INDEX idx_players_para ON players(para_class) WHERE para_class IS NOT NULL;
CREATE TRIGGER trg_players_updated BEFORE UPDATE ON players
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- Consent & data governance (critical for juniors / para / minors — MASTER_SPEC Part 15)
CREATE TABLE consents (
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    player_id       uuid NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    type            text NOT NULL CHECK (type IN ('data_processing','video_storage','image_rights','medical')),
    granted         boolean NOT NULL DEFAULT true,
    by_guardian     boolean NOT NULL DEFAULT false,    -- true when the player is a minor
    guardian_name   text,
    scope           text,
    granted_at      timestamptz NOT NULL DEFAULT now(),
    expires_at      timestamptz,
    revoked_at      timestamptz
);
CREATE INDEX idx_consents_player ON consents(player_id);

CREATE TABLE player_equipment (
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    player_id       uuid NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    blade           text,
    fh_rubber       text,
    fh_rubber_type  text CHECK (fh_rubber_type IN ('inverted','short_pips','medium_pips','long_pips','anti')),
    fh_sponge_mm    numeric(3,1),  -- 0 = OX
    bh_rubber       text,
    bh_rubber_type  text CHECK (bh_rubber_type IN ('inverted','short_pips','medium_pips','long_pips','anti')),
    bh_sponge_mm    numeric(3,1),
    valid_from      date NOT NULL DEFAULT CURRENT_DATE,
    created_at      timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX idx_equipment_player ON player_equipment(player_id);

-- ─────────────────────────────────────────────────────────────
-- Videos & analysis runs
-- ─────────────────────────────────────────────────────────────
CREATE TABLE videos (
    id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id        uuid NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    player_id     uuid REFERENCES players(id) ON DELETE SET NULL,
    source        text NOT NULL CHECK (source IN ('upload','drive','url','stream')),
    storage_key   text,
    status        text NOT NULL DEFAULT 'uploaded'
                   CHECK (status IN ('uploaded','queued','processing','done','failed')),
    capture_tier  text NOT NULL DEFAULT 't1' CHECK (capture_tier IN ('t1','t2','t3')),
    fps           numeric(6,2),
    width         int,
    height        int,
    duration_sec  numeric(10,2),
    uploaded_by   uuid REFERENCES users(id) ON DELETE SET NULL,
    created_at    timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX idx_videos_org ON videos(org_id);
CREATE INDEX idx_videos_player ON videos(player_id);

CREATE TABLE analysis_runs (
    id                uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    video_id          uuid NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
    status            text NOT NULL DEFAULT 'queued'
                       CHECK (status IN ('queued','processing','done','failed')),
    model_versions    jsonb NOT NULL DEFAULT '{}'::jsonb,   -- reproducibility/provenance
    input_quality     jsonb,                                -- res/fps/angle/lighting/occlusion%
    reliability_index numeric(4,3) CHECK (reliability_index BETWEEN 0 AND 1),
    error             text,
    started_at        timestamptz,
    finished_at       timestamptz,
    created_at        timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX idx_runs_video ON analysis_runs(video_id);

-- ─────────────────────────────────────────────────────────────
-- Results: match → rallies → shots / events
-- ─────────────────────────────────────────────────────────────
CREATE TABLE matches (
    id               uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_run_id  uuid NOT NULL REFERENCES analysis_runs(id) ON DELETE CASCADE,
    video_id         uuid NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
    player1_id       uuid REFERENCES players(id) ON DELETE SET NULL,
    player2_id       uuid REFERENCES players(id) ON DELETE SET NULL,
    player3_id       uuid REFERENCES players(id) ON DELETE SET NULL,  -- doubles
    player4_id       uuid REFERENCES players(id) ON DELETE SET NULL,  -- doubles
    score            jsonb,           -- {"sets": [...], "points": {...}}
    format           text CHECK (format IN ('bo3','bo5','bo7')),
    is_doubles       boolean NOT NULL DEFAULT false,
    created_at       timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX idx_matches_run ON matches(analysis_run_id);

CREATE TABLE rallies (
    id               uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    match_id         uuid NOT NULL REFERENCES matches(id) ON DELETE CASCADE,
    idx              int NOT NULL,
    start_frame      int,
    end_frame        int,
    start_ms         bigint,
    end_ms           bigint,
    server_player_id uuid REFERENCES players(id) ON DELETE SET NULL,
    winner_player_id uuid REFERENCES players(id) ON DELETE SET NULL,
    reason           text,
    duration_sec     numeric(6,2),
    quality          numeric(5,1),    -- 0..100 rally quality
    confidence       numeric(4,3) CHECK (confidence BETWEEN 0 AND 1),
    UNIQUE (match_id, idx)
);
CREATE INDEX idx_rallies_match ON rallies(match_id);

CREATE TABLE shots (
    id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    rally_id     uuid NOT NULL REFERENCES rallies(id) ON DELETE CASCADE,
    idx          int NOT NULL,
    player_id    uuid REFERENCES players(id) ON DELETE SET NULL,
    frame        int,
    ts_ms        bigint,
    stroke_type  text,        -- enum list in MASTER_SPEC Part 27 §2 (validated at app layer)
    spin_type    text CHECK (spin_type IN
                  ('topspin','backspin','sidespin_left','sidespin_right','corkspin','mixed','no_spin')),
    wing         text CHECK (wing IN ('fh','bh')),
    speed_kmh    numeric(6,2),
    speed_ci     numeric(6,2),     -- +/- interval half-width
    quality      numeric(5,1),
    confidence   numeric(4,3) CHECK (confidence BETWEEN 0 AND 1),
    provenance   jsonb,            -- {source, tier, signals[...]}
    UNIQUE (rally_id, idx)
);
CREATE INDEX idx_shots_rally ON shots(rally_id);

CREATE TABLE events (
    id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    rally_id    uuid REFERENCES rallies(id) ON DELETE CASCADE,        -- null for match-level events
    match_id    uuid REFERENCES matches(id) ON DELETE CASCADE,        -- timeouts, set changes, scoreboard reads
    type        text NOT NULL CHECK (type IN
                  ('bounce','net','hit','serve','point','let','violation','timeout','set_change','score_read')),
    frame       int,
    ts_ms       bigint,
    side        text,             -- near/far/left/right
    position    jsonb,            -- {x,y} image or {tx,ty} table coords
    confidence  numeric(4,3) CHECK (confidence BETWEEN 0 AND 1),
    provenance  jsonb,
    CHECK (rally_id IS NOT NULL OR match_id IS NOT NULL)
);
CREATE INDEX idx_events_rally ON events(rally_id);
CREATE INDEX idx_events_match ON events(match_id);
CREATE INDEX idx_events_type ON events(type);

-- ─────────────────────────────────────────────────────────────
-- Aggregated profile (versioned, append-only)
-- ─────────────────────────────────────────────────────────────
CREATE TABLE player_profiles (
    id                uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    player_id         uuid NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    version           int NOT NULL,
    style_class       text CHECK (style_class IN
                        ('fh_looper','two_winged_attacker','counter_driver','all_rounder','chopper',
                         'penhold_looper','penhold_rpb','short_pips_hitter','combination_chopper')),
    aggregated_stats  jsonb NOT NULL DEFAULT '{}'::jsonb,
    style_signature   jsonb,
    strengths         jsonb,
    weaknesses        jsonb,
    source_video_ids  jsonb,
    confidence        numeric(4,3) CHECK (confidence BETWEEN 0 AND 1),
    created_at        timestamptz NOT NULL DEFAULT now(),
    UNIQUE (player_id, version)
);

-- ─────────────────────────────────────────────────────────────
-- Opponent dossier → matchup → game plan → outcome
-- ─────────────────────────────────────────────────────────────
CREATE TABLE opponent_dossiers (
    id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id              uuid NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    subject_player_id   uuid NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    opponent_player_id  uuid REFERENCES players(id) ON DELETE SET NULL,
    opponent_ref        text,          -- free name when not in DB
    footage_count       int NOT NULL DEFAULT 0,
    style_class         text,
    summary             jsonb,
    confidence          numeric(4,3) CHECK (confidence BETWEEN 0 AND 1),
    created_at          timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX idx_dossiers_subject ON opponent_dossiers(subject_player_id);

CREATE TABLE matchups (
    id                 uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id             uuid NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    my_player_id       uuid NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    opponent_dossier_id uuid REFERENCES opponent_dossiers(id) ON DELETE SET NULL,
    h2h                jsonb,
    predicted_winprob  numeric(4,3) CHECK (predicted_winprob BETWEEN 0 AND 1),
    confidence         numeric(4,3) CHECK (confidence BETWEEN 0 AND 1),
    created_at         timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX idx_matchups_player ON matchups(my_player_id);

CREATE TABLE game_plans (
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    matchup_id      uuid NOT NULL REFERENCES matchups(id) ON DELETE CASCADE,
    plan            jsonb NOT NULL DEFAULT '{}'::jsonb,
    training_block  jsonb,
    report_key      text,             -- storage key of the PDF
    status          text NOT NULL DEFAULT 'draft' CHECK (status IN ('draft','final')),
    confidence      numeric(4,3) CHECK (confidence BETWEEN 0 AND 1),
    created_at      timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX idx_plans_matchup ON game_plans(matchup_id);

CREATE TABLE plan_outcomes (
    id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    game_plan_id  uuid NOT NULL REFERENCES game_plans(id) ON DELETE CASCADE,
    match_id      uuid REFERENCES matches(id) ON DELETE SET NULL,
    actual_result text,
    adherence     numeric(4,3) CHECK (adherence BETWEEN 0 AND 1),
    effectiveness numeric(4,3) CHECK (effectiveness BETWEEN 0 AND 1),
    notes         text,
    created_at    timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX idx_outcomes_plan ON plan_outcomes(game_plan_id);

-- ─────────────────────────────────────────────────────────────
-- Generated outputs (annotated video, charts, clips, reports, results.json)
-- ─────────────────────────────────────────────────────────────
CREATE TABLE artifacts (
    id               uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_run_id  uuid REFERENCES analysis_runs(id) ON DELETE CASCADE,
    match_id         uuid REFERENCES matches(id) ON DELETE CASCADE,
    game_plan_id     uuid REFERENCES game_plans(id) ON DELETE CASCADE,
    type             text NOT NULL CHECK (type IN ('video','chart','clip','report','results_json')),
    storage_key      text NOT NULL,
    meta             jsonb,
    created_at       timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX idx_artifacts_run ON artifacts(analysis_run_id);
CREATE INDEX idx_artifacts_match ON artifacts(match_id);

-- ─────────────────────────────────────────────────────────────
-- Coaching: drill catalog + periodized training plans (MASTER_SPEC Parts 08, 22)
-- ─────────────────────────────────────────────────────────────
CREATE TABLE drills (
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id          uuid REFERENCES organizations(id) ON DELETE CASCADE,  -- null = global catalog
    name            text NOT NULL,
    targets_skill   text,                 -- stroke_type / footwork / etc. (Part 19)
    structure       text CHECK (structure IN ('regular','semi_random','random')),
    multiball       boolean NOT NULL DEFAULT false,
    mode            text CHECK (mode IN ('solo','partner','robot')),
    level           text CHECK (level IN ('beginner','intermediate','advanced','elite')),
    phase           text CHECK (phase IN ('off_season','pre_season','in_season')),
    description     text,
    video_key       text,
    created_at      timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX idx_drills_org ON drills(org_id);

CREATE TABLE training_plans (
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    player_id       uuid NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    horizon         text NOT NULL CHECK (horizon IN ('daily','weekly','monthly','yearly','olympic_cycle')),
    plan            jsonb NOT NULL DEFAULT '{}'::jsonb,    -- periodized blocks + prescribed drills
    source_profile_id uuid REFERENCES player_profiles(id) ON DELETE SET NULL,
    confidence      numeric(4,3) CHECK (confidence BETWEEN 0 AND 1),
    created_at      timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX idx_trainingplans_player ON training_plans(player_id);

-- ─────────────────────────────────────────────────────────────
-- Webhook subscriptions (tenant-registered) + delivery secret
-- ─────────────────────────────────────────────────────────────
CREATE TABLE webhooks (
    id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id      uuid NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    url         text NOT NULL,
    secret      text NOT NULL,                 -- HMAC signing secret
    events      text[] NOT NULL DEFAULT '{}',  -- e.g. {analysis.completed, gameplan.ready}
    active      boolean NOT NULL DEFAULT true,
    created_at  timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX idx_webhooks_org ON webhooks(org_id);

-- ─────────────────────────────────────────────────────────────
-- Audit trail (who did what) — RBAC accountability (MASTER_SPEC Part 15)
-- ─────────────────────────────────────────────────────────────
CREATE TABLE audit_log (
    id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id      uuid NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    user_id     uuid REFERENCES users(id) ON DELETE SET NULL,
    action      text NOT NULL,                 -- create/update/delete/generate/login...
    entity      text NOT NULL,                 -- table/resource name
    entity_id   uuid,
    meta        jsonb,
    at          timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX idx_audit_org_at ON audit_log(org_id, at);
CREATE INDEX idx_audit_entity ON audit_log(entity, entity_id);

-- A few additional FK indexes for hot paths
CREATE INDEX idx_shots_player ON shots(player_id);
CREATE INDEX idx_outcomes_match ON plan_outcomes(match_id);

COMMIT;
