# Sistema Escola

Sistema CRUD executado no terminal para gerenciar **alunos, cursos e matrículas** de uma escola, com login de usuário e consultas SQL com filtros.

## Descrição

- Login com senha armazenada em hash (`pgcrypto`/bcrypt).
- CRUD completo de **alunos**, **cursos** e **matrículas**.
- Relacionamento N:N entre alunos e cursos, através da tabela `matriculas` (duas chaves estrangeiras).
- Filtros e relatórios feitos com SQL (`ILIKE`, `JOIN`, `LEFT JOIN`, `GROUP BY`, `AVG`).

### Modelo de dados

```
alunos (id PK, nome, email UNIQUE, data_nascimento)
cursos (id PK, nome UNIQUE, professor, carga_horaria)
matriculas (id PK, aluno_id FK -> alunos, curso_id FK -> cursos, data_matricula, nota)
usuarios (id PK, nome, login UNIQUE, senha_hash)
```

- Excluir um **aluno** remove suas matrículas (`ON DELETE CASCADE`).
- Excluir um **curso** com alunos matriculados é bloqueado (`ON DELETE RESTRICT`).

## Tecnologias

- Python 3.9+
- PostgreSQL 13+
- Biblioteca `psycopg2-binary`

## Configuração do banco de dados

1. Crie o banco:
   ```bash
   psql -U postgres -c "CREATE DATABASE escola;"
   ```
2. Crie as tabelas e os dados de teste:
   ```bash
   psql -U postgres -d escola -f schema.sql
   ```

## Execução

```bash
pip install -r requirements.txt
python app.py
```

A conexão usa, por padrão, `localhost:5432`, banco `escola`, usuário `postgres` e senha `postgres`.
Para alterar, defina variáveis de ambiente antes de executar:

```bash
# Linux / macOS
export DB_USER=meuusuario DB_PASSWORD=minhasenha
# Windows (PowerShell)
$env:DB_USER="meuusuario"; $env:DB_PASSWORD="minhasenha"
```

Variáveis disponíveis: `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`.

## Usuário para teste

| Login | Senha    |
|-------|----------|
| admin | admin123 |

## Arquivos

- `app.py` — aplicação de terminal
- `schema.sql` — criação das tabelas e dados de teste
- `queries.sql` — todos os comandos SQL utilizados (CRUD e filtros)
- `requirements.txt` — dependências Python

## Filtros disponíveis

1. Alunos por nome (busca parcial)
2. Alunos de um curso
3. Cursos por carga horária mínima
4. Alunos sem matrícula
5. Total de alunos e média de notas por curso
6. Alunos aprovados (nota >= 7)
