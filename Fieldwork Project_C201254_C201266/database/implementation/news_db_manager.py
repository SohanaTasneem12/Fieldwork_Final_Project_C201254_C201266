import mysql.connector
from mysql.connector import Error
from db_connection import create_db_connection

def execute_query(connection, query, params=None):
    """
    Execute a given SQL query on the provided database connection with optional parameters.

    Parameters
    ----------
    connection : mysql.connector.connection.MySQLConnection
        The connection object to the database.
    query : str
        The SQL query to execute.
    params : tuple, optional
        Parameters to pass to the query (default is None).

    Returns
    -------
    None
    """
    cursor = connection.cursor()
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        connection.commit()
        print("Query executed successfully")
    except Error as e:
        print(f"The error '{e}' occurred")
    finally:
        cursor.close()

def execute_read_query(connection, query, params=None):
    """
    Execute a read query and return the results.

    Parameters
    ----------
    connection : mysql.connector.connection.MySQLConnection
        The connection object to the database.
    query : str
        The SQL query to execute.
    params : tuple, optional
        Parameters to pass to the query (default is None).

    Returns
    -------
    list
        A list of tuples containing the rows returned by the query.
    """
    cursor = connection.cursor()
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as e:
        print(f"The error '{e}' occurred")
        return []
    finally:
        cursor.close()

def create_tables(connection):
    """
    Create tables in the database based on the predefined schema.

    Parameters
    ----------
    connection : mysql.connector.connection.MySQLConnection
        The connection object to the database.

    Returns
    -------
    None
    """
    create_categories_table = """
    CREATE TABLE IF NOT EXISTS categories (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        description TEXT
    );
    """
    
    create_publishers_table = """
    CREATE TABLE IF NOT EXISTS publishers (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        email VARCHAR(255) UNIQUE NOT NULL
    );
    """
    
    create_reporters_table = """
    CREATE TABLE IF NOT EXISTS reporters (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        email VARCHAR(255) UNIQUE NOT NULL
    );
    """
    
    # Updated news table to store multiple reporters as a single string
 
    create_news_table = """
    CREATE TABLE IF NOT EXISTS news (
        id INT AUTO_INCREMENT PRIMARY KEY,
        category_id INT,
        publishers_id INT,
        reporters VARCHAR(255),  -- Storing reporters as a comma-separated string
        datetime DATETIME,       -- Ensure this is DATETIME type
        title VARCHAR(255) NOT NULL,
        body TEXT,
        link VARCHAR(255),
        FOREIGN KEY (category_id) REFERENCES categories (id),
        FOREIGN KEY (publishers_id) REFERENCES publishers (id)
    );
    """

    create_images_table = """
    CREATE TABLE IF NOT EXISTS images (
        id INT AUTO_INCREMENT PRIMARY KEY,
        news_id INT,
        image_url VARCHAR(255),
        FOREIGN KEY (news_id) REFERENCES news (id)
    );
    """
    
    create_summaries_table = """
    CREATE TABLE IF NOT EXISTS summaries (
        id INT AUTO_INCREMENT PRIMARY KEY,
        news_id INT,
        summary_text TEXT,
        FOREIGN KEY (news_id) REFERENCES news (id)
    );
    """
    
    # Execute the table creation queries
    execute_query(connection, create_categories_table)
    execute_query(connection, create_publishers_table)
    execute_query(connection, create_reporters_table)
    execute_query(connection, create_news_table)
    execute_query(connection, create_images_table)
    execute_query(connection, create_summaries_table)


# Example usage
if __name__ == "__main__":
    conn = create_db_connection()
    if conn is not None:
        create_tables(conn)
        # You can add further queries to test and check the created tables.
