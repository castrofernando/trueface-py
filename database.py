import sqlite3

class TrueFaceDb:
    def __init__(self) -> None:
        pass

    def createDatabase(self):
        conn = sqlite3.connect('face_settings.db')
        # definindo um cursor
        cursor = conn.cursor()

        # criando a tabela (schema)
        cursor.execute("""
        CREATE TABLE settings (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                vb_url_base     VARCHAR(100) NOT NULL,
                vb_port         INTEGER NOT NULL,
                vb_version      VARCHAR(10) NOT NULL,
                vb_username     VARCHAR(50) NOT NULL,
                vb_password     VARCHAR(50) NOT NULL
        );
        """)

        print('Tabela criada com sucesso.')
        # desconectando...
        conn.close()
    
if __name__ == "__main__":
    db=TrueFaceDb()
    db.createDatabase()