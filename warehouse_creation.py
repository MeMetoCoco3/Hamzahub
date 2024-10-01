import mysql.connector
import json
import pandas
import random
import numpy


# Warehouse Creation
def mfwh_db(mycursor, providers,  level_range):
    clients = ""
    for i in providers:
        clients += f"'{i[1]}', "
    levels = ""
    for i in level_range:
        levels += f"'{i}',"
    # Proveedores e info
    tables = [
        f"""CREATE TABLE Providers ( 
                company_code VARCHAR(10) PRIMARY KEY UNIQUE,
                name VARCHAR(30))""",
        f"""CREATE TABLE Contact_Providers(
                company_code VARCHAR(10),
                telefono VARCHAR(15), 
                email VARCHAR(75), 
                CONSTRAINT FK_contactP FOREIGN KEY(company_code) references Providers(company_code))""",
        """CREATE TABLE Customers (
                id INT AUTO_INCREMENT PRIMARY KEY, 
                country VARCHAR(30), 
                postal_code VARCHAR(12))""",
        """CREATE TABLE Contact_Customers (
                contact_id INT, 
                telefono VARCHAR(15), 
                email VARCHAR(75), 
                CONSTRAINT FK_contactC FOREIGN KEY(contact_id) references Customers(id))""",
        f"""CREATE TABLE Products (
                sku INT PRIMARY KEY, 
                name VARCHAR(40), 
                num_boxes_per_pallet INT, 
                company_code VARCHAR(10),
                benefit FLOAT, 
                ADR ENUM('Y','N'), 
                CONSTRAINT FK_prod_cc_prov FOREIGN KEY(company_code) references Providers(company_code))""",
        """CREATE TABLE Lps (
                lp VARCHAR(12) PRIMARY KEY, 
                sku INT,
                num_boxes INT DEFAULT 0,
                num_allocated_boxes INT DEFAULT 0,
                on_loc ENUM('Y','N'), 
                employee VARCHAR(20),
                CONSTRAINT FK_lps_sku_prod FOREIGN KEY(sku) references Products(sku))""",
        """CREATE TABLE Sales (
                id INT AUTO_INCREMENT PRIMARY KEY, 
                date DATE, 
                sku INT,
                num_boxes INT, 
                CONSTRAINT FK_sales_sku_prod FOREIGN KEY(sku) references Products(sku))""",
        """CREATE TABLE Locations ( 
                position VARCHAR(8) PRIMARY KEY, 
                level CHAR,
                lp VARCHAR(12),
                max_weight INT,
                max_height INT,
                ADR ENUM('Y','N'),
                CONSTRAINT FK_loc_lp_lps FOREIGN KEY(lp) references Lps(lp) 
                ON DELETE SET NULL)""",
        f"""CREATE TABLE Moves (
                id INT AUTO_INCREMENT PRIMARY KEY,
                lp VARCHAR(12) UNIQUE, 
                future_position VARCHAR(8), 
                employee VARCHAR(20),
                company_code VARCHAR(10),
                CONSTRAINT FK_mv_lp_lps FOREIGN KEY(lp) references Lps(lp),
                CONSTRAINT FK_mv_cc_prov FOREIGN KEY(company_code) references Providers(company_code),
                CONSTRAINT FK_mv_fpos_loc FOREIGN KEY(future_position) references Locations(position))""",
        """CREATE TABLE Products_bufe (
                id INT AUTO_INCREMENT PRIMARY KEY,
                wave_number VARCHAR(16),
                order_number VARCHAR(12),
                sku INT,
                num_boxes INT,
                fecha DATE,
                added VARCHAR(1),
                CONSTRAINT FK_pb_sku_prod FOREIGN KEY(sku) references Products(sku))""",
        f"""CREATE TABLE Back_orders (
                id INT AUTO_INCREMENT PRIMARY KEY,
                sku INT,  
                num_boxes INT, 
                backorder_number VARCHAR(12), 
                fecha DATE,
                CONSTRAINT FK_bord_sku_prod FOREIGN KEY(sku) references Products(sku))""",
        f"""CREATE TABLE Pick_list (
                id INT AUTO_INCREMENT PRIMARY KEY, 
                company_code VARCHAR(10), 
                order_number VARCHAR(12), 
                sku INT, 
                num_boxes INT, 
                state ENUM('NR','WM','NP', 'P') DEFAULT 'NR', 
                loc VARCHAR(8),
                lp VARCHAR(12),
                employee VARCHAR(20),
                CONSTRAINT FK_pickl_cc_prov FOREIGN KEY(company_code) references Providers(company_code),
                CONSTRAINT FK_pickl_sku_prod FOREIGN KEY(sku) references Products(sku),
                CONSTRAINT FK_pickl_loc_locs FOREIGN KEY(loc) references Locations(position))""",
        f"""CREATE TABLE Trailers(
                id INT AUTO_INCREMENT PRIMARY KEY,
                trailer_number VARCHAR(16),
                sku INT,
                num_boxes INT,
                company_code VARCHAR(10),
                fecha DATE,
                CONSTRAINT FK_tr_sku_prod FOREIGN KEY(sku) references Products(sku))""",
        """CREATE VIEW Lp_location_data AS 
                SELECT Lps.lp AS lp, 
                    Lps.sku AS sku, 
                    Lps.num_boxes AS num_boxes, 
                    Lps.num_allocated_boxes AS num_allocated_boxes,
                    Locations.position AS position, 
                    Locations.level AS level
                FROM Lps RIGHT JOIN Locations 
                ON Lps.lp = Locations.lp;""",
        """CREATE VIEW Sales_info AS 
                SELECT Sales.id AS Order_id, 
                    Sales.date AS Date, 
                    Sales.sku AS SKU, 
                    Sales.num_boxes AS Num_boxes,
                    ROUND(Products.benefit, 2) AS Single_unit_benefit,
                    ROUND(Sales.num_boxes * Products.benefit, 2) as Total_benefit,
                    Products.company_code 
                FROM Sales LEFT JOIN Products 
                ON Sales.sku = Products.sku;""",
    ]

    for table in tables:
        mycursor.execute(table)

    # Triggers
    mycursor.execute(
        """CREATE TRIGGER tr_write_lp_on_loc
                AFTER INSERT ON Lps 
                FOR EACH ROW 
                BEGIN 
                    DECLARE check_on_location INT;
                    DECLARE random_position VARCHAR(8);
                    
                    SELECT COUNT(position) INTO check_on_location
                    FROM Locations WHERE Locations.lp = NEW.lp LIMIT 1;

                    IF (NEW.on_loc = 'Y' AND check_on_location != 1) THEN
                        SELECT Locations.position INTO random_position FROM Locations
                        WHERE Locations.lp IS NULL
                        ORDER BY RAND()
                        LIMIT 1; 

                        UPDATE Locations SET Locations.lp = NEW.lp
                        WHERE Locations.position = random_position;
                    END IF;
                END;"""
    )

    mycursor.execute(
        """CREATE TRIGGER tr_write_lp
                BEFORE INSERT ON Lps 
                FOR EACH ROW 
                BEGIN 
                    DECLARE last_id INT;
                    SELECT COUNT(lp) INTO last_id FROM Lps;
                    IF (NEW.lp IS NULL) THEN 
                        SET NEW.lp = CONCAT(last_id, '-', NEW.sku);
                    END IF;
                END;"""
    )

    mycursor.execute(
        """CREATE TRIGGER tr_assign_cc 
            BEFORE INSERT ON Pick_list
            FOR EACH ROW
            BEGIN
                DECLARE new_company_code VARCHAR(10);
                SELECT company_code INTO new_company_code
                FROM Products 
                WHERE SKU = NEW.sku;
                SET NEW.company_code = new_company_code;
            END;"""
    )

    mycursor.execute(
        """CREATE TRIGGER tr_assign_cc_moves
            BEFORE INSERT ON Moves
            FOR EACH ROW
            BEGIN
                DECLARE new_company_code VARCHAR(10);
                SELECT company_code INTO new_company_code
                FROM Products RIGHT JOIN Lps
                ON Products.Sku = Lps.sku
                WHERE Lps.lp = NEW.lp;
                SET NEW.company_code = new_company_code;
            END;"""
    )

    mycursor.execute(
        """CREATE PROCEDURE IF NOT EXISTS pr_complete_move(
                IN new_position VARCHAR(8),
                IN lp_to_move VARCHAR(12))
                BEGIN    
                    CALL pr_check_lp_exists(lp_to_move);
                    CALL pr_check_empty(new_position);
                    CALL pr_check_allocated_boxes(lp_to_move, @allocated_boxes);
                    IF (@allocated_boxes > 0) THEN
                        SIGNAL SQLSTATE '47000' SET MESSAGE_TEXT = 'NOT POSSIBLE MOVE ALLOCATED PRODUCTS';
                    END IF;

                    UPDATE Locations SET Locations.lp = NULL WHERE Locations.lp = lp_to_move;
                    UPDATE Locations SET Locations.lp = lp_to_move WHERE Locations.position = new_position;
                    UPDATE Lps SET Lps.on_loc = 'Y' WHERE Lps.lp = lp_to_move;
                END;"""
    )

    mycursor.execute(
        f"""CREATE PROCEDURE IF NOT EXISTS pr_picking_move(
                IN new_position VARCHAR(8),
                IN lp_to_move VARCHAR(12))
                BEGIN    
                    DECLARE level_var CHAR;
                    DECLARE old_loc VARCHAR(8);
                    SELECT level INTO level_var FROM Locations WHERE position = new_position;  
                    SELECT position INTO old_loc FROM Locations WHERE lp = lp_to_move;
                    CALL pr_check_empty(new_position);
                    
                    IF (level_var != '{level_range[0]}') THEN    
                        SIGNAL SQLSTATE '47000' SET MESSAGE_TEXT = 'NOT "A" LEVEL LOCATION';
                    END IF;

                    UPDATE Locations SET Locations.lp = NULL WHERE Locations.lp = lp_to_move;
                    UPDATE Locations SET Locations.lp = lp_to_move WHERE Locations.position = new_position;
                    DELETE FROM Moves WHERE lp = lp_to_move;
                END;"""
    )

    mycursor.execute(
        """CREATE PROCEDURE IF NOT EXISTS pr_partial_move(
                IN old_lp VARCHAR(12),
                IN new_lp VARCHAR(12),
                IN num_boxes_to_move INT)
                BEGIN    
                    DECLARE not_alloc_boxes INT;
                    DECLARE pm_sku INT;
                    DECLARE boxes_lp INT;
                    SELECT num_boxes INTO not_alloc_boxes FROM Lps WHERE Lps.lp = old_lp;
                    SELECT sku INTO pm_sku FROM Lps WHERE Lps.lp = old_lp;

                    CALL pr_check_lp_exists(old_lp);
                    IF (num_boxes_to_move > not_alloc_boxes) THEN
                        SIGNAL SQLSTATE '49000' SET MESSAGE_TEXT = 'NOT ENOUGH MOVABLE BOXES';
                    END IF;

                    INSERT INTO Lps (lp, sku, num_boxes) 
                    VALUES (new_lp, pm_sku, num_boxes_to_move);
                    UPDATE Lps SET Lps.num_boxes = Lps.num_boxes - num_boxes_to_move WHERE Lps.lp = old_lp;

                    CALL pr_delete_empty_lp();
                END;"""
    )

    mycursor.execute(
        """CREATE PROCEDURE IF NOT EXISTS pr_check_in(
                IN trailer_number VARCHAR(16),
                IN var_sku INT,
                IN new_lp VARCHAR(12),
                IN num_boxes_to_move INT)
                BEGIN    
                    DECLARE total_boxes INT;

                    SELECT num_boxes INTO total_boxes FROM Trailers 
                        WHERE Trailers.trailer_number = trailer_number AND Trailers.sku = var_sku;

                    CALL pr_check_lp_not_exists(new_lp);
                    
                    IF (total_boxes IS NULL) THEN
                        SIGNAL SQLSTATE '85000' SET MESSAGE_TEXT = 'TRAILER NOT FOUND';
                    END IF;

                    IF (num_boxes_to_move > total_boxes) THEN
                        SIGNAL SQLSTATE '85000' SET MESSAGE_TEXT = 'NOT ENOUGH BOXES';
                    END IF;

                    UPDATE Trailers SET Trailers.num_boxes = total_boxes - num_boxes_to_move 
                        WHERE Trailers.trailer_number = trailer_number AND Trailers.sku = var_sku;
                        
                    IF (num_boxes_to_move = total_boxes) THEN
                        DELETE FROM Trailers WHERE Trailers.num_boxes = 0;
                    END IF;


                    INSERT INTO Lps (lp, sku, num_boxes) 
                    VALUES (new_lp, var_sku, num_boxes_to_move);


                END;"""
    )

    mycursor.execute(
        """CREATE PROCEDURE IF NOT EXISTS pr_check_allocated_boxes(
                    IN lp VARCHAR(12),
                    OUT return_value INT)
                        BEGIN    
                            DECLARE allocated_boxes INT;
                            SELECT num_allocated_boxes INTO allocated_boxes FROM Lps WHERE Lps.lp = lp;
                            SET return_value = allocated_boxes;
                            SELECT return_value;
                        END;"""
    )

    mycursor.execute(
        """CREATE PROCEDURE IF NOT EXISTS pr_delete_empty_lp()
            BEGIN
                DELETE FROM Lps WHERE num_boxes = 0 AND num_allocated_boxes = 0;
            END; """
    )

    mycursor.execute(
        """CREATE PROCEDURE IF NOT EXISTS pr_delete_trailer(
                    IN trailer VARCHAR(16)
                    )
                        BEGIN    
                            DELETE FROM Trailers WHERE Trailers.trailer_number = trailer;
                        END;"""
    )

    mycursor.execute(
        """CREATE PROCEDURE IF NOT EXISTS pr_delete_order(
                    IN order_number VARCHAR(12)
                    )
                        BEGIN    
                            DELETE FROM Products_bufe WHERE Products_bufe.order_number= order_number;
                            DELETE FROM Pick_list WHERE Pick_list.order_number= order_number;
                        END;"""
    )

    mycursor.execute(
        """CREATE PROCEDURE IF NOT EXISTS pr_check_empty(
                IN check_position VARCHAR(8))
                    BEGIN   
                        DECLARE check_empty VARCHAR(12);
                        SELECT lp INTO check_empty 
                        FROM lp_location_data
                        WHERE position = check_position;
                                
                        IF (check_empty IS NOT NULL) THEN
                            SIGNAL SQLSTATE '46000' SET MESSAGE_TEXT = 'LOCATION NOT EMPTY';
                        END IF;
                    END;"""
    )

    mycursor.execute(
        """CREATE PROCEDURE IF NOT EXISTS pr_check_order_employee(
                IN check_order VARCHAR(8),
                IN employee VARCHAR(20))
                    BEGIN   
                        DECLARE check_empty VARCHAR(20);
                        SELECT Pick_list.employee INTO check_empty 
                        FROM Pick_list
                        WHERE Pick_list.order_number = check_order LIMIT 1;
                        
                        IF check_empty IS NULL THEN
                            SET @result_o = 'ISEMPTY';
                        ELSE 
                            SET @result_o = check_empty;
                        END IF;

                    END;"""
    )

    mycursor.execute(
        """CREATE PROCEDURE IF NOT EXISTS pr_check_move_employee(
                IN lp VARCHAR(12),
                IN employee VARCHAR(20))
                    BEGIN   
                        DECLARE check_empty VARCHAR(20);
                        SELECT Moves.employee INTO check_empty 
                        FROM Moves
                        WHERE Moves.lp = lp LIMIT 1;

                        IF check_empty IS NULL THEN
                            SET @result_m = 'ISEMPTY';
                        ELSEIF check_empty = employee THEN
                            SET @result_m = 'ISEMPTY';
                        ELSE 
                            SET @result_m = check_empty;
                        END IF;

                    END;"""
    )

    mycursor.execute(
        """CREATE PROCEDURE IF NOT EXISTS pr_check_released(
                IN order_number VARCHAR(12))
                    BEGIN   
                        DECLARE check_var ENUM('NR','NP','P');
                        DECLARE _message_var VARCHAR(128);
                        SELECT state INTO check_var 
                        FROM Pick_list
                        WHERE Pick_list.order_number = order_number LIMIT 1;
                                
                        IF (check_var <> 'NP') THEN
                            SELECT CONCAT('ERROR,  STATE: ', check_var) INTO _message_var;
                            SIGNAL SQLSTATE '40000' SET MESSAGE_TEXT = _message_var;
                        END IF;
                    END;"""
    )
    mycursor.execute(
        """CREATE PROCEDURE IF NOT EXISTS pr_check_lp_exists(
                IN check_lp VARCHAR(12))
                    BEGIN   
                        DECLARE check_empty VARCHAR(12);
                        SELECT lp INTO check_empty 
                        FROM Lps
                        WHERE lp = check_lp;
                                
                        IF (check_empty IS NULL) THEN
                            SIGNAL SQLSTATE '50000' SET MESSAGE_TEXT = 'LP DOES NOT EXIST';
                        END IF;
                    END;"""
    )

    mycursor.execute(
        """CREATE PROCEDURE IF NOT EXISTS pr_check_lp_not_exists(
                IN check_lp VARCHAR(12))
                    BEGIN   
                        DECLARE check_empty VARCHAR(12);
                        SELECT lp INTO check_empty 
                        FROM Lps
                        WHERE lp = check_lp;
                                
                        IF (check_empty IS NOT NULL) THEN
                            SIGNAL SQLSTATE '50000' SET MESSAGE_TEXT = 'LP DOES EXIST';
                        END IF;
                    END;"""
    )

    mycursor.execute(
        """CREATE PROCEDURE IF NOT EXISTS pr_picking(
                IN order_number VARCHAR(12),
                IN pick_location VARCHAR(8),
                IN num_boxes INT)
                    BEGIN
                        DECLARE lp_from_location VARCHAR(12);
                        DECLARE order_num_state VARCHAR(2);
                        SELECT state INTO order_num_state FROM Pick_list WHERE Pick_list.order_number = order_number LIMIT 1;

                        SELECT lp INTO lp_from_location FROM lp_location_data WHERE position = pick_location;
                        UPDATE Pick_list SET Pick_list.state = 'P' WHERE Pick_list.order_number = order_number AND Pick_list.loc = pick_location;
                        UPDATE Lps SET Lps.num_allocated_boxes = Lps.num_allocated_boxes - num_boxes  WHERE Lps.lp = lp_from_location;

                        CALL pr_delete_empty_lp();
                    END;"""
    )

    mycursor.execute(
        f"""CREATE PROCEDURE IF NOT EXISTS pr_release_orders(
            IN client ENUM({clients[:-2]}, 'WA')
        )
                    BEGIN
                        DECLARE checker INT;
                        DECLARE _error_message VARCHAR(128);
                        DECLARE orders_left INT;

                        IF client = 'WA' THEN
                            SELECT COUNT(id) INTO checker FROM Moves;
                        ELSE
                            SELECT COUNT(id) INTO checker FROM Moves WHERE Moves.company_code = client;
                        END IF;

                        SELECT id INTO orders_left FROM Pick_list 
                            WHERE Pick_list.company_code = client AND 
                            Pick_list.state = 'NR' LIMIT 1;
                        
                        IF orders_left IS NULL THEN 
                            SELECT CONCAT('The client ', client, ' does not have orders left to release' ) INTO _error_message;
                            SIGNAL SQLSTATE '41000'
                            SET MESSAGE_TEXT = _error_message; 
                        END IF;
                        
                        CASE
                            WHEN (checker != 0) THEN
                                SELECT CONCAT('STILL HAVE ', checker, ' MOVES TO DO FOR ', client) INTO _error_message;
                                SIGNAL SQLSTATE '41000' SET MESSAGE_TEXT = _error_message;
                            WHEN (checker = 0) THEN
                                IF client = 'WA' THEN
                                    UPDATE Pick_list SET state = 'NP';
                                ELSE
                                    UPDATE Pick_list SET state = 'NP'
                                    WHERE Pick_list.company_code = client;
                                END IF;
                            END CASE;
                    END;"""
    )

    mycursor.execute(
        f"""CREATE PROCEDURE IF NOT EXISTS pr_check_enough_boxes(
            IN new_sku INT,
            IN new_order INT )
          
                    BEGIN
                        DECLARE total_boxes_in_wh INT;
                        DECLARE total_boxes_to_pick INT;

                        SELECT SUM(num_boxes) INTO total_boxes_in_wh
                            FROM lp_location_data WHERE lp_location_data.sku = new_sku;
                        
                        IF new_order = 0 THEN
                            SELECT SUM(num_boxes) INTO total_boxes_to_pick
                                FROM back_orders WHERE back_orders.sku = new_sku;
                        ELSE
                            SELECT SUM(num_boxes) INTO total_boxes_to_pick
                                FROM back_orders WHERE back_orders.sku = new_sku 
                                    AND back_orders.backorder_number = new_order;
                        END IF;

                        IF total_boxes_in_wh < total_boxes_to_pick THEN
                            SET @can_be_picked = 'N';
                        ELSE 
                            SET @can_be_picked = 'Y';
                        END IF;
                    END;
    """
    )


