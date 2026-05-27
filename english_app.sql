-- ============================================================
-- LexiRise Database Schema + Large Seed Data (MySQL 8+)
-- ============================================================
-- This script resets the LexiRise schema and loads a large demo dataset.
-- Demo user password for all seeded users: Password123!
-- ============================================================

SET NAMES utf8mb4;

CREATE DATABASE IF NOT EXISTS lexirise
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE lexirise;

DROP VIEW IF EXISTS user_tier;
DROP TRIGGER IF EXISTS trg_after_user_insert;

SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS user_question_attempts;
DROP TABLE IF EXISTS user_lesson_sessions;
DROP TABLE IF EXISTS user_progress;
DROP TABLE IF EXISTS questions;
DROP TABLE IF EXISTS lessons;
DROP TABLE IF EXISTS topics;
DROP TABLE IF EXISTS user_settings;
DROP TABLE IF EXISTS user_stats;
DROP TABLE IF EXISTS users;
SET FOREIGN_KEY_CHECKS = 1;

-- ============================================================
-- USERS AND PROFILE TABLES
-- ============================================================

CREATE TABLE users (
    id                 VARCHAR(36) NOT NULL DEFAULT (UUID()),
    email              VARCHAR(255) NOT NULL,
    password_hash      VARCHAR(255) NOT NULL,
    full_name          VARCHAR(150) NOT NULL,
    avatar_url         VARCHAR(500) NULL,
    daily_goal_minutes INT UNSIGNED NOT NULL DEFAULT 10,
    current_level      ENUM('A1','A2','B1','B2','C1','C2') NOT NULL DEFAULT 'A1',
    created_at         TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at         TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    UNIQUE KEY uq_users_email (email),
    KEY idx_users_level (current_level)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE user_settings (
    user_id               VARCHAR(36) NOT NULL,
    theme                 ENUM('light','dark') NOT NULL DEFAULT 'light',
    high_contrast_borders TINYINT(1) NOT NULL DEFAULT 0,
    notifications_enabled TINYINT(1) NOT NULL DEFAULT 1,
    updated_at            TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (user_id),
    CONSTRAINT fk_user_settings_user
        FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE user_stats (
    user_id              VARCHAR(36) NOT NULL,
    total_xp             INT UNSIGNED NOT NULL DEFAULT 0,
    streak_count         SMALLINT UNSIGNED NOT NULL DEFAULT 0,
    last_active_date     DATE NULL,
    words_mastered_count INT UNSIGNED NOT NULL DEFAULT 0,
    updated_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (user_id),
    CONSTRAINT fk_user_stats_user
        FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- LEARNING CONTENT
-- ============================================================

CREATE TABLE topics (
    id         VARCHAR(36) NOT NULL DEFAULT (UUID()),
    title      VARCHAR(200) NOT NULL,
    level      ENUM('A1','A2','B1','B2','C1','C2') NOT NULL,
    category   ENUM('Vocabulary','Grammar') NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    UNIQUE KEY uq_topics_title_level (title, level),
    KEY idx_topics_level (level),
    KEY idx_topics_category (category)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE lessons (
    id         VARCHAR(36) NOT NULL DEFAULT (UUID()),
    topic_id   VARCHAR(36) NOT NULL,
    `order`    SMALLINT UNSIGNED NOT NULL DEFAULT 1,
    xp_reward  SMALLINT UNSIGNED NOT NULL DEFAULT 100,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    UNIQUE KEY uq_lessons_topic_order (topic_id, `order`),
    KEY idx_lessons_topic (topic_id, `order`),
    CONSTRAINT fk_lessons_topic
        FOREIGN KEY (topic_id) REFERENCES topics(id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE questions (
    id               VARCHAR(36) NOT NULL DEFAULT (UUID()),
    lesson_id        VARCHAR(36) NOT NULL,
    word             VARCHAR(200) NOT NULL,
    context_sentence TEXT NULL,
    correct_answer   VARCHAR(500) NOT NULL,
    distractors      JSON NULL,
    image_url        VARCHAR(500) NULL,
    created_at       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    UNIQUE KEY uq_questions_lesson_word (lesson_id, word),
    KEY idx_questions_lesson (lesson_id),
    CONSTRAINT fk_questions_lesson
        FOREIGN KEY (lesson_id) REFERENCES lessons(id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE user_progress (
    user_id            VARCHAR(36) NOT NULL,
    lesson_id          VARCHAR(36) NOT NULL,
    is_completed       TINYINT(1) NOT NULL DEFAULT 0,
    accuracy           DECIMAL(5,2) NULL,
    time_spent_seconds INT UNSIGNED NULL,
    needs_review       TINYINT(1) NOT NULL DEFAULT 0,
    last_studied_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (user_id, lesson_id),
    KEY idx_progress_lesson (lesson_id),
    KEY idx_progress_review (user_id, needs_review),
    CONSTRAINT fk_progress_user
        FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_progress_lesson
        FOREIGN KEY (lesson_id) REFERENCES lessons(id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE user_lesson_sessions (
    id                 VARCHAR(36) NOT NULL DEFAULT (UUID()),
    user_id            VARCHAR(36) NOT NULL,
    lesson_id          VARCHAR(36) NOT NULL,
    earned_xp          INT UNSIGNED NOT NULL DEFAULT 0,
    accuracy           DECIMAL(5,2) NOT NULL,
    time_spent_seconds INT UNSIGNED NOT NULL,
    mastered_words     INT UNSIGNED NOT NULL DEFAULT 0,
    studied_at         TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    KEY idx_sessions_user_date (user_id, studied_at),
    KEY idx_sessions_lesson (lesson_id),
    CONSTRAINT fk_sessions_user
        FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_sessions_lesson
        FOREIGN KEY (lesson_id) REFERENCES lessons(id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE user_question_attempts (
    id              VARCHAR(36) NOT NULL DEFAULT (UUID()),
    user_id         VARCHAR(36) NOT NULL,
    lesson_id       VARCHAR(36) NOT NULL,
    question_id     VARCHAR(36) NOT NULL,
    selected_answer VARCHAR(500) NULL,
    is_correct      TINYINT(1) NOT NULL,
    answered_at     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    KEY idx_attempts_user_correct (user_id, is_correct, answered_at),
    KEY idx_attempts_lesson (lesson_id),
    KEY idx_attempts_question (question_id),
    CONSTRAINT fk_attempts_user
        FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_attempts_lesson
        FOREIGN KEY (lesson_id) REFERENCES lessons(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_attempts_question
        FOREIGN KEY (question_id) REFERENCES questions(id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- TRIGGERS AND VIEWS
-- ============================================================

DELIMITER $$

CREATE TRIGGER trg_after_user_insert
AFTER INSERT ON users
FOR EACH ROW
BEGIN
    INSERT INTO user_settings (user_id)
    VALUES (NEW.id);

    INSERT INTO user_stats (user_id)
    VALUES (NEW.id);
END$$

DELIMITER ;

CREATE VIEW user_tier AS
SELECT
    u.id AS user_id,
    u.full_name,
    s.total_xp,
    s.streak_count,
    s.words_mastered_count,
    CASE
        WHEN s.total_xp < 5000 THEN 'Beginner'
        WHEN s.total_xp < 15000 THEN 'Intermediate'
        WHEN s.total_xp < 30000 THEN 'Advanced'
        ELSE 'Expert'
    END AS tier
FROM users u
JOIN user_stats s ON s.user_id = u.id;

-- ============================================================
-- LARGE CONTENT SEED
-- 48 topics, 192 lessons, and 1920 questions.
-- ============================================================

DROP TEMPORARY TABLE IF EXISTS seed_topics;
CREATE TEMPORARY TABLE seed_topics (
    id       VARCHAR(36) NOT NULL PRIMARY KEY,
    slug     VARCHAR(64) NOT NULL UNIQUE,
    title    VARCHAR(200) NOT NULL,
    level    ENUM('A1','A2','B1','B2','C1','C2') NOT NULL,
    category ENUM('Vocabulary','Grammar') NOT NULL
);

INSERT INTO seed_topics (id, slug, title, level, category) VALUES
('topic-a1-daily-routines', 'a1-daily-routines', 'Daily Routines', 'A1', 'Vocabulary'),
('topic-a1-family-friends', 'a1-family-friends', 'Family and Friends', 'A1', 'Vocabulary'),
('topic-a1-food-drinks', 'a1-food-drinks', 'Food and Drinks', 'A1', 'Vocabulary'),
('topic-a1-home-objects', 'a1-home-objects', 'Home Objects', 'A1', 'Vocabulary'),
('topic-a1-numbers-time', 'a1-numbers-time', 'Numbers and Time', 'A1', 'Vocabulary'),
('topic-a1-colors-clothes', 'a1-colors-clothes', 'Colors and Clothes', 'A1', 'Vocabulary'),
('topic-a1-simple-present', 'a1-simple-present', 'Simple Present', 'A1', 'Grammar'),
('topic-a1-basic-questions', 'a1-basic-questions', 'Basic Questions', 'A1', 'Grammar'),

('topic-a2-travel', 'a2-travel', 'Travel English', 'A2', 'Vocabulary'),
('topic-a2-shopping-money', 'a2-shopping-money', 'Shopping and Money', 'A2', 'Vocabulary'),
('topic-a2-health-fitness', 'a2-health-fitness', 'Health and Fitness', 'A2', 'Vocabulary'),
('topic-a2-weather-seasons', 'a2-weather-seasons', 'Weather and Seasons', 'A2', 'Vocabulary'),
('topic-a2-city-places', 'a2-city-places', 'City Places', 'A2', 'Vocabulary'),
('topic-a2-hobbies-free-time', 'a2-hobbies-free-time', 'Hobbies and Free Time', 'A2', 'Vocabulary'),
('topic-a2-past-simple', 'a2-past-simple', 'Past Simple', 'A2', 'Grammar'),
('topic-a2-comparatives', 'a2-comparatives', 'Comparatives', 'A2', 'Grammar'),

('topic-b1-technology', 'b1-technology', 'Technology', 'B1', 'Vocabulary'),
('topic-b1-workplace', 'b1-workplace', 'Workplace Communication', 'B1', 'Vocabulary'),
('topic-b1-education', 'b1-education', 'Education', 'B1', 'Vocabulary'),
('topic-b1-environment', 'b1-environment', 'Environment', 'B1', 'Vocabulary'),
('topic-b1-social-media', 'b1-social-media', 'Social Media', 'B1', 'Vocabulary'),
('topic-b1-culture-festivals', 'b1-culture-festivals', 'Culture and Festivals', 'B1', 'Vocabulary'),
('topic-b1-present-perfect', 'b1-present-perfect', 'Present Perfect', 'B1', 'Grammar'),
('topic-b1-modal-verbs', 'b1-modal-verbs', 'Modal Verbs', 'B1', 'Grammar'),

('topic-b2-business', 'b2-business', 'Business Communication', 'B2', 'Vocabulary'),
('topic-b2-productivity', 'b2-productivity', 'Productivity', 'B2', 'Vocabulary'),
('topic-b2-leadership', 'b2-leadership', 'Leadership', 'B2', 'Vocabulary'),
('topic-b2-finance-banking', 'b2-finance-banking', 'Finance and Banking', 'B2', 'Vocabulary'),
('topic-b2-media-news', 'b2-media-news', 'Media and News', 'B2', 'Vocabulary'),
('topic-b2-problem-solving', 'b2-problem-solving', 'Problem Solving', 'B2', 'Vocabulary'),
('topic-b2-conditionals', 'b2-conditionals', 'Conditionals', 'B2', 'Grammar'),
('topic-b2-passive-voice', 'b2-passive-voice', 'Passive Voice', 'B2', 'Grammar'),

('topic-c1-academic', 'c1-academic', 'Academic Vocabulary', 'C1', 'Vocabulary'),
('topic-c1-critical-thinking', 'c1-critical-thinking', 'Critical Thinking', 'C1', 'Vocabulary'),
('topic-c1-innovation', 'c1-innovation', 'Innovation', 'C1', 'Vocabulary'),
('topic-c1-global-issues', 'c1-global-issues', 'Global Issues', 'C1', 'Vocabulary'),
('topic-c1-psychology', 'c1-psychology', 'Psychology', 'C1', 'Vocabulary'),
('topic-c1-law-policy', 'c1-law-policy', 'Law and Policy', 'C1', 'Vocabulary'),
('topic-c1-advanced-connectors', 'c1-advanced-connectors', 'Advanced Connectors', 'C1', 'Grammar'),
('topic-c1-nominalisation', 'c1-nominalisation', 'Nominalisation', 'C1', 'Grammar'),

('topic-c2-diplomacy-debate', 'c2-diplomacy-debate', 'Diplomacy and Debate', 'C2', 'Vocabulary'),
('topic-c2-literature-style', 'c2-literature-style', 'Literature and Style', 'C2', 'Vocabulary'),
('topic-c2-philosophy-ethics', 'c2-philosophy-ethics', 'Philosophy and Ethics', 'C2', 'Vocabulary'),
('topic-c2-data-analysis', 'c2-data-analysis', 'Data Analysis', 'C2', 'Vocabulary'),
('topic-c2-entrepreneurship', 'c2-entrepreneurship', 'Entrepreneurship', 'C2', 'Vocabulary'),
('topic-c2-sustainability', 'c2-sustainability', 'Sustainability', 'C2', 'Vocabulary'),
('topic-c2-inversion-emphasis', 'c2-inversion-emphasis', 'Inversion and Emphasis', 'C2', 'Grammar'),
('topic-c2-discourse-markers', 'c2-discourse-markers', 'Discourse Markers', 'C2', 'Grammar');

INSERT INTO topics (id, title, level, category)
SELECT id, title, level, category
FROM seed_topics
ORDER BY level, category, title;

DROP TEMPORARY TABLE IF EXISTS seed_lesson_numbers;
CREATE TEMPORARY TABLE seed_lesson_numbers (
    n SMALLINT UNSIGNED NOT NULL PRIMARY KEY
);

INSERT INTO seed_lesson_numbers (n) VALUES (1), (2), (3), (4);

INSERT INTO lessons (id, topic_id, `order`, xp_reward)
SELECT
    CONCAT('lesson-', t.slug, '-', LPAD(n.n, 2, '0')) AS id,
    t.id AS topic_id,
    n.n AS `order`,
    (
        CASE t.level
            WHEN 'A1' THEN 80
            WHEN 'A2' THEN 110
            WHEN 'B1' THEN 150
            WHEN 'B2' THEN 200
            WHEN 'C1' THEN 260
            ELSE 320
        END
        + (n.n * 10)
    ) AS xp_reward
FROM seed_topics t
CROSS JOIN seed_lesson_numbers n
ORDER BY t.level, t.slug, n.n;

DROP TEMPORARY TABLE IF EXISTS seed_question_templates;
CREATE TEMPORARY TABLE seed_question_templates (
    n             SMALLINT UNSIGNED NOT NULL PRIMARY KEY,
    word_label    VARCHAR(80) NOT NULL,
    answer_label  VARCHAR(200) NOT NULL,
    distractor_a  VARCHAR(120) NOT NULL,
    distractor_b  VARCHAR(120) NOT NULL,
    distractor_c  VARCHAR(120) NOT NULL
);

INSERT INTO seed_question_templates
    (n, word_label, answer_label, distractor_a, distractor_b, distractor_c)
VALUES
(1, 'Core Word', 'A central word or structure used in this topic', 'A random place name', 'A number only', 'An unrelated object'),
(2, 'Useful Phrase', 'A natural phrase for everyday communication', 'A grammar label only', 'A spelling mistake', 'A topic title'),
(3, 'Meaning Check', 'The best meaning in the given context', 'The opposite meaning', 'A very broad meaning', 'A false friend'),
(4, 'Context Clue', 'The clue that fits the sentence situation', 'A clue from another topic', 'A literal translation', 'A punctuation mark'),
(5, 'Collocation', 'Words that commonly appear together', 'Words that sound similar', 'Words in random order', 'Words with no connection'),
(6, 'Grammar Pattern', 'The correct grammar pattern for this item', 'A tense mismatch', 'A missing subject', 'An incorrect word form'),
(7, 'Speaking Task', 'A response that sounds natural in conversation', 'A response that is too formal', 'A response with no answer', 'A response about another topic'),
(8, 'Reading Skill', 'The detail that supports the main idea', 'A detail not stated', 'An opinion without evidence', 'A repeated distractor'),
(9, 'Listening Cue', 'The signal word or phrase that helps understanding', 'Background noise', 'A speaker name only', 'A long pause'),
(10, 'Review Point', 'The key takeaway from this lesson', 'An earlier wrong answer', 'A decorative sentence', 'A topic with no example');

INSERT INTO questions
    (id, lesson_id, word, context_sentence, correct_answer, distractors, image_url)
SELECT
    CONCAT('q-', t.slug, '-', LPAD(ln.n, 2, '0'), '-', LPAD(q.n, 2, '0')) AS id,
    CONCAT('lesson-', t.slug, '-', LPAD(ln.n, 2, '0')) AS lesson_id,
    CONCAT(t.title, ' ', q.word_label, ' L', ln.n, '.', q.n) AS word,
    CONCAT(
        'In ', t.title, ', lesson ', ln.n,
        ' asks learners to practice ', LOWER(q.word_label),
        ' at ', t.level, ' level.'
    ) AS context_sentence,
    CONCAT(q.answer_label, ' for ', t.title, ' at ', t.level, ' level.') AS correct_answer,
    JSON_ARRAY(
        CONCAT(q.distractor_a, ' - ', t.title),
        CONCAT(q.distractor_b, ' - lesson ', ln.n),
        CONCAT(q.distractor_c, ' - ', t.level)
    ) AS distractors,
    NULL AS image_url
FROM seed_topics t
CROSS JOIN seed_lesson_numbers ln
CROSS JOIN seed_question_templates q
ORDER BY t.level, t.slug, ln.n, q.n;

-- ============================================================
-- DEMO USERS AND PROGRESS
-- ============================================================

INSERT INTO users
    (id, email, password_hash, full_name, avatar_url, daily_goal_minutes, current_level)
VALUES
('user-001', 'minh.nguyen@lexirise.vn', '$2b$12$CYnG3OPMUCjO2pcedR.sOupsVGwU5dA6.MwlrUdCeJtKzvedYDjx2', 'Nguyen Quang Minh', 'https://i.pravatar.cc/150?img=11', 10, 'A2'),
('user-002', 'linh.tran@lexirise.vn', '$2b$12$CYnG3OPMUCjO2pcedR.sOupsVGwU5dA6.MwlrUdCeJtKzvedYDjx2', 'Tran Bao Linh', 'https://i.pravatar.cc/150?img=32', 15, 'B1'),
('user-003', 'khoa.le@lexirise.vn', '$2b$12$CYnG3OPMUCjO2pcedR.sOupsVGwU5dA6.MwlrUdCeJtKzvedYDjx2', 'Le Minh Khoa', 'https://i.pravatar.cc/150?img=51', 5, 'B2'),
('user-004', 'ha.pham@lexirise.vn', '$2b$12$CYnG3OPMUCjO2pcedR.sOupsVGwU5dA6.MwlrUdCeJtKzvedYDjx2', 'Pham Thu Ha', 'https://i.pravatar.cc/150?img=47', 10, 'C1'),
('user-005', 'nam.vo@lexirise.vn', '$2b$12$CYnG3OPMUCjO2pcedR.sOupsVGwU5dA6.MwlrUdCeJtKzvedYDjx2', 'Vo Hoang Nam', 'https://i.pravatar.cc/150?img=15', 15, 'B1'),
('user-006', 'anh.do@lexirise.vn', '$2b$12$CYnG3OPMUCjO2pcedR.sOupsVGwU5dA6.MwlrUdCeJtKzvedYDjx2', 'Do Mai Anh', 'https://i.pravatar.cc/150?img=5', 10, 'A1'),
('user-007', 'phuc.dang@lexirise.vn', '$2b$12$CYnG3OPMUCjO2pcedR.sOupsVGwU5dA6.MwlrUdCeJtKzvedYDjx2', 'Dang Gia Phuc', 'https://i.pravatar.cc/150?img=12', 15, 'B2'),
('user-008', 'vy.ho@lexirise.vn', '$2b$12$CYnG3OPMUCjO2pcedR.sOupsVGwU5dA6.MwlrUdCeJtKzvedYDjx2', 'Ho Tuong Vy', 'https://i.pravatar.cc/150?img=26', 10, 'C1'),
('user-009', 'duy.bui@lexirise.vn', '$2b$12$CYnG3OPMUCjO2pcedR.sOupsVGwU5dA6.MwlrUdCeJtKzvedYDjx2', 'Bui Minh Duy', 'https://i.pravatar.cc/150?img=18', 5, 'A2'),
('user-010', 'mai.vo@lexirise.vn', '$2b$12$CYnG3OPMUCjO2pcedR.sOupsVGwU5dA6.MwlrUdCeJtKzvedYDjx2', 'Vo Thanh Mai', 'https://i.pravatar.cc/150?img=44', 15, 'C2');

UPDATE user_settings
SET theme = 'dark'
WHERE user_id IN ('user-003', 'user-004', 'user-008', 'user-010');

INSERT INTO user_progress
    (user_id, lesson_id, is_completed, accuracy, time_spent_seconds, needs_review)
SELECT
    u.id AS user_id,
    l.id AS lesson_id,
    CASE
        WHEN ROUND(55 + (MOD(CRC32(CONCAT(u.id, ':', l.id)), 4500) / 100), 2) >= 65
        THEN 1 ELSE 0
    END AS is_completed,
    ROUND(55 + (MOD(CRC32(CONCAT(u.id, ':', l.id)), 4500) / 100), 2) AS accuracy,
    240 + MOD(CRC32(CONCAT(l.id, ':', u.id)), 1500) AS time_spent_seconds,
    CASE
        WHEN ROUND(55 + (MOD(CRC32(CONCAT(u.id, ':', l.id)), 4500) / 100), 2) < 70
        THEN 1 ELSE 0
    END AS needs_review
FROM users u
JOIN lessons l
    ON MOD(CRC32(CONCAT(u.id, ':', l.id)), 4) = 0
WHERE u.id LIKE 'user-%'
ORDER BY u.id, l.id;

INSERT INTO user_lesson_sessions
    (id, user_id, lesson_id, earned_xp, accuracy, time_spent_seconds, mastered_words, studied_at)
SELECT
    UUID() AS id,
    p.user_id,
    p.lesson_id,
    CASE WHEN p.is_completed = 1 THEN l.xp_reward ELSE 0 END AS earned_xp,
    p.accuracy,
    COALESCE(p.time_spent_seconds, 0) AS time_spent_seconds,
    CASE WHEN p.accuracy >= 90 THEN COALESCE(q.total_questions, 0) ELSE 0 END AS mastered_words,
    TIMESTAMP(DATE_SUB(CURDATE(), INTERVAL MOD(CRC32(CONCAT(p.user_id, ':', p.lesson_id)), 7) DAY), '09:00:00') AS studied_at
FROM user_progress p
JOIN lessons l ON l.id = p.lesson_id
LEFT JOIN (
    SELECT lesson_id, COUNT(*) AS total_questions
    FROM questions
    GROUP BY lesson_id
) q ON q.lesson_id = p.lesson_id;

INSERT INTO user_question_attempts
    (id, user_id, lesson_id, question_id, selected_answer, is_correct, answered_at)
SELECT
    UUID() AS id,
    p.user_id,
    p.lesson_id,
    q.id AS question_id,
    JSON_UNQUOTE(JSON_EXTRACT(q.distractors, '$[0]')) AS selected_answer,
    0 AS is_correct,
    TIMESTAMP(DATE_SUB(CURDATE(), INTERVAL MOD(CRC32(CONCAT(p.user_id, ':', q.id)), 7) DAY), '09:15:00') AS answered_at
FROM user_progress p
JOIN questions q ON q.lesson_id = p.lesson_id
WHERE p.accuracy < 70
  AND MOD(CRC32(CONCAT(p.user_id, ':', q.id)), 3) = 0;

UPDATE user_stats s
JOIN (
    SELECT
        user_id,
        COALESCE(SUM(earned_xp), 0) AS total_xp,
        COALESCE(SUM(mastered_words), 0) AS words_mastered_count,
        COUNT(*) AS session_count
    FROM user_lesson_sessions
    GROUP BY user_id
) x ON x.user_id = s.user_id
SET
    s.total_xp = x.total_xp,
    s.words_mastered_count = x.words_mastered_count,
    s.streak_count = 3 + MOD(CRC32(s.user_id), 40),
    s.last_active_date = CURDATE();

-- ============================================================
-- QUICK CHECKS
-- ============================================================

SELECT 'topics' AS table_name, COUNT(*) AS total_rows FROM topics
UNION ALL
SELECT 'lessons', COUNT(*) FROM lessons
UNION ALL
SELECT 'questions', COUNT(*) FROM questions
UNION ALL
SELECT 'users', COUNT(*) FROM users
UNION ALL
SELECT 'user_progress', COUNT(*) FROM user_progress
UNION ALL
SELECT 'user_lesson_sessions', COUNT(*) FROM user_lesson_sessions
UNION ALL
SELECT 'user_question_attempts', COUNT(*) FROM user_question_attempts;
