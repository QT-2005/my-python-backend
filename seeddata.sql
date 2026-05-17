-- ============================================================
-- EXTRA UNIQUE CONSTRAINTS (ANTI-DUPLICATE)
-- ============================================================

ALTER TABLE topics
ADD CONSTRAINT uq_topic_title_level
UNIQUE(title, level);

ALTER TABLE lessons
ADD CONSTRAINT uq_topic_order
UNIQUE(topic_id, `order`);

ALTER TABLE questions
ADD CONSTRAINT uq_question_word_per_lesson
UNIQUE(lesson_id, word);

-- ============================================================
-- TOPICS
-- ============================================================

INSERT INTO topics (id, title, level, category) VALUES

('topic-a1-family',         'Family and Friends',      'A1', 'Vocabulary'),
('topic-a1-food',           'Food and Drinks',         'A1', 'Vocabulary'),
('topic-a1-school',         'School Life',             'A1', 'Vocabulary'),

('topic-a2-travel',         'Travel English',          'A2', 'Vocabulary'),
('topic-a2-shopping',       'Shopping',                'A2', 'Vocabulary'),
('topic-a2-health',         'Health and Fitness',      'A2', 'Vocabulary'),

('topic-b1-technology',     'Technology',              'B1', 'Vocabulary'),
('topic-b1-workplace',      'Workplace Communication', 'B1', 'Vocabulary'),
('topic-b1-social',         'Social Media',            'B1', 'Vocabulary'),

('topic-b2-business',       'Business Communication',  'B2', 'Vocabulary'),
('topic-b2-productivity',   'Productivity',            'B2', 'Vocabulary'),
('topic-b2-leadership',     'Leadership',              'B2', 'Vocabulary'),

('topic-c1-academic',       'Academic Vocabulary',     'C1', 'Vocabulary'),
('topic-c1-critical',       'Critical Thinking',       'C1', 'Vocabulary');

-- ============================================================
-- LESSONS
-- ============================================================

INSERT INTO lessons (id, topic_id, `order`, xp_reward) VALUES

('lesson-a1-family-01',      'topic-a1-family',       1, 100),
('lesson-a1-family-02',      'topic-a1-family',       2, 120),

('lesson-a1-food-01',        'topic-a1-food',         1, 100),
('lesson-a1-school-01',      'topic-a1-school',       1, 110),

('lesson-a2-travel-01',      'topic-a2-travel',       1, 150),
('lesson-a2-shopping-01',    'topic-a2-shopping',     1, 150),
('lesson-a2-health-01',      'topic-a2-health',       1, 160),

('lesson-b1-tech-01',        'topic-b1-technology',   1, 180),
('lesson-b1-work-01',        'topic-b1-workplace',    1, 180),
('lesson-b1-social-01',      'topic-b1-social',       1, 190),

('lesson-b2-business-01',    'topic-b2-business',     1, 220),
('lesson-b2-productivity-01','topic-b2-productivity', 1, 230),
('lesson-b2-leadership-01',  'topic-b2-leadership',   1, 240),

('lesson-c1-academic-01',    'topic-c1-academic',     1, 300),
('lesson-c1-critical-01',    'topic-c1-critical',     1, 320);

-- ============================================================
-- QUESTIONS
-- ============================================================

INSERT INTO questions
(id, lesson_id, word, context_sentence, correct_answer, distractors, image_url)
VALUES

-- ============================================================
-- A1 FAMILY
-- ============================================================

(
'q-a1-family-001',
'lesson-a1-family-01',
'Relative',
'My relatives visited us during Tet holiday.',
'A member of your family.',
'["Teacher","Customer","Neighbor"]',
NULL
),

(
'q-a1-family-002',
'lesson-a1-family-01',
'Cousin',
'My cousin studies at Hue University.',
'A child of your uncle or aunt.',
'["Brother","Father","Grandfather"]',
NULL
),

(
'q-a1-family-003',
'lesson-a1-family-01',
'Friendly',
'Our new classmates are very friendly.',
'Kind and pleasant toward others.',
'["Hungry","Expensive","Dangerous"]',
NULL
),

(
'q-a1-family-004',
'lesson-a1-family-02',
'Introduce',
'She introduced her best friend to me.',
'To tell people someone’s name for the first time.',
'["Forget","Cancel","Hide"]',
NULL
),

(
'q-a1-family-005',
'lesson-a1-family-02',
'Conversation',
'We had a long conversation after class.',
'A talk between two or more people.',
'["Competition","Celebration","Journey"]',
NULL
),

-- ============================================================
-- A1 FOOD
-- ============================================================

