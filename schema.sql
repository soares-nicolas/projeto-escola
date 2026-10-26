-- =====================================================
-- Sistema Escola - Schema PostgreSQL
-- Uso: psql -U postgres -d escola -f schema.sql
-- =====================================================

CREATE EXTENSION IF NOT EXISTS pgcrypto;  -- para hash de senha (crypt / gen_salt)

DROP TABLE IF EXISTS matriculas;
DROP TABLE IF EXISTS alunos;
DROP TABLE IF EXISTS cursos;
DROP TABLE IF EXISTS usuarios;

-- Usuários do sistema (login)
CREATE TABLE usuarios (
    id         SERIAL PRIMARY KEY,
    nome       VARCHAR(100) NOT NULL,
    login      VARCHAR(50)  NOT NULL UNIQUE,
    senha_hash TEXT         NOT NULL
);

CREATE TABLE alunos (
    id              SERIAL PRIMARY KEY,
    nome            VARCHAR(100) NOT NULL,
    email           VARCHAR(100) NOT NULL UNIQUE,
    data_nascimento DATE
);

CREATE TABLE cursos (
    id            SERIAL PRIMARY KEY,
    nome          VARCHAR(100) NOT NULL UNIQUE,
    professor     VARCHAR(100) NOT NULL,
    carga_horaria INTEGER      NOT NULL CHECK (carga_horaria > 0)
);

-- Tabela associativa (N:N) com duas chaves estrangeiras
CREATE TABLE matriculas (
    id             SERIAL PRIMARY KEY,
    aluno_id       INTEGER NOT NULL REFERENCES alunos(id) ON DELETE CASCADE,
    curso_id       INTEGER NOT NULL REFERENCES cursos(id) ON DELETE RESTRICT,
    data_matricula DATE    NOT NULL DEFAULT CURRENT_DATE,
    nota           NUMERIC(4,2) CHECK (nota BETWEEN 0 AND 10),
    UNIQUE (aluno_id, curso_id)
);

-- =====================================================
-- Dados de teste
-- =====================================================

-- Usuário de teste: admin / admin123
INSERT INTO usuarios (nome, login, senha_hash)
VALUES ('Administrador', 'admin', crypt('admin123', gen_salt('bf')));

INSERT INTO alunos (nome, email, data_nascimento) VALUES
('Ana Souza',    'ana@email.com',    '2003-04-12'),
('Bruno Lima',   'bruno@email.com',  '2002-09-30'),
('Carla Mendes', 'carla@email.com',  '2004-01-22'),
('Diego Alves',  'diego@email.com',  '2001-11-05'),
('Elisa Rocha',  'elisa@email.com',  '2003-07-18');

INSERT INTO cursos (nome, professor, carga_horaria) VALUES
('Banco de Dados',          'Prof. Marcos',  60),
('Programação em Python',   'Profa. Helena', 80),
('Engenharia de Software',  'Prof. Ricardo', 100),
('Redes de Computadores',   'Profa. Teresa', 40);

INSERT INTO matriculas (aluno_id, curso_id, nota) VALUES
((SELECT id FROM alunos WHERE email = 'ana@email.com'),   (SELECT id FROM cursos WHERE nome = 'Banco de Dados'),         9.0),
((SELECT id FROM alunos WHERE email = 'ana@email.com'),   (SELECT id FROM cursos WHERE nome = 'Programação em Python'),  8.5),
((SELECT id FROM alunos WHERE email = 'bruno@email.com'), (SELECT id FROM cursos WHERE nome = 'Banco de Dados'),         6.0),
((SELECT id FROM alunos WHERE email = 'carla@email.com'), (SELECT id FROM cursos WHERE nome = 'Engenharia de Software'), 7.5),
((SELECT id FROM alunos WHERE email = 'carla@email.com'), (SELECT id FROM cursos WHERE nome = 'Banco de Dados'),         NULL);
-- Diego e Elisa ficam sem matrícula (para testar o filtro "alunos sem matrícula")
