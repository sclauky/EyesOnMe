-- migrate:up
INSERT INTO gesture (code, label, description) VALUES
  ('peace_sign',  'Signe de paix', 'Index et majeur levés'),
  ('open_hand',   'Main ouverte',  'Tous les doigts écartés'),
  ('closed_hand', 'Poing fermé',   'Tous les doigts repliés');

INSERT INTO action_type (code, label, description, params_schema) VALUES
  ('mouse.toggle_control', 'Activer/désactiver la souris', 'Bascule le contrôle du curseur', '{}'),
  ('mouse.move',  'Déplacer le curseur', 'Le curseur suit un point de la main',
     '{"landmark": "integer (0-20, point MediaPipe suivi)"}'),
  ('mouse.click', 'Cliquer', 'Clic de souris',
     '{"button": "left|right|middle", "count": "integer (1 ou 2)"}');

INSERT INTO profile (name, is_default) VALUES ('default', true);

INSERT INTO binding (profile_name, gesture_code, hand, trigger, action_code, params) VALUES
  ('default', 'peace_sign',  'any', 'on_start',   'mouse.toggle_control', '{}'),
  ('default', 'open_hand',   'any', 'while_held', 'mouse.move',  '{"landmark": 8}'),
  ('default', 'closed_hand', 'any', 'on_start',   'mouse.click', '{"button": "left", "count": 1}');

-- migrate:down
DELETE FROM binding WHERE profile_name = 'default';
DELETE FROM profile WHERE name = 'default';
DELETE FROM action_type WHERE code IN ('mouse.toggle_control', 'mouse.move', 'mouse.click');
DELETE FROM gesture WHERE code IN ('peace_sign', 'open_hand', 'closed_hand');