(
'q-a1-food-001',
'lesson-a1-food-01',
'Ingredient',
'Fish sauce is an important ingredient in Vietnamese cooking.',
'One of the foods used to make a meal.',
'["Kitchen","Plate","Spoon"]',
NULL
),

(
'q-a1-food-002',
'lesson-a1-food-01',
'Delicious',
'The bun bo Hue was absolutely delicious.',
'Very pleasant to eat.',
'["Empty","Late","Broken"]',
NULL
),

(
'q-a1-food-003',
'lesson-a1-food-01',
'Recipe',
'My mother taught me a chicken soup recipe.',
'A set of instructions for cooking.',
'["Customer","Waiter","Bill"]',
NULL
),

-- ============================================================
-- A1 SCHOOL
-- ============================================================

(
'q-a1-school-001',
'lesson-a1-school-01',
'Homework',
'I finished my math homework before dinner.',
'School work done at home.',
'["Festival","Vacation","Uniform"]',
NULL
),

(
'q-a1-school-002',
'lesson-a1-school-01',
'Subject',
'English is my favorite subject.',
'An area of study in school.',
'["Classroom","Notebook","Teacher"]',
NULL
),

(
'q-a1-school-003',
'lesson-a1-school-01',
'Library',
'Students are studying quietly in the library.',
'A place where books are kept.',
'["Playground","Restaurant","Hospital"]',
NULL
),

-- ============================================================
-- A2 TRAVEL
-- ============================================================

(
'q-a2-travel-001',
'lesson-a2-travel-01',
'Destination',
'Da Lat is a popular travel destination.',
'A place someone is going to.',
'["Airport","Border","Ticket"]',
NULL
),

(
'q-a2-travel-002',
'lesson-a2-travel-01',
'Reservation',
'I made a hotel reservation online yesterday.',
'An arrangement to save something in advance.',
'["Passport","Map","Schedule"]',
NULL
),

(
'q-a2-travel-003',
'lesson-a2-travel-01',
'Departure',
'The departure time was delayed because of rain.',
'The act of leaving somewhere.',
'["Arrival","Journey","Customs"]',
NULL
),

-- ============================================================
-- A2 SHOPPING
-- ============================================================

(
'q-a2-shopping-001',
'lesson-a2-shopping-01',
'Discount',
'This store offers a big discount on laptops.',
'A reduction in price.',
'["Receipt","Warranty","Package"]',
NULL
),

(
'q-a2-shopping-002',
'lesson-a2-shopping-01',
'Customer',
'The customer asked for a refund.',
'A person who buys goods or services.',
'["Cashier","Manager","Driver"]',
NULL
),

(
'q-a2-shopping-003',
'lesson-a2-shopping-01',
'Purchase',
'I purchased a new backpack yesterday.',
'Something that you buy.',
'["Delivery","Exchange","Advertisement"]',
NULL
),

-- ============================================================
-- A2 HEALTH
-- ============================================================

(
'q-a2-health-001',
'lesson-a2-health-01',
'Exercise',
'Regular exercise helps you stay healthy.',
'Physical activity to improve health.',
'["Medicine","Appointment","Symptom"]',
NULL
),

(
'q-a2-health-002',
'lesson-a2-health-01',
'Balanced',
'A balanced diet includes vegetables and protein.',
'Containing different healthy things in the correct amount.',
'["Frozen","Expired","Artificial"]',
NULL
),

(
'q-a2-health-003',
'lesson-a2-health-01',
'Appointment',
'I booked a dentist appointment for tomorrow.',
'A planned meeting at a specific time.',
'["Treatment","Emergency","Operation"]',
NULL
),

-- ============================================================
-- B1 TECHNOLOGY
-- ============================================================

(
'q-b1-tech-001',
'lesson-b1-tech-01',
'Database',
'The app stores user progress in a database.',
'An organized collection of information.',
'["Keyboard","Battery","Monitor"]',
NULL
),

(
'q-b1-tech-002',
'lesson-b1-tech-01',
'Software',
'Our team develops accounting software.',
'Programs used by computers.',
'["Speaker","Mouse","Cable"]',
NULL
),

(
'q-b1-tech-003',
'lesson-b1-tech-01',
'Security',
'Two-factor authentication improves account security.',
'Protection from danger or attacks.',
'["Display","Signal","Download"]',
NULL
),

(
'q-b1-tech-004',
'lesson-b1-tech-01',
'Update',
'Please update the application to the latest version.',
'To make something more modern or current.',
'["Remove","Destroy","Ignore"]',
NULL
),

-- ============================================================
-- B1 WORKPLACE
-- ============================================================

