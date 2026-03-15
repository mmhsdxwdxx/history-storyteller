-- 数据库迁移脚本：从旧版本升级
-- 执行方式：在容器启动时自动运行

-- 添加旧数据兼容字段（如果不存在）
ALTER TABLE contents ADD COLUMN IF NOT EXISTS vernacular_text TEXT;
ALTER TABLE contents ADD COLUMN IF NOT EXISTS humorous_text TEXT;
ALTER TABLE contents ADD COLUMN IF NOT EXISTS legacy_provider VARCHAR(50);

-- 创建 generation_results 表（如果不存在）
CREATE TABLE IF NOT EXISTS generation_results (
    id SERIAL PRIMARY KEY,
    content_id INTEGER NOT NULL REFERENCES contents(id),
    provider VARCHAR(50) NOT NULL,
    vernacular_text TEXT,
    humorous_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS ix_generation_results_content_id ON generation_results(content_id);
