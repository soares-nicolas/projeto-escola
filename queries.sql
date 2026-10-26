-- =====================================================
-- Sistema Escola - Comandos SQL utilizados no projeto
-- (os valores de exemplo correspondem aos parâmetros %s do app.py)
-- =====================================================

-- ---------- LOGIN ----------
SELECT id, nome FROM usuarios
WHERE login = 'admin' AND senha_hash = crypt('admin123', senha_hash);

-- ---------- CRUD: ALUNOS ----------
INSERT INTO alunos (nome, email, data_nascimento)
VALUES ('Fernanda Costa', 'fernanda@email.com', '2004-03-10');

SELECT * FROM alunos ORDER BY nome;

UPDATE alunos
SET nome  = COALESCE(NULLIF('Fernanda C. Silva', ''), nome),
    email = COALESCE(NULLIF('', ''), email)
WHERE id = 6;

DELETE FROM alunos WHERE id = 6;

-- ---------- CRUD: CURSOS ----------
INSERT INTO cursos (nome, professor, carga_horaria)
VALUES ('Estruturas de Dados', 'Prof. Paulo', 60);

SELECT * FROM cursos ORDER BY nome;

UPDATE cursos SET carga_horaria = 70 WHERE id = 5;

DELETE FROM cursos WHERE id = 5;

-- ---------- CRUD: MATRÍCULAS ----------
INSERT INTO matriculas (aluno_id, curso_id) VALUES (4, 1);

SELECT m.id, a.nome AS aluno, c.nome AS curso, m.data_matricula, m.nota
FROM matriculas m
JOIN alunos a ON a.id = m.aluno_id
JOIN cursos c ON c.id = m.curso_id
ORDER BY a.nome, c.nome;

UPDATE matriculas SET nota = 8.0 WHERE id = 3;

DELETE FROM matriculas WHERE id = 3;

-- ---------- FILTROS ----------
-- 1) Alunos por nome (busca parcial, sem diferenciar maiúsculas)
SELECT * FROM alunos WHERE nome ILIKE '%an%' ORDER BY nome;

-- 2) Alunos matriculados em um curso
SELECT a.id, a.nome, a.email, m.nota
FROM alunos a
JOIN matriculas m ON m.aluno_id = a.id
JOIN cursos c     ON c.id = m.curso_id
WHERE c.nome ILIKE '%banco%'
ORDER BY a.nome;

-- 3) Cursos com carga horária mínima
SELECT * FROM cursos WHERE carga_horaria >= 60 ORDER BY carga_horaria DESC;

-- 4) Alunos sem nenhuma matrícula (LEFT JOIN)
SELECT a.id, a.nome, a.email
FROM alunos a
LEFT JOIN matriculas m ON m.aluno_id = a.id
WHERE m.id IS NULL;

-- 5) Quantidade de alunos e média de notas por curso (GROUP BY)
SELECT c.nome AS curso,
       COUNT(m.id)              AS total_alunos,
       ROUND(AVG(m.nota), 2)    AS media_notas
FROM cursos c
LEFT JOIN matriculas m ON m.curso_id = c.id
GROUP BY c.id, c.nome
ORDER BY total_alunos DESC;

-- 6) Alunos aprovados (nota >= 7)
SELECT a.nome AS aluno, c.nome AS curso, m.nota
FROM matriculas m
JOIN alunos a ON a.id = m.aluno_id
JOIN cursos c ON c.id = m.curso_id
WHERE m.nota >= 7
ORDER BY m.nota DESC;
