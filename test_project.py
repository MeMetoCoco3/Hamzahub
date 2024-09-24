import unittest, json, csv, os
from unittest.mock import patch, MagicMock, call, Mock
import project as wc


class TestWarehouseCreation(unittest.TestCase):
    @patch("project.mysql.connector.connect")
    def test_create_connection(self, mock_connect):
        with open(r".config\config_database.json", "r") as f:
            config_data = json.load(f)
        conexion = config_data["CONEXION"]
        warehouse_name = config_data["INFO"]["name"]

        mock_db = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_db
        mock_db.cursor.return_value = mock_cursor

        host, user, password, port = (
            conexion["host"],
            conexion["user"],
            conexion["password"],
            conexion["port"],
        )
        mydb, mycursor = wc.create_connection(
            host, user, password, port, warehouse_name
        )

        self.assertEqual(mydb, mock_db)
        self.assertEqual(mycursor, mock_cursor)
        mock_connect.assert_called_with(
            host=host, user=user, password=password, port=port, database=warehouse_name
        )
        mock_cursor.execute.assert_called_with(f"CREATE DATABASE {warehouse_name}")
        self.assertTrue(mock_db.commit.called)


        mock_db.reset_mock(), mock_cursor.reset_mock()

        host, user, password, port = (
            conexion["host"],
            conexion["user"],
            conexion["password"],
            conexion["port"],
        )
        mydb, mycursor = wc.create_connection(
            host, user, password, port, warehouse_name
        )

        mock_connect.assert_any_call(host=host, user=user, password=password, port=port)
        mock_cursor.execute.assert_called_with(f"CREATE DATABASE {warehouse_name}")
        self.assertTrue(mock_db.commit.called)

        mock_db.reset_mock(), mock_cursor.reset_mock(), mycursor.reset_mock()

    @patch("mysql.connector.connect")
    def test_mfwh_db(self, mock_connect):
        with open(r".config\config_database.json", "r") as f:
            config_data = json.load(f)
        conexion = config_data["CONEXION"]
        warehouse_name = config_data["INFO"]["name"]

        mock_db = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_db
        mock_db.cursor.return_value = mock_cursor

        host, user, password, port = (
            conexion["host"],
            conexion["user"],
            conexion["password"],
            conexion["port"],
        )
        mydb, mycursor = wc.create_connection(
            host, user, password, port, warehouse_name
        )

        self.assertEqual(mydb, mock_db)
        self.assertEqual(mycursor, mock_cursor)

        providers = config_data["CLIENTS"]
        products = config_data["PRODUCTS"]
        clients = ""
        for i in providers:
            clients += f"'{i[1]}', "
        levels = ""
        level_range = list(
            max(
                (
                    [
                        x["Levels"].keys()
                        for x in config_data["WAREHOUSE_DIMENSIONS"].values()
                    ]
                )
            )
        )
        for i in level_range:
            levels += f"'{i}',"

        wc.mfwh_db(mock_db, mock_cursor, providers, products, level_range)
        # Deal with call()
        expected_calls = [
            call(
                f"""CREATE TABLE Providers ( 
                company_code VARCHAR(10) PRIMARY KEY UNIQUE,
                name VARCHAR(30))"""
            ),
            call(
                f"""CREATE TABLE Contact_Providers(
                company_code VARCHAR(10),
                telefono VARCHAR(15), 
                email VARCHAR(75), 
                CONSTRAINT FK_contactP FOREIGN KEY(company_code) references Providers(company_code))"""
            ),
            call(
                """CREATE TABLE Customers (
                id INT AUTO_INCREMENT PRIMARY KEY, 
                country VARCHAR(30), 
                postal_code VARCHAR(12))"""
            ),
            call(
                """CREATE TABLE Contact_Customers (
                contact_id INT, 
                telefono VARCHAR(15), 
                email VARCHAR(75), 
                CONSTRAINT FK_contactC FOREIGN KEY(contact_id) references Customers(id))"""
            ),
            call(
                f"""CREATE TABLE Products (
                sku INT PRIMARY KEY, 
                name VARCHAR(40), 
                num_boxes_per_pallet INT, 
                company_code VARCHAR(10),
                benefit FLOAT, 
                ADR ENUM('Y','N'), 
                CONSTRAINT FK_prod_cc_prov FOREIGN KEY(company_code) references Providers(company_code))"""
            ),
            call(
                """CREATE TABLE Lps (
                lp VARCHAR(12) PRIMARY KEY, 
                sku INT,
                num_boxes INT DEFAULT 0,
                num_allocated_boxes INT DEFAULT 0,
                on_loc ENUM('Y','N'), 
                employee VARCHAR(20),
                CONSTRAINT FK_lps_sku_prod FOREIGN KEY(sku) references Products(sku))"""
            ),
            call(
                """CREATE TABLE Sales (
                id INT AUTO_INCREMENT PRIMARY KEY, 
                date DATE, 
                sku INT,
                num_boxes INT, 
                CONSTRAINT FK_sales_sku_prod FOREIGN KEY(sku) references Products(sku))"""
            ),
            call(
                """CREATE TABLE Locations ( 
                position VARCHAR(8) PRIMARY KEY, 
                level CHAR,
                lp VARCHAR(12),
                max_weight INT,
                max_height INT,
                ADR ENUM('Y','N'),
                CONSTRAINT FK_loc_lp_lps FOREIGN KEY(lp) references Lps(lp) 
                ON DELETE SET NULL)"""
            ),
            call(
                f"""CREATE TABLE Moves (
                id INT AUTO_INCREMENT PRIMARY KEY,
                lp VARCHAR(12), 
                future_position VARCHAR(8), 
                employee VARCHAR(20),
                company_code VARCHAR(10),
                CONSTRAINT FK_mv_lp_lps FOREIGN KEY(lp) references Lps(lp),
                CONSTRAINT FK_mv_cc_prov FOREIGN KEY(company_code) references Providers(company_code),
                CONSTRAINT FK_mv_fpos_loc FOREIGN KEY(future_position) references Locations(position))"""
            ),
            call(
                """CREATE TABLE Products_bufe (
                id INT AUTO_INCREMENT PRIMARY KEY,
                wave_number VARCHAR(16),
                order_number VARCHAR(12),
                sku INT,
                num_boxes INT,
                fecha DATE,
                CONSTRAINT FK_pb_sku_prod FOREIGN KEY(sku) references Products(sku))"""
            ),
            call(
                f"""CREATE TABLE Back_orders (
                id INT AUTO_INCREMENT PRIMARY KEY,
                sku INT,  
                num_boxes INT, 
                backorder_number VARCHAR(12), 
                fecha DATE,
                CONSTRAINT FK_bord_sku_prod FOREIGN KEY(sku) references Products(sku))"""
            ),
            call(
                f"""CREATE TABLE Pick_list (
                id INT AUTO_INCREMENT PRIMARY KEY, 
                company_code VARCHAR(10), 
                order_number VARCHAR(12), 
                sku INT, 
                num_boxes INT, 
                state ENUM('NR','NP', 'P') DEFAULT 'NR', 
                loc VARCHAR(8),
                employee VARCHAR(20),
                CONSTRAINT FK_pickl_cc_prov FOREIGN KEY(company_code) references Providers(company_code),
                CONSTRAINT FK_pickl_sku_prod FOREIGN KEY(sku) references Products(sku),
                CONSTRAINT FK_pickl_loc_locs FOREIGN KEY(loc) references Locations(position))"""
            ),
            call(
                f"""CREATE TABLE Trailers(
                id INT AUTO_INCREMENT PRIMARY KEY,
                trailer_number VARCHAR(16),
                sku INT,
                num_boxes INT,
                company_code VARCHAR(10),
                fecha DATE,
                CONSTRAINT FK_tr_sku_prod FOREIGN KEY(sku) references Products(sku))"""
            ),
            call(
                """CREATE VIEW Lp_location_data AS 
                SELECT Lps.lp AS lp, 
                    Lps.sku AS sku, 
                    Lps.num_boxes AS num_boxes, 
                    Lps.num_allocated_boxes AS num_allocated_boxes,
                    Locations.position AS position, 
                    Locations.level AS level
                FROM Lps RIGHT JOIN Locations 
                ON Lps.lp = Locations.lp;"""
            ),
            call(
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
            ),
            call(
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
            ),
            call(
                f"""CREATE TRIGGER tr_check_moves
            BEFORE UPDATE ON Lps
            FOR EACH ROW 
            BEGIN 
                DECLARE level_var ENUM({levels[:-1]});
                SELECT level INTO level_var 
                    FROM Locations 
                    WHERE Locations.Lp = NEW.lp;

                IF (level_var != '{level_range[0]}' AND NEW.num_allocated_boxes > 0) THEN
                    CALL pr_create_move(NEW.lp);
                END IF;
            END;"""
            ),
            call(
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
            ),
            call(
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
            ),
            call(
                f"""CREATE PROCEDURE pr_create_move(
            IN pallet_lp VARCHAR(12))
                BEGIN
                    DECLARE old_location_pos VARCHAR(8);
                    DECLARE new_location_pos VARCHAR(8);
                    DECLARE checker INT;


                    SELECT position INTO old_location_pos
                    FROM Locations
                    WHERE Locations.lp = pallet_lp LIMIT 1;

                    SELECT COUNT(id) INTO checker 
                    FROM Moves 
                    WHERE Moves.lp = pallet_lp;


                    IF (checker = 0) THEN
                        SELECT position INTO new_location_pos
                        FROM Locations
                        WHERE Locations.lp IS NULL AND Locations.level = '{level_range[0]}' AND position NOT IN (SELECT future_position FROM Moves) LIMIT 1;

                        INSERT INTO Moves (lp, future_position) 
                        VALUES (pallet_lp, new_location_pos);
                    END IF;

                END;"""
            ),
            call(
                f"""CREATE TRIGGER tr_count_allocate_boxes_per_location
                AFTER INSERT ON Products_bufe
                FOR EACH ROW
                BEGIN
                    DECLARE lp_pick VARCHAR(12);
                    DECLARE boxes_left INT;
                    DECLARE last_boxes_in_loc INT;
                    DECLARE boxes_for_new_location INT;
                    DECLARE number_boxes_warehouse INT;
                    DECLARE pick_location VARCHAR(8);
                    
                    SELECT lp INTO lp_pick 
                    FROM Lp_location_data
                    WHERE sku = NEW.sku AND level = '{level_range[0]}' AND num_boxes != 0 LIMIT 1;

                    IF (lp_pick IS NULL) THEN 
                        SELECT lp INTO lp_pick 
                        FROM Lp_location_data
                        WHERE sku = NEW.sku AND num_boxes != 0 LIMIT 1;
                    END IF;

                    SELECT (num_boxes - NEW.num_boxes) INTO boxes_left
                    FROM Lp_location_data
                    WHERE lp = lp_pick;

                    SELECT SUM(num_boxes) INTO number_boxes_warehouse 
                    FROM Lp_location_data 
                    WHERE sku = NEW.sku;

                    CASE 
                        WHEN number_boxes_warehouse < NEW.num_boxes THEN
                            INSERT INTO Back_orders(sku, num_boxes, backorder_number, fecha)
                            VALUES (NEW.sku, NEW.num_boxes, NEW.order_number, curdate());

                        WHEN boxes_left >= 0 THEN
                            UPDATE Lps 
                            SET Lps.num_boxes = boxes_left,
                                Lps.num_allocated_boxes = Lps.num_allocated_boxes + NEW.num_boxes
                            WHERE Lps.lp = lp_pick;

                            SELECT position INTO pick_location 
                            FROM Locations 
                            WHERE Locations.lp = lp_pick LIMIT 1;

                            INSERT INTO Pick_list(order_number, sku, num_boxes, loc)
                            VALUES(NEW.order_number, NEW.sku, NEW.num_boxes, pick_location);

                        WHEN boxes_left < 0 THEN      
                            SELECT num_boxes INTO last_boxes_in_loc
                            FROM Lp_location_data
                            WHERE lp = lp_pick LIMIT 1;
                            
                            SELECT (NEW.num_boxes - num_boxes) INTO boxes_for_new_location
                            FROM Lp_location_data
                            WHERE lp = lp_pick;
                    
                            UPDATE Lps 
                            SET Lps.num_boxes = 0,
                                Lps.num_allocated_boxes = Lps.num_allocated_boxes + last_boxes_in_loc
                            WHERE Lps.lp =  lp_pick;
                            
                            SELECT position INTO pick_location 
                            FROM Locations 
                            WHERE Locations.lp = lp_pick LIMIT 1;

                            INSERT INTO Pick_list(sku, order_number, num_boxes, loc) 
                            VALUES (NEW.sku, NEW.order_number, last_boxes_in_loc , pick_location);

                            SELECT lp INTO lp_pick FROM lp_location_data
                            WHERE sku = NEW.sku AND num_boxes > boxes_for_new_location 
                            ORDER BY Level, num_boxes DESC LIMIT 1;

                            UPDATE Lps
                            SET Lps.num_boxes = Lps.num_boxes - boxes_for_new_location,
                                Lps.num_allocated_boxes = Lps.num_allocated_boxes + boxes_for_new_location
                            WHERE Lps.lp = lp_pick;

                            SELECT position INTO pick_location 
                            FROM Locations 
                            WHERE Locations.lp = lp_pick Limit 1;

                            INSERT INTO Pick_list(sku, order_number, num_boxes, loc) 
                            VALUES (NEW.sku, NEW.order_number, boxes_for_new_location, pick_location);

                        ELSE BEGIN END;
                    END CASE;
                END;"""
            ),
            call(
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
            ),
            call(
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
            ),
            call(
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
            ),
            call(
                """CREATE PROCEDURE IF NOT EXISTS pr_check_allocated_boxes(
                    IN lp VARCHAR(12),
                    OUT return_value INT)
                        BEGIN    
                            DECLARE allocated_boxes INT;
                            SELECT num_allocated_boxes INTO allocated_boxes FROM Lps WHERE Lps.lp = lp;
                            SET return_value = allocated_boxes;
                            SELECT return_value;
                        END;"""
            ),
            call(
                """CREATE PROCEDURE IF NOT EXISTS pr_delete_empty_lp()
            BEGIN
                DELETE FROM Lps WHERE num_boxes = 0 AND num_allocated_boxes = 0;
            END; """
            ),
            call(
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
            ),
            call(
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
            ),
            call(
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
            ),
            call(
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
            ),
            call(
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
            ),
        ]

        mock_cursor.execute.assert_has_calls(expected_calls, any_order=True)
        mock_db.commit.assert_called()


    @patch('project.mysql.connector.connect')
    def test_mfwh_db_insert_providers_products(self, mock_connect):
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.executemany.return_value = mock_connection
    
        with open(r".config\config_database.json", "r") as f:
            config_data = json.load(f)

        aisles = [x for x in config_data['WAREHOUSE_DIMENSIONS'].keys()]
        adr = [x["ADR"] for x in config_data['WAREHOUSE_DIMENSIONS'].values()]
        aisles = list(zip(aisles, adr))
        rows = [x["Rows"] for x in config_data['WAREHOUSE_DIMENSIONS'].values()]
        levels = [x["Levels"] for x in config_data['WAREHOUSE_DIMENSIONS'].values()] 

        digital_warehouse = wc.mfwh_digital_warehouse(aisles, rows, levels)
    
        for index, x in enumerate(digital_warehouse): 
            self.assertEqual(x, aisles[index])
    
        self.assertEqual(len(digital_warehouse), len(aisles))
        
        test_rows = []
        for x in digital_warehouse.values():
            test_rows += [i for i in x]
    
        self.assertEqual(sum(rows), len(test_rows))

    @patch('project.mysql.connector.connect')
    @patch('project.numpy.random.choice')
    def test_fill_locations(self, mock_random_choice, mock_connect):
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor

        mock_cursor.fetchall.side_effect = [
            [('SKU1', 10), ('SKU2', 20)], 
            [(100,)] 
        ]

        # Mock the numpy.random.choice function to return a predictable sequence
        mock_random_choice.return_value = ['SKU1', 'SKU2', 'SKU1', None, 'SKU2']

        # Call the function under test
        wc.fill_locations(mock_connection)

        # Expected calls to execute and commit
        expected_execute_calls = [
            call("SELECT sku, num_boxes_per_pallet FROM Products"),
            call("SELECT COUNT(position) FROM Locations"),
            call(
                "INSERT INTO Lps(sku, num_boxes, on_loc) VALUES(%s, %s, %s)",
                ('SKU1', 10, 'Y')
            ),
            call(
                "INSERT INTO Lps(sku, num_boxes, on_loc) VALUES(%s, %s, %s)",
                ('SKU2', 20, 'Y')
            ),
            call(
                "INSERT INTO Lps(sku, num_boxes, on_loc) VALUES(%s, %s, %s)",
                ('SKU1', 10, 'Y')
            ),
            call(
                "INSERT INTO Lps(sku, num_boxes, on_loc) VALUES(%s, %s, %s)",
                ('SKU2', 20, 'Y')
            )
        ]

        mock_cursor.execute.assert_has_calls(expected_execute_calls, any_order=True)
        self.assertEqual(mock_connection.commit.call_count, 1)

    @patch('project.mysql.connector.connect')
    @patch('project.random.randint')
    def test_get_orders(self, mock_randint, mock_connect):
        mock_db = MagicMock()
        mock_cursor = MagicMock()

        mock_randint.side_effect = [
                1, 1, 1, 1,
                1, 1, 1,
                1, 1, 1,
                1, 1, 1,
                1, 1, 1,
        ]

        mock_connect.return_value = mock_db
        mock_db.cursor.return_value = mock_cursor
        

        mock_cursor.fetchall.side_effect = [
            [("sku1", 20), ("sku1", 40)],  # Products for KD
            [("sku1", 10), ("sku1", 12)],  # Products for JW
            [("sku1", 25), ("sku1", 30)],  # Products for RC
            [("sku1", 50), ("sku1", 50)],  # Products for SCP
        ]

        orders = wc.get_orders(mock_db, loop = True)
        expected_orders = {
            "JW": {
                1113: {"sku1": 1},
            },
            "KD": {
                1112: {"sku1": 1},
            },
            "RC": {
                1114: {"sku1": 1},
            },
            "SCP": {
                1115: {"sku1": 1},
            },
        }
        self.maxDiff = None
        self.assertEqual(orders, expected_orders)
    

    @patch('project.mysql.connector.connect')
    def test_fill_orders(self, mock_mydb):
        mock_cursor = MagicMock()
        mock_mydb.cursor.return_value = mock_cursor

        orders = {
            'KD': {1112: {'sku1': 5, 'sku2': 3}},
            'JW': {1113: {'sku1': 4, 'sku2': 2}},
            'RC': {1114: {'sku1': 2, 'sku2': 1}},
            'SCP': {1115: {'sku1': 3, 'sku2': 1}}
        }

        wc.fill_orders(mock_mydb, orders)
        expected_calls = [
            call("INSERT INTO Products_bufe (order_number, sku, num_boxes) VALUES(%s, %s, %s)", (1112, 'sku1', 5)),
            call("INSERT INTO Products_bufe (order_number, sku, num_boxes) VALUES(%s, %s, %s)", (1112, 'sku2', 3)),
            call("INSERT INTO Products_bufe (order_number, sku, num_boxes) VALUES(%s, %s, %s)", (1113, 'sku1', 4)),
            call("INSERT INTO Products_bufe (order_number, sku, num_boxes) VALUES(%s, %s, %s)", (1113, 'sku2', 2)),
            call("INSERT INTO Products_bufe (order_number, sku, num_boxes) VALUES(%s, %s, %s)", (1114, 'sku1', 2)),
            call("INSERT INTO Products_bufe (order_number, sku, num_boxes) VALUES(%s, %s, %s)", (1114, 'sku2', 1)),
            call("INSERT INTO Products_bufe (order_number, sku, num_boxes) VALUES(%s, %s, %s)", (1115, 'sku1', 3)),
            call("INSERT INTO Products_bufe (order_number, sku, num_boxes) VALUES(%s, %s, %s)", (1115, 'sku2', 1))
        ]

        self.assertEqual(mock_cursor.execute.call_args_list, expected_calls)
        self.assertEqual(mock_mydb.commit.call_count, 8)

    def test_trailer_in(self):
        data = [['TEST', 'TEST', 'TEST', 'NOT IN'], ['SCP', '41', '1'], ['SCP', '42', '1'], ['SCP', '43', '1'], ['SCP', '44', '1']]
        file_path = fr"trailer\TEST.csv"
        with open(file_path, "w", newline="") as f:
            writer = csv.writer(f, delimiter=",")
            writer.writerows(data)
        self.assertEqual(wc.trailer_in("TEST"), (data, "TEST"))

        data[0][-1] = "IN"
        file_path = fr"trailer\TEST.csv"
        with open(file_path, "w", newline="") as f:
            writer = csv.writer(f, delimiter=",")
            writer.writerows(data)
        self.assertEqual(wc.trailer_in("TEST"), f"Already in the system")
        os.remove(file_path)
        self.assertEqual(wc.trailer_in("This trailer dosnt exist"), f"Error, trailer 'This trailer dosnt exist' not found.")

if __name__ == "__main__":
    unittest.main()