(
'q-b1-work-001',
'lesson-b1-work-01',
'Deadline',
'The design team must finish before the deadline.',
'A time limit for completing work.',
'["Holiday","Meeting","Interview"]',
NULL
),

(
'q-b1-work-002',
'lesson-b1-work-01',
'Colleague',
'My colleague helped me prepare the presentation.',
'A person you work with.',
'["Client","Competitor","Visitor"]',
NULL
),

(
'q-b1-work-003',
'lesson-b1-work-01',
'Promotion',
'She received a promotion after leading the project successfully.',
'A move to a higher job position.',
'["Transfer","Vacation","Internship"]',
NULL
),

(
'q-b1-work-004',
'lesson-b1-work-01',
'Responsibility',
'Managing customer support is a big responsibility.',
'A duty that you must deal with.',
'["Reward","Permission","Advice"]',
NULL
),

-- ============================================================
-- B1 SOCIAL
-- ============================================================

(
'q-b1-social-001',
'lesson-b1-social-01',
'Influencer',
'The influencer reviewed the new smartphone online.',
'A person who affects other people’s opinions online.',
'["Programmer","Designer","Teacher"]',
NULL
),

(
'q-b1-social-002',
'lesson-b1-social-01',
'Comment',
'Thousands of users left positive comments.',
'A written opinion online.',
'["Password","Account","Device"]',
NULL
),

(
'q-b1-social-003',
'lesson-b1-social-01',
'Viral',
'The funny video quickly became viral.',
'Becoming very popular on the internet.',
'["Private","Formal","Secure"]',
NULL
),

-- ============================================================
-- B2 BUSINESS
-- ============================================================

(
'q-b2-business-001',
'lesson-b2-business-01',
'Negotiation',
'The salary negotiation lasted nearly two hours.',
'A discussion to reach an agreement.',
'["Celebration","Competition","Vacation"]',
NULL
),

(
'q-b2-business-002',
'lesson-b2-business-01',
'Strategy',
'The company changed its marketing strategy this year.',
'A plan designed to achieve success.',
'["Tradition","Accident","Complaint"]',
NULL
),

(
'q-b2-business-003',
'lesson-b2-business-01',
'Leverage',
'Startups often leverage social media to gain attention.',
'Use something effectively for advantage.',
'["Ignore","Abandon","Reject"]',
NULL
),

(
'q-b2-business-004',
'lesson-b2-business-01',
'Revenue',
'The business increased its annual revenue significantly.',
'Income generated by a company.',
'["Debt","Loss","Salary"]',
NULL
),

-- ============================================================
-- B2 PRODUCTIVITY
-- ============================================================

(
'q-b2-productivity-001',
'lesson-b2-productivity-01',
'Prioritize',
'Students should prioritize important assignments first.',
'To decide what is most important.',
'["Delay","Avoid","Forget"]',
NULL
),

(
'q-b2-productivity-002',
'lesson-b2-productivity-01',
'Efficiency',
'Automation improves workplace efficiency.',
'The ability to work well without wasting resources.',
'["Confusion","Pressure","Weakness"]',
NULL
),

(
'q-b2-productivity-003',
'lesson-b2-productivity-01',
'Distraction',
'Mobile games can become a distraction during study time.',
'Something that takes attention away.',
'["Motivation","Schedule","Achievement"]',
NULL
),

(
'q-b2-productivity-004',
'lesson-b2-productivity-01',
'Multitasking',
'Multitasking sometimes reduces concentration.',
'Doing several tasks at the same time.',
'["Planning","Research","Training"]',
NULL
),

-- ============================================================
-- B2 LEADERSHIP
-- ============================================================

(
'q-b2-leadership-001',
'lesson-b2-leadership-01',
'Motivate',
'Good managers motivate their teams regularly.',
'To encourage someone to act.',
'["Punish","Ignore","Replace"]',
NULL
),

(
'q-b2-leadership-002',
'lesson-b2-leadership-01',
'Delegate',
'Leaders should delegate smaller tasks effectively.',
'To give work to another person.',
'["Cancel","Repeat","Collect"]',
NULL
),

(
'q-b2-leadership-003',
'lesson-b2-leadership-01',
'Vision',
'The CEO shared her long-term vision for the company.',
'An idea of what the future should be like.',
'["Routine","Weakness","Habit"]',
NULL
),

-- ============================================================
-- C1 ACADEMIC
-- ============================================================

(
'q-c1-academic-001',
'lesson-c1-academic-01',
'Hypothesis',
'Researchers tested the hypothesis carefully.',
'An explanation that can be tested scientifically.',
'["Conclusion","Memory","Emotion"]',
NULL
),

