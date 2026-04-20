-- ============================================================
--  Chạy file này trong MySQL Workbench hoặc terminal MySQL
--  trước khi khởi động server
-- ============================================================

-- 1. Tạo database (chỉ tạo nếu chưa có)
CREATE DATABASE IF NOT EXISTS dict_app
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE dict_app;

-- 2. Tạo bảng words
CREATE TABLE IF NOT EXISTS words (
    word_id       INT          NOT NULL AUTO_INCREMENT,
    word_en       VARCHAR(100) NOT NULL UNIQUE COMMENT 'Từ tiếng Anh',
    word_vn       VARCHAR(200) NOT NULL              COMMENT 'Nghĩa tiếng Việt',
    pronunciation VARCHAR(100)                       COMMENT 'Phiên âm IPA, vd: /kæt/',
    word_type     VARCHAR(30)                        COMMENT 'Loại từ: noun/verb/adj/adv',
    example_en    TEXT                               COMMENT 'Câu ví dụ tiếng Anh',
    example_vn    TEXT                               COMMENT 'Câu ví dụ tiếng Việt',
    level         ENUM('A1','A2','B1','B2','C1','C2') COMMENT 'Trình độ',
    topic         VARCHAR(50)                        COMMENT 'Chủ đề: animals/food/travel...',
    PRIMARY KEY (word_id),
    INDEX idx_word_en  (word_en),
    INDEX idx_topic    (topic),
    INDEX idx_level    (level),
    INDEX idx_word_type (word_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. Kiểm tra
SELECT 'Database và bảng đã tạo thành công!' AS status;
SHOW TABLES;