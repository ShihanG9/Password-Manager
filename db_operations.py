from encryption_util import decrypt_password, encrypt_password, set_master_password

import sqlite3


class DbOperations:

    def create_master_check(self):
        conn = self.connect_to_db()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS master_check (
                id INTEGER PRIMARY KEY,
                secret TEXT
            );
        ''')
        cursor.execute('SELECT COUNT(*) FROM master_check')
        if cursor.fetchone()[0] == 0:
            from encryption_util import encrypt_password
            encrypted = encrypt_password("VALID_KEY")
            cursor.execute('INSERT INTO master_check (secret) VALUES (?)', (encrypted,))
        conn.commit()


    def validate_master_password(self):
        conn = self.connect_to_db()
        cursor = conn.cursor()
        cursor.execute('SELECT secret FROM master_check LIMIT 1;')
        row = cursor.fetchone()

        if row is None:
            return False  # Can't validate if check isn't there

        from encryption_util import decrypt_password
        try:
            decrypted = decrypt_password(row[0])
            return decrypted == "VALID_KEY"
        except:
            return False




    def connect_to_db(self):
        conn = sqlite3.connect('password_records.db')
        return conn
    
    def create_table(self, table_name="password_info"):
        conn = self.connect_to_db()
        query = f'''
        CREATE TABLE IF NOT EXISTS {table_name}(
            ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            update_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            website TEXT NOT NULL,
            username VARCHAR(200),
            password VARCHAR(50) 
        );
        '''

        with conn as conn:
            cursor = conn.cursor()
            cursor.execute(query)



    def change_master_password(self, new_password, table_name="password_info"):
        conn = self.connect_to_db()
        cursor = conn.cursor()
        cursor.execute(f"SELECT ID, password FROM {table_name};")
        records = cursor.fetchall()
        
        from encryption_util import decrypt_password, encrypt_password, set_master_password
        
        for record in records:
            ID, encrypted_pwd = record
            try:
                # Decrypt using old master password
                plain_pwd = decrypt_password(encrypted_pwd)
                # Encrypt using new master password
                set_master_password(new_password)
                new_encrypted = encrypt_password(plain_pwd)
                # Update record
                cursor.execute(f"UPDATE {table_name} SET password = ? WHERE ID = ?", (new_encrypted, ID))
            except:
                print(f"Error updating record {ID}, skipping...")

        # Now update master_check table too
        try:
            encrypted_check = encrypt_password("VALID_KEY")
            cursor.execute("UPDATE master_check SET secret = ? WHERE id = 1;", (encrypted_check,))
        except:
            print("Failed to update master_check validation token.")

        conn.commit()



    
    def create_record(self, data, table_name="password_info"):
        website = data['website']
        username = data['username']
        password = encrypt_password(data['password'])  # 🔐 Encrypt before storing
        conn = self.connect_to_db()
        query = f'''
        INSERT INTO {table_name}('website', 'username', 'password') VALUES ( ?, ?, ?);
        '''

        with conn as conn:
            cursor = conn.cursor()
            cursor.execute(query, (website, username, password))

    def show_records(self, table_name="password_info"):
        conn = self.connect_to_db()
        query = f'''
        SELECT * FROM {table_name};
        '''
        with conn as conn:
            cursor = conn.cursor()
            list_records = cursor.execute(query)
            return list_records

    def update_record(self, data, table_name="password_info"):
        ID = data['ID']
        website = data['website']
        username = data['username']
        password = encrypt_password(data['password'])
        conn = self.connect_to_db()
        query = f'''
        UPDATE {table_name} SET  website = ?, username = ?, password = ? WHERE ID  = ?;
        '''
        with conn as conn:
            cursor = conn.cursor()
            cursor.execute(query, (website, username, password, ID))

    def delete_record(self, ID, table_name="password_info"):
        conn = self.connect_to_db()
        query = f'''
        DELETE FROM {table_name} WHERE ID  = ?;
        '''
        with conn as conn:
            cursor = conn.cursor()
            cursor.execute(query, (ID,))
