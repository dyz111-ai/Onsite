-- =============================================
-- 数据库建表SQL导出
-- 导出时间: 2026-01-02 23:38:45
-- 数据库: railway
-- =============================================




-- =============================================
-- 表: admin
-- =============================================

DROP TABLE IF EXISTS admin CASCADE;

CREATE TABLE admin (admin_id INTEGER NOT NULL ,
    account VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL);

ALTER TABLE admin ADD CONSTRAINT admin_pkey PRIMARY KEY (admin_id);


-- =============================================
-- 表: competition
-- =============================================

DROP TABLE IF EXISTS competition CASCADE;

CREATE TABLE competition (competition_id INTEGER NOT NULL DEFAULT ,
    created_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    status VARCHAR(20) NOT NULL,
    type VARCHAR(10) NOT NULL,
    number INTEGER NOT NULL);

ALTER TABLE competition ADD CONSTRAINT competition_pkey PRIMARY KEY (competition_id);




-- =============================================
-- 表: participant
-- =============================================

DROP TABLE IF EXISTS participant CASCADE;

CREATE TABLE participant (participant_id INTEGER NOT NULL DEFAULT ,
    account VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL);

ALTER TABLE participant ADD CONSTRAINT participant_pkey PRIMARY KEY (participant_id);


-- =============================================
-- 表: render
-- =============================================

DROP TABLE IF EXISTS render CASCADE;

CREATE TABLE render (render_id INTEGER NOT NULL DEFAULT nextval('render_render_id_seq'::regclass),
    user_id INTEGER NOT NULL,
    status VARCHAR(10) NOT NULL,
    created_time TIMESTAMP NOT NULL,
    render_cost DOUBLE PRECISION,
    name TEXT);

ALTER TABLE render ADD CONSTRAINT render_pkey PRIMARY KEY (render_id);

ALTER TABLE render ADD CONSTRAINT fk_render_user FOREIGN KEY (user_id) REFERENCES participant(participant_id);


-- =============================================
-- 表: test_task
-- =============================================

DROP TABLE IF EXISTS test_task CASCADE;

CREATE TABLE test_task (training_id INTEGER NOT NULL,
    competition_id INTEGER NOT NULL,
    score DOUBLE PRECISION);

ALTER TABLE test_task ADD CONSTRAINT test_task_pkey PRIMARY KEY (training_id);

ALTER TABLE test_task ADD CONSTRAINT fk_test_training FOREIGN KEY (training_id) REFERENCES training_task(training_id);

ALTER TABLE test_task ADD CONSTRAINT fk_test_competition FOREIGN KEY (competition_id) REFERENCES competition(competition_id);


-- =============================================
-- 表: training_render_relation
-- =============================================

DROP TABLE IF EXISTS training_render_relation CASCADE;

CREATE TABLE training_render_relation (training_id INTEGER NOT NULL,
    render_id INTEGER NOT NULL);

ALTER TABLE training_render_relation ADD CONSTRAINT training_render_relation_pkey PRIMARY KEY (training_id, render_id);

ALTER TABLE training_render_relation ADD CONSTRAINT fk_training_relation FOREIGN KEY (training_id) REFERENCES training_task(training_id);

ALTER TABLE training_render_relation ADD CONSTRAINT fk_render_relation FOREIGN KEY (render_id) REFERENCES render(render_id);


-- =============================================
-- 表: training_task
-- =============================================

DROP TABLE IF EXISTS training_task CASCADE;

CREATE TABLE training_task (training_id INTEGER NOT NULL DEFAULT nextval('training_task_training_id_seq'::regclass),
    user_id INTEGER NOT NULL,
    created_time TIMESTAMP NOT NULL,
    status VARCHAR(20) NOT NULL,
    train_cost DOUBLE PRECISION,
    test_score DOUBLE PRECISION,
    total_score DOUBLE PRECISION,
    server_port INTEGER,
    end_time TIMESTAMP);

ALTER TABLE training_task ADD CONSTRAINT training_task_pkey PRIMARY KEY (training_id);

ALTER TABLE training_task ADD CONSTRAINT fk_training_user FOREIGN KEY (user_id) REFERENCES participant(participant_id);


-- =============================================
-- 序列 (Sequences)
-- =============================================

