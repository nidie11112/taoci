-- 保研导师信息搜集网站数据库初始化脚本

-- 创建扩展（如果需要）
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 创建表空间（可选）
-- CREATE TABLESPACE taoci_ts LOCATION '/var/lib/postgresql/data/taoci';

-- 设置搜索路径
SET search_path TO public;

-- 导师信息表
CREATE TABLE IF NOT EXISTS professors (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    university VARCHAR(200) NOT NULL,
    department VARCHAR(200),
    title VARCHAR(100),
    research_fields TEXT[],  -- 研究方向数组
    personal_page_url VARCHAR(500),
    email VARCHAR(100),
    phone VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP WITH TIME ZONE,

    -- 索引
    CONSTRAINT professors_email_key UNIQUE (email),
    CONSTRAINT professors_personal_page_url_key UNIQUE (personal_page_url)
);

-- 为常用查询字段创建索引
CREATE INDEX IF NOT EXISTS idx_professors_university ON professors(university);
CREATE INDEX IF NOT EXISTS idx_professors_department ON professors(department);
CREATE INDEX IF NOT EXISTS idx_professors_research_fields ON professors USING GIN(research_fields);
CREATE INDEX IF NOT EXISTS idx_professors_created_at ON professors(created_at);

-- 导师评价表
CREATE TABLE IF NOT EXISTS professor_evaluations (
    id SERIAL PRIMARY KEY,
    professor_id INTEGER NOT NULL REFERENCES professors(id) ON DELETE CASCADE,
    source VARCHAR(50) NOT NULL CHECK (source IN ('excel', 'github', 'manual', 'web')),
    personality_score DECIMAL(3,2) CHECK (personality_score >= 1 AND personality_score <= 5),  -- 人品得分 1-5
    group_atmosphere TEXT,  -- 课题组氛围描述
    student_comments TEXT,
    evaluation_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- 约束
    CONSTRAINT fk_professor_evaluations_professor FOREIGN KEY (professor_id) REFERENCES professors(id),
    CONSTRAINT unique_evaluation_source UNIQUE (professor_id, source, evaluation_date)
);

CREATE INDEX IF NOT EXISTS idx_professor_evaluations_professor_id ON professor_evaluations(professor_id);
CREATE INDEX IF NOT EXISTS idx_professor_evaluations_source ON professor_evaluations(source);
CREATE INDEX IF NOT EXISTS idx_professor_evaluations_personality_score ON professor_evaluations(personality_score);

-- 学术论文表
CREATE TABLE IF NOT EXISTS academic_papers (
    id SERIAL PRIMARY KEY,
    professor_id INTEGER NOT NULL REFERENCES professors(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    authors TEXT[],
    publication_venue VARCHAR(300),
    publication_year INTEGER CHECK (publication_year >= 1900 AND publication_year <= EXTRACT(YEAR FROM CURRENT_DATE) + 5),
    abstract TEXT,
    keywords TEXT[],
    pdf_url VARCHAR(500),
    citations INTEGER DEFAULT 0 CHECK (citations >= 0),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- 约束
    CONSTRAINT fk_academic_papers_professor FOREIGN KEY (professor_id) REFERENCES professors(id)
);

CREATE INDEX IF NOT EXISTS idx_academic_papers_professor_id ON academic_papers(professor_id);
CREATE INDEX IF NOT EXISTS idx_academic_papers_publication_year ON academic_papers(publication_year);
CREATE INDEX IF NOT EXISTS idx_academic_papers_keywords ON academic_papers USING GIN(keywords);

-- 学生信息表
CREATE TABLE IF NOT EXISTS students (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    university VARCHAR(200) NOT NULL,
    major VARCHAR(200),
    gpa DECIMAL(3,2) CHECK (gpa >= 0 AND gpa <= 5),
    gpa_ranking INTEGER CHECK (gpa_ranking >= 1),  -- 专业排名
    research_experience JSONB DEFAULT '[]',  -- 科研经历
    competition_awards JSONB DEFAULT '[]',  -- 竞赛获奖
    skills TEXT[] DEFAULT '{}',
    resume_pdf_path VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP WITH TIME ZONE,

    -- 约束
    CONSTRAINT students_gpa_check CHECK (gpa >= 0 AND gpa <= 5)
);

CREATE INDEX IF NOT EXISTS idx_students_university ON students(university);
CREATE INDEX IF NOT EXISTS idx_students_gpa ON students(gpa);
CREATE INDEX IF NOT EXISTS idx_students_created_at ON students(created_at);

-- 匹配记录表
CREATE TABLE IF NOT EXISTS matches (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    professor_id INTEGER NOT NULL REFERENCES professors(id) ON DELETE CASCADE,
    research_match_score DECIMAL(5,4) CHECK (research_match_score >= 0 AND research_match_score <= 1),  -- 研究方向匹配度
    background_match_score DECIMAL(5,4) CHECK (background_match_score >= 0 AND background_match_score <= 1), -- 背景匹配度
    personality_match_score DECIMAL(5,4) CHECK (personality_match_score >= 0 AND personality_match_score <= 1), -- 性格匹配度
    overall_score DECIMAL(5,4) CHECK (overall_score >= 0 AND overall_score <= 1),  -- 综合匹配度
    admission_probability DECIMAL(5,4) CHECK (admission_probability >= 0 AND admission_probability <= 1),  -- 录取概率
    match_reasons TEXT,  -- 匹配原因分析
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- 约束
    CONSTRAINT fk_matches_student FOREIGN KEY (student_id) REFERENCES students(id),
    CONSTRAINT fk_matches_professor FOREIGN KEY (professor_id) REFERENCES professors(id),
    CONSTRAINT unique_match UNIQUE (student_id, professor_id)
);

CREATE INDEX IF NOT EXISTS idx_matches_student_id ON matches(student_id);
CREATE INDEX IF NOT EXISTS idx_matches_professor_id ON matches(professor_id);
CREATE INDEX IF NOT EXISTS idx_matches_overall_score ON matches(overall_score DESC);
CREATE INDEX IF NOT EXISTS idx_matches_admission_probability ON matches(admission_probability DESC);

-- 文书模板表
CREATE TABLE IF NOT EXISTS document_templates (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    category VARCHAR(100) CHECK (category IN ('通用', '力学', '机械', '智能制造', '其他')),
    content_template TEXT NOT NULL,
    variables JSONB DEFAULT '{}',  -- 模板变量定义
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP WITH TIME ZONE,

    -- 约束
    CONSTRAINT document_templates_name_key UNIQUE (name)
);

CREATE INDEX IF NOT EXISTS idx_document_templates_category ON document_templates(category);

-- 生成文书表
CREATE TABLE IF NOT EXISTS generated_documents (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    professor_id INTEGER REFERENCES professors(id) ON DELETE SET NULL,
    template_id INTEGER REFERENCES document_templates(id) ON DELETE SET NULL,
    document_type VARCHAR(100) NOT NULL CHECK (document_type IN ('套磁信', '个人陈述', '自我介绍', '推荐信', '其他')),
    content TEXT NOT NULL,
    file_path VARCHAR(500),
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- 约束
    CONSTRAINT fk_generated_documents_student FOREIGN KEY (student_id) REFERENCES students(id),
    CONSTRAINT fk_generated_documents_professor FOREIGN KEY (professor_id) REFERENCES professors(id),
    CONSTRAINT fk_generated_documents_template FOREIGN KEY (template_id) REFERENCES document_templates(id)
);

CREATE INDEX IF NOT EXISTS idx_generated_documents_student_id ON generated_documents(student_id);
CREATE INDEX IF NOT EXISTS idx_generated_documents_professor_id ON generated_documents(professor_id);
CREATE INDEX IF NOT EXISTS idx_generated_documents_document_type ON generated_documents(document_type);

-- 用户表（如果实现用户系统）
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);