(
'q-c1-academic-002',
'lesson-c1-academic-01',
'Methodology',
'The thesis explains its research methodology clearly.',
'A system of methods used in research.',
'["Prediction","Tradition","Assumption"]',
NULL
),

(
'q-c1-academic-003',
'lesson-c1-academic-01',
'Interpretation',
'The interpretation of the data was controversial.',
'An explanation of meaning.',
'["Calculation","Translation","Measurement"]',
NULL
),

-- ============================================================
-- C1 CRITICAL THINKING
-- ============================================================

(
'q-c1-critical-001',
'lesson-c1-critical-01',
'Ambiguity',
'The statement contains considerable ambiguity.',
'Something unclear with multiple meanings.',
'["Accuracy","Confidence","Honesty"]',
NULL
),

(
'q-c1-critical-002',
'lesson-c1-critical-01',
'Bias',
'Media bias can influence public opinion.',
'An unfair preference toward something.',
'["Evidence","Logic","Precision"]',
NULL
),

(
'q-c1-critical-003',
'lesson-c1-critical-01',
'Rational',
'Consumers should make rational decisions.',
'Based on reason and logic.',
'["Emotional","Sudden","Careless"]',
NULL
);

-- ============================================================
-- USERS
-- ============================================================

INSERT INTO users
(id, email, password_hash, full_name, avatar_url, daily_goal_minutes, current_level)
VALUES

(
'user-001',
'minh.nguyen@lexirise.vn',
'$2a$10$lexirisehashedpassword001',
'Nguyen Quang Minh',
'https://i.pravatar.cc/150?img=11',
10,
'A2'
),

(
'user-002',
'linh.tran@lexirise.vn',
'$2a$10$lexirisehashedpassword002',
'Tran Bao Linh',
'https://i.pravatar.cc/150?img=32',
15,
'B1'
),

(
'user-003',
'khoa.le@lexirise.vn',
'$2a$10$lexirisehashedpassword003',
'Le Minh Khoa',
'https://i.pravatar.cc/150?img=51',
5,
'B2'
),

(
'user-004',
'ha.pham@lexirise.vn',
'$2a$10$lexirisehashedpassword004',
'Pham Thu Ha',
'https://i.pravatar.cc/150?img=47',
10,
'C1'
),

(
'user-005',
'nam.vo@lexirise.vn',
'$2a$10$lexirisehashedpassword005',
'Vo Hoang Nam',
'https://i.pravatar.cc/150?img=15',
15,
'B1'
);

-- ============================================================
-- USER STATS
-- trigger tạo row tự động -> UPDATE
-- ============================================================

UPDATE user_stats
SET total_xp = 1200,
    streak_count = 5,
    words_mastered_count = 42,
    last_active_date = CURDATE()
WHERE user_id = 'user-001';

UPDATE user_stats
SET total_xp = 5600,
    streak_count = 14,
    words_mastered_count = 138,
    last_active_date = CURDATE()
WHERE user_id = 'user-002';

UPDATE user_stats
SET total_xp = 10450,
    streak_count = 22,
    words_mastered_count = 241,
    last_active_date = CURDATE()
WHERE user_id = 'user-003';

UPDATE user_stats
SET total_xp = 18700,
    streak_count = 40,
    words_mastered_count = 490,
    last_active_date = CURDATE()
WHERE user_id = 'user-004';

UPDATE user_stats
SET total_xp = 7200,
    streak_count = 16,
    words_mastered_count = 170,
    last_active_date = CURDATE()
WHERE user_id = 'user-005';

-- ============================================================
-- USER PROGRESS
-- ============================================================

INSERT INTO user_progress
(user_id, lesson_id, is_completed, accuracy, time_spent_seconds)
VALUES

('user-001','lesson-a1-family-01',1,92.50,420),
('user-001','lesson-a1-food-01',1,88.00,510),
('user-001','lesson-a2-travel-01',0,61.20,630),

('user-002','lesson-a2-travel-01',1,91.30,700),
('user-002','lesson-b1-tech-01',1,86.40,830),
('user-002','lesson-b1-work-01',1,89.90,790),

('user-003','lesson-b1-social-01',1,94.10,880),
('user-003','lesson-b2-business-01',1,92.70,960),
('user-003','lesson-b2-productivity-01',0,74.30,1100),

('user-004','lesson-b2-leadership-01',1,96.50,1300),
('user-004','lesson-c1-academic-01',1,93.20,1500),
('user-004','lesson-c1-critical-01',1,95.80,1700),

('user-005','lesson-b1-work-01',1,84.20,760),
('user-005','lesson-b2-business-01',0,68.40,980);