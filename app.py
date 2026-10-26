"""Sistema Escola - CRUD no terminal com Python + PostgreSQL."""
import os
import sys
import getpass

import psycopg2
from psycopg2 import errors

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "dbname": os.getenv("DB_NAME", "escola"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "postgres"),
}

try:
    conn = psycopg2.connect(**DB_CONFIG)
except psycopg2.Error as e:
    sys.exit(f"Não foi possível conectar ao banco: {e}")


# ---------------------------------------------------------------- helpers
def executar(sql, params=()):
    """INSERT/UPDATE/DELETE. Retorna linhas afetadas ou None em caso de erro."""
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            n = cur.rowcount
        conn.commit()
        return n
    except errors.UniqueViolation:
        conn.rollback()
        print("Erro: já existe um registro com esse valor único (e-mail, nome ou matrícula).")
    except errors.ForeignKeyViolation:
        conn.rollback()
        print("Erro: operação bloqueada por chave estrangeira (id inexistente ou registros relacionados).")
    except psycopg2.Error as e:
        conn.rollback()
        print(f"Erro no banco: {(e.pgerror or str(e)).strip()}")
    return None


def mostrar(sql, params=()):
    """Executa um SELECT e imprime o resultado em formato de tabela."""
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            linhas = cur.fetchall()
            colunas = [d[0] for d in cur.description]
    except psycopg2.Error as e:
        conn.rollback()
        print(f"Erro no banco: {(e.pgerror or str(e)).strip()}")
        return
    if not linhas:
        print("Nenhum registro encontrado.")
        return
    linhas = [["-" if v is None else str(v) for v in l] for l in linhas]
    larg = [max(len(c), *(len(l[i]) for l in linhas)) for i, c in enumerate(colunas)]
    print(" | ".join(c.ljust(larg[i]) for i, c in enumerate(colunas)))
    print("-+-".join("-" * w for w in larg))
    for l in linhas:
        print(" | ".join(v.ljust(larg[i]) for i, v in enumerate(l)))


def resultado(n, msg):
    if n is None:
        return
    print(msg if n else "Registro não encontrado.")


def ler_int(msg):
    try:
        return int(input(msg))
    except ValueError:
        print("Valor inválido.")
        return None


def menu(titulo, opcoes):
    while True:
        print(f"\n=== {titulo} ===")
        for i, (texto, _) in enumerate(opcoes, 1):
            print(f"{i} - {texto}")
        print("0 - Voltar/Sair")
        op = input("Opção: ").strip()
        if op == "0":
            return
        if op.isdigit() and 1 <= int(op) <= len(opcoes):
            opcoes[int(op) - 1][1]()
        else:
            print("Opção inválida.")


# ------------------------------------------------------------------ login
def login():
    for _ in range(3):
        usuario = input("Login: ").strip()
        senha = getpass.getpass("Senha: ")
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, nome FROM usuarios "
                "WHERE login = %s AND senha_hash = crypt(%s, senha_hash)",
                (usuario, senha),
            )
            row = cur.fetchone()
        if row:
            print(f"\nBem-vindo(a), {row[1]}!")
            return True
        print("Login ou senha incorretos.")
    return False


# ----------------------------------------------------------------- alunos
def aluno_cadastrar():
    nome = input("Nome: ")
    email = input("E-mail: ")
    nasc = input("Nascimento (AAAA-MM-DD, opcional): ") or None
    n = executar(
        "INSERT INTO alunos (nome, email, data_nascimento) VALUES (%s, %s, %s)",
        (nome, email, nasc),
    )
    resultado(n, "Aluno cadastrado!")


def aluno_listar():
    mostrar("SELECT * FROM alunos ORDER BY nome")


def aluno_atualizar():
    aluno_listar()
    id_ = ler_int("ID do aluno: ")
    if id_ is None:
        return
    print("(deixe em branco para manter o valor atual)")
    nome, email = input("Novo nome: "), input("Novo e-mail: ")
    nasc = input("Nova data de nascimento (AAAA-MM-DD): ")
    n = executar(
        "UPDATE alunos SET nome = COALESCE(NULLIF(%s, ''), nome), "
        "email = COALESCE(NULLIF(%s, ''), email), "
        "data_nascimento = COALESCE(NULLIF(%s, '')::date, data_nascimento) "
        "WHERE id = %s",
        (nome, email, nasc, id_),
    )
    resultado(n, "Aluno atualizado!")


def aluno_excluir():
    aluno_listar()
    id_ = ler_int("ID do aluno a excluir: ")
    if id_ is not None:
        resultado(executar("DELETE FROM alunos WHERE id = %s", (id_,)),
                  "Aluno excluído (suas matrículas também).")


# ----------------------------------------------------------------- cursos
def curso_cadastrar():
    nome, prof = input("Nome do curso: "), input("Professor: ")
    carga = ler_int("Carga horária (horas): ")
    if carga is None:
        return
    n = executar(
        "INSERT INTO cursos (nome, professor, carga_horaria) VALUES (%s, %s, %s)",
        (nome, prof, carga),
    )
    resultado(n, "Curso cadastrado!")


def curso_listar():
    mostrar("SELECT * FROM cursos ORDER BY nome")


def curso_atualizar():
    curso_listar()
    id_ = ler_int("ID do curso: ")
    if id_ is None:
        return
    print("(deixe em branco para manter o valor atual)")
    nome, prof = input("Novo nome: "), input("Novo professor: ")
    carga = input("Nova carga horária: ")
    n = executar(
        "UPDATE cursos SET nome = COALESCE(NULLIF(%s, ''), nome), "
        "professor = COALESCE(NULLIF(%s, ''), professor), "
        "carga_horaria = COALESCE(NULLIF(%s, '')::int, carga_horaria) "
        "WHERE id = %s",
        (nome, prof, carga, id_),
    )
    resultado(n, "Curso atualizado!")


def curso_excluir():
    curso_listar()
    id_ = ler_int("ID do curso a excluir: ")
    if id_ is not None:
        resultado(executar("DELETE FROM cursos WHERE id = %s", (id_,)), "Curso excluído.")


# -------------------------------------------------------------- matrículas
def matricula_criar():
    aluno_listar()
    aluno = ler_int("ID do aluno: ")
    curso_listar()
    curso = ler_int("ID do curso: ")
    if aluno is None or curso is None:
        return
    n = executar("INSERT INTO matriculas (aluno_id, curso_id) VALUES (%s, %s)", (aluno, curso))
    resultado(n, "Matrícula realizada!")


def matricula_listar():
    mostrar(
        "SELECT m.id, a.nome AS aluno, c.nome AS curso, m.data_matricula, m.nota "
        "FROM matriculas m "
        "JOIN alunos a ON a.id = m.aluno_id "
        "JOIN cursos c ON c.id = m.curso_id "
        "ORDER BY a.nome, c.nome"
    )


def matricula_nota():
    matricula_listar()
    id_ = ler_int("ID da matrícula: ")
    if id_ is None:
        return
    try:
        nota = float(input("Nota (0 a 10): ").replace(",", "."))
    except ValueError:
        print("Nota inválida.")
        return
    resultado(executar("UPDATE matriculas SET nota = %s WHERE id = %s", (nota, id_)),
              "Nota lançada!")


def matricula_cancelar():
    matricula_listar()
    id_ = ler_int("ID da matrícula a cancelar: ")
    if id_ is not None:
        resultado(executar("DELETE FROM matriculas WHERE id = %s", (id_,)), "Matrícula cancelada.")


# ----------------------------------------------------------------- filtros
def filtro_aluno_nome():
    termo = input("Parte do nome: ")
    mostrar("SELECT * FROM alunos WHERE nome ILIKE %s ORDER BY nome", (f"%{termo}%",))


def filtro_alunos_curso():
    termo = input("Parte do nome do curso: ")
    mostrar(
        "SELECT a.id, a.nome, a.email, c.nome AS curso, m.nota "
        "FROM alunos a "
        "JOIN matriculas m ON m.aluno_id = a.id "
        "JOIN cursos c ON c.id = m.curso_id "
        "WHERE c.nome ILIKE %s ORDER BY c.nome, a.nome",
        (f"%{termo}%",),
    )


def filtro_curso_carga():
    minimo = ler_int("Carga horária mínima: ")
    if minimo is not None:
        mostrar("SELECT * FROM cursos WHERE carga_horaria >= %s ORDER BY carga_horaria DESC",
                (minimo,))


def filtro_sem_matricula():
    mostrar(
        "SELECT a.id, a.nome, a.email FROM alunos a "
        "LEFT JOIN matriculas m ON m.aluno_id = a.id "
        "WHERE m.id IS NULL ORDER BY a.nome"
    )


def filtro_media_curso():
    mostrar(
        "SELECT c.nome AS curso, COUNT(m.id) AS total_alunos, "
        "ROUND(AVG(m.nota), 2) AS media_notas "
        "FROM cursos c LEFT JOIN matriculas m ON m.curso_id = c.id "
        "GROUP BY c.id, c.nome ORDER BY total_alunos DESC"
    )


def filtro_aprovados():
    mostrar(
        "SELECT a.nome AS aluno, c.nome AS curso, m.nota "
        "FROM matriculas m "
        "JOIN alunos a ON a.id = m.aluno_id "
        "JOIN cursos c ON c.id = m.curso_id "
        "WHERE m.nota >= 7 ORDER BY m.nota DESC"
    )


# -------------------------------------------------------------------- main
def main():
    print("=== SISTEMA ESCOLA ===")
    if not login():
        sys.exit("Número máximo de tentativas excedido.")

    menu("MENU PRINCIPAL", [
        ("Alunos", lambda: menu("ALUNOS", [
            ("Cadastrar", aluno_cadastrar), ("Listar", aluno_listar),
            ("Atualizar", aluno_atualizar), ("Excluir", aluno_excluir)])),
        ("Cursos", lambda: menu("CURSOS", [
            ("Cadastrar", curso_cadastrar), ("Listar", curso_listar),
            ("Atualizar", curso_atualizar), ("Excluir", curso_excluir)])),
        ("Matrículas", lambda: menu("MATRÍCULAS", [
            ("Matricular aluno em curso", matricula_criar), ("Listar matrículas", matricula_listar),
            ("Lançar nota", matricula_nota), ("Cancelar matrícula", matricula_cancelar)])),
        ("Filtros e relatórios", lambda: menu("FILTROS", [
            ("Alunos por nome", filtro_aluno_nome),
            ("Alunos de um curso", filtro_alunos_curso),
            ("Cursos por carga horária mínima", filtro_curso_carga),
            ("Alunos sem matrícula", filtro_sem_matricula),
            ("Total de alunos e média por curso", filtro_media_curso),
            ("Alunos aprovados (nota >= 7)", filtro_aprovados)])),
    ])
    conn.close()
    print("Até logo!")


if __name__ == "__main__":
    main()