-- 创建更新时间触发器函数
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 为需要更新时间的表创建触发器
DO $$
BEGIN
    -- professors 表
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_professors_updated_at') THEN
        CREATE TRIGGER update_professors_updated_at
            BEFORE UPDATE ON professors
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
    END IF;

    -- students 表
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_students_updated_at') THEN
        CREATE TRIGGER update_students_updated_at
            BEFORE UPDATE ON students
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
    END IF;

    -- document_templates 表
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_document_templates_updated_at') THEN
        CREATE TRIGGER update_document_templates_updated_at
            BEFORE UPDATE ON document_templates
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
    END IF;

    -- professor_evaluations 表
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_professor_evaluations_updated_at') THEN
        CREATE TRIGGER update_professor_evaluations_updated_at
            BEFORE UPDATE ON professor_evaluations
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
    END IF;
END $$;

-- 插入初始数据（文书模板示例）
INSERT INTO document_templates (name, category, content_template, variables) VALUES
('通用套磁信模板', '通用', '
尊敬的{professor_title}{professor_name}老师：

您好！

我是{student_university}{student_major}专业的{student_name}，目前正在申请贵校{professor_department}的推免研究生。通过阅读您的研究论文，我对您的研究方向，特别是{research_field}领域产生了浓厚的兴趣。

我在本科阶段学习了{relevant_courses}等课程，并在{research_experience}等方面有一定的研究经验。我的GPA为{student_gpa}，专业排名{student_ranking}，曾获得{competition_awards}等奖励。

我认为我的学术背景和研究兴趣与您的研究方向高度契合，特别是在{specifc_match_point}方面。如果能有机会在您的指导下继续深造，我将倍感荣幸。

随信附上我的个人简历，恳请您审阅。期待您的回复！

祝工作顺利，身体健康！

此致
敬礼！

{student_name}
{date}
',
'{"professor_title": "职称", "professor_name": "导师姓名", "professor_department": "院系", "student_university": "学生学校", "student_major": "学生专业", "student_name": "学生姓名", "research_field": "研究方向", "relevant_courses": "相关课程", "research_experience": "科研经历", "student_gpa": "GPA", "student_ranking": "专业排名", "competition_awards": "竞赛获奖", "specifc_match_point": "具体匹配点", "date": "日期"}'),

('力学方向套磁信模板', '力学', '
尊敬的{professor_title}{professor_name}老师：

您好！

我是{student_university}工程力学专业的{student_name}，目前正在申请贵校力学系的推免研究生。我仔细研读了您关于{research_topic}的研究工作，对您提出的{research_method}方法深感兴趣。

在本科阶段，我系统学习了《理论力学》、《材料力学》、《流体力学》等核心课程，并在{research_project}项目中，运用{relevant_technique}方法研究了{research_problem}问题，相关成果{research_output}。

我的学术背景和研究兴趣与您在{specifc_research_area}的研究方向高度契合。我希望能够在您的指导下，在{research_direction}领域进行深入研究。

随信附上我的个人简历和成绩单，恳请您审阅。期待您的回复！

祝科研顺利！

此致
敬礼！

{student_name}
{date}
',
'{"professor_title": "职称", "professor_name": "导师姓名", "student_university": "学生学校", "student_name": "学生姓名", "research_topic": "研究主题", "research_method": "研究方法", "research_project": "科研项目", "relevant_technique": "相关技术", "research_problem": "研究问题", "research_output": "研究成果", "specifc_research_area": "具体研究领域", "research_direction": "研究方向", "date": "日期"}')

ON CONFLICT (name) DO NOTHING;

-- 输出完成信息
DO $$
BEGIN
    RAISE NOTICE '数据库初始化完成！';
    RAISE NOTICE '创建的表: professors, professor_evaluations, academic_papers, students, matches, document_templates, generated_documents, users';
    RAISE NOTICE '插入的初始数据: 2个文书模板';
END $$;