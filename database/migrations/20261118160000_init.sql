-- migrate:up
CREATE TABLE gesture (
  code        text PRIMARY KEY CHECK (code ~ '^[a-z][a-z0-9_]*$'),
  label       text NOT NULL,
  description text NOT NULL DEFAULT ''
);

CREATE TABLE action_type (
  code          text PRIMARY KEY CHECK (code ~ '^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+$'),
  label         text NOT NULL,
  description   text NOT NULL DEFAULT '',
  -- Format attendu des paramètres (JSON Schema simplifié), informatif pour l'API et le logiciel.
  params_schema jsonb NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE profile (
  name       text PRIMARY KEY CHECK (name ~ '^[a-z][a-z0-9_-]*$'),
  is_default boolean NOT NULL DEFAULT false,
  created_at timestamptz NOT NULL DEFAULT now()
);
-- Un seul profil par défaut.
CREATE UNIQUE INDEX profile_single_default ON profile (is_default) WHERE is_default;

CREATE TABLE binding (
  profile_name text NOT NULL REFERENCES profile(name) ON UPDATE CASCADE ON DELETE CASCADE,
  gesture_code text NOT NULL REFERENCES gesture(code) ON UPDATE CASCADE ON DELETE RESTRICT,
  hand         text NOT NULL DEFAULT 'any' CHECK (hand IN ('left', 'right', 'any')),
  trigger      text NOT NULL CHECK (trigger IN ('on_start', 'on_end', 'while_held')),
  action_code  text NOT NULL REFERENCES action_type(code) ON UPDATE CASCADE ON DELETE RESTRICT,
  params       jsonb NOT NULL DEFAULT '{}'::jsonb CHECK (jsonb_typeof(params) = 'object'),
  PRIMARY KEY (profile_name, gesture_code, hand, trigger)
);
CREATE INDEX binding_gesture_idx ON binding (gesture_code);
CREATE INDEX binding_action_idx ON binding (action_code);

-- migrate:down
DROP TABLE binding;
DROP TABLE profile;
DROP TABLE action_type;
DROP TABLE gesture;
