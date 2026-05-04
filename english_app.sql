-- ============================================================
-- LexiRise Database Schema (MySQL)
-- ============================================================

CREATE DATABASE IF NOT EXISTS lexirise
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE lexirise;

-- ============================================================
-- NHÓM 1: NGƯỜI DÙNG & CẤU HÌNH
-- ============================================================

CREATE TABLE users (
    id            CHAR(36)        NOT NULL DEFAULT (UUID()),
    email         VARCHAR(255)    NOT NULL,
    password_hash VARCHAR(255)    NOT NULL,
    full_name     VARCHAR(150)    NOT NULL,
    avatar_url    VARCHAR(500)        NULL,
    daily_goal_minutes TINYINT UNSIGNED NOT NULL DEFAULT 10
                        COMMENT '5, 10, or 15 minutes',
    current_level ENUM('A1','A2','B1','B2','C1','C2')
                        NOT NULL DEFAULT 'A1',
    created_at    TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP
                        ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    UNIQUE KEY uq_users_email (email)
) ENGINE=InnoDB COMMENT='Tài khoản người dùng';

-- ------------------------------------------------------------

CREATE TABLE user_settings (
    user_id                CHAR(36)  NOT NULL,
    theme                  ENUM('light','dark') NOT NULL DEFAULT 'light',
    high_contrast_borders  TINYINT(1)           NOT NULL DEFAULT 0,
    notifications_enabled  TINYINT(1)           NOT NULL DEFAULT 1,
    updated_at             TIMESTAMP  NOT NULL DEFAULT CURRENT_TIMESTAMP
                               ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (user_id),
    CONSTRAINT fk_usettings_user
        FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB COMMENT='Tuỳ chỉnh giao diện & thông báo';

-- ============================================================
-- NHÓM 2: NỘI DUNG HỌC TẬP
-- ============================================================

CREATE TABLE topics (
    id         CHAR(36)     NOT NULL DEFAULT (UUID()),
    title      VARCHAR(200) NOT NULL,
    level      ENUM('A1','A2','B1','B2','C1','C2') NOT NULL,
    category   ENUM('Vocabulary','Grammar')         NOT NULL,
    created_at TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    KEY idx_topics_level    (level),
    KEY idx_topics_category (category)
) ENGINE=InnoDB COMMENT='Chủ đề học tập';

-- ------------------------------------------------------------

CREATE TABLE lessons (
    id         CHAR(36)         NOT NULL DEFAULT (UUID()),
    topic_id   CHAR(36)         NOT NULL,
    `order`    SMALLINT UNSIGNED NOT NULL DEFAULT 1
                   COMMENT 'Thứ tự bài trong chủ đề',
    xp_reward  SMALLINT UNSIGNED NOT NULL DEFAULT 100
                   COMMENT 'XP thưởng khi hoàn thành bài',
    created_at TIMESTAMP        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    KEY idx_lessons_topic (`topic_id`, `order`),
    CONSTRAINT fk_lessons_topic
        FOREIGN KEY (topic_id) REFERENCES topics(id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB COMMENT='Bài học trong từng chủ đề';

-- ------------------------------------------------------------

CREATE TABLE questions (
    id               CHAR(36)     NOT NULL DEFAULT (UUID()),
    lesson_id        CHAR(36)     NOT NULL,
    word             VARCHAR(200) NOT NULL  COMMENT 'Từ khoá chính, vd: Ephemeral',
    context_sentence TEXT             NULL  COMMENT 'Câu ví dụ minh hoạ',
    correct_answer   VARCHAR(500) NOT NULL  COMMENT 'Định nghĩa / đáp án đúng',
    -- Lưu dưới dạng JSON array, vd: ["fleeting","permanent","rigid"]
    distractors      JSON             NULL  COMMENT 'Danh sách đáp án sai',
    image_url        VARCHAR(500)     NULL  COMMENT 'Visual Anchor – URL ảnh gợi ý',
    created_at       TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    KEY idx_questions_lesson (lesson_id),
    CONSTRAINT fk_questions_lesson
        FOREIGN KEY (lesson_id) REFERENCES lessons(id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB COMMENT='Flashcard / câu hỏi trong bài học';

-- ============================================================
-- NHÓM 3: TIẾN TRÌNH & THỐNG KÊ
-- ============================================================

CREATE TABLE user_progress (
    user_id           CHAR(36)         NOT NULL,
    lesson_id         CHAR(36)         NOT NULL,
    is_completed      TINYINT(1)       NOT NULL DEFAULT 0,
    accuracy          DECIMAL(5,2)         NULL
                          COMMENT 'Tỉ lệ đúng 0–100 (%), vd: 94.50',
    time_spent_seconds INT UNSIGNED        NULL
                          COMMENT 'Thời gian làm bài tính bằng giây',
    last_studied_at   TIMESTAMP        NOT NULL DEFAULT CURRENT_TIMESTAMP
                          ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (user_id, lesson_id),
    KEY idx_progress_lesson (lesson_id),
    CONSTRAINT fk_progress_user
        FOREIGN KEY (user_id)   REFERENCES users(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_progress_lesson
        FOREIGN KEY (lesson_id) REFERENCES lessons(id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB COMMENT='Tiến trình học bài của người dùng';

-- ------------------------------------------------------------

CREATE TABLE user_stats (
    user_id              CHAR(36)       NOT NULL,
    total_xp             INT UNSIGNED   NOT NULL DEFAULT 0,
    streak_count         SMALLINT UNSIGNED NOT NULL DEFAULT 0
                             COMMENT 'Số ngày học liên tiếp hiện tại',
    last_active_date     DATE               NULL
                             COMMENT 'Ngày hoạt động gần nhất – dùng tính streak',
    words_mastered_count INT UNSIGNED   NOT NULL DEFAULT 0,
    updated_at           TIMESTAMP      NOT NULL DEFAULT CURRENT_TIMESTAMP
                             ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (user_id),
    CONSTRAINT fk_stats_user
        FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB COMMENT='Tổng hợp XP, streak và từ vựng đã thành thạo';

-- ============================================================
-- TRIGGER: Tự động tạo user_settings & user_stats sau khi
--          đăng ký tài khoản mới.
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

-- ============================================================
-- VIEW: user_tier – Cấp bậc người dùng dựa trên total_xp
-- ============================================================

CREATE VIEW user_tier AS
SELECT
    u.id                           AS user_id,
    u.full_name,
    s.total_xp,
    s.streak_count,
    s.words_mastered_count,
    CASE
        WHEN s.total_xp <  5000  THEN 'Beginner'
        WHEN s.total_xp < 15000  THEN 'Intermediate'
        ELSE                          'Advanced'
    END                            AS tier
FROM users  u
JOIN user_stats s ON s.user_id = u.id;

-- ============================================================
-- DỮ LIỆU MẪU (Seed Data)
-- ============================================================

-- Topic mẫu
INSERT INTO topics (id, title, level, category) VALUES
    ('topic-001', 'Business Negotiation', 'B2', 'Vocabulary'),
    ('topic-002', 'Academic Writing',     'C1', 'Grammar');

-- Lesson mẫu
INSERT INTO lessons (id, topic_id, `order`, xp_reward) VALUES
    ('lesson-001', 'topic-001', 1, 200),
    ('lesson-002', 'topic-001', 2, 250);

-- Question / Flashcard mẫu
INSERT INTO questions
    (id, lesson_id, word, context_sentence, correct_answer, distractors, image_url)
VALUES (
    'q-001',
    'lesson-001',
    'Ephemeral',
    'The beauty of cherry blossoms is ephemeral, lasting only a few days.',
    'Lasting for a very short time; transitory.',
    '["Permanent","Everlasting","Durable"]',
    'https://cdn.lexirise.app/images/ephemeral.jpg'
),
(
    'q-002',
    'lesson-001',
    'Leverage',
    'We can leverage our existing network to close the deal faster.',
    'Use something to maximum advantage.',
    '["Ignore","Undermine","Abandon"]',
    NULL
);