def mfwh_db_insert_providers_products(mydb, mycursor, providers, products):
    sql = "INSERT INTO Providers (name, company_code) VALUES (%s, %s)"
    mycursor.executemany(sql, providers)
    mydb.commit()

    sql = "INSERT INTO Products (sku, name, num_boxes_per_pallet, company_code, benefit, ADR) VALUES (%s, %s, %s, %s, %s, %s)"
    mycursor.executemany(sql, products)
    mydb.commit()


def drop_db(mycursor, mydb, name):
    mycursor.execute(f"DROP DATABASE IF EXISTS {name}")
    mydb.commit()


def create_connection(host, user, password, port, name):
    try:
        mydb = mysql.connector.connect(
            host=host, user=user, password=password, port=port, database=name
        )
        mycursor = mydb.cursor()
        drop_db(mycursor, mydb, name)
    except:
        mydb = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            port=port,
        )
        mycursor = mydb.cursor()
    finally:
        mydb = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            port=port,
        )
        mycursor = mydb.cursor()
        mycursor.execute(f"""CREATE DATABASE {name}""")
        mydb.commit()
        del mydb, mycursor

        mydb = mysql.connector.connect(
            host=host, user=user, password=password, port=port, database=name
        )
        mycursor = mydb.cursor()
        return mydb, mycursor
    


if __name__ == '__main__':
    print("done!")
    with open(".config\config_database.json", "r") as f:
        config_data = json.load(f)
    
    conexion = config_data['CONEXION']

    host = conexion['host']
    user = conexion['user']
    password = conexion['password']
    port = conexion['port']
    name = conexion['database']

    providers = config_data['CLIENTS']
    products = config_data['PRODUCTS']
    level_range = list(
        max(
            ([x["Levels"].keys() for x in config_data["WAREHOUSE_DIMENSIONS"].values()])
        )
    )

    db, cursor = create_connection(host, user, password, port, name)
    mfwh_db(cursor, providers, level_range)
    mfwh_db_insert_providers_products(db, cursor, providers, products)
