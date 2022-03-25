DROP DATABASE rbacpoc;
CREATE DATABASE rbacpoc;
USE rbacpoc;

--

CREATE TABLE IF NOT EXISTS operation (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL
);
CREATE TABLE IF NOT EXISTS `group` (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);
--
CREATE TABLE IF NOT EXISTS permission (
    id INT AUTO_INCREMENT PRIMARY KEY,
    `resource` VARCHAR(255) NOT NULL,
    operation_id INT NOT NULL,
    FOREIGN KEY (operation_id) REFERENCES operation(id)
);

CREATE TABLE IF NOT EXISTS user_group (
    `group_id` INT NOT NULL,
    `user_id` INT NOT NULL,
    FOREIGN KEY (group_id) REFERENCES `group`(id),
    FOREIGN KEY (user_id) REFERENCES `user`(id)
);
CREATE TABLE IF NOT EXISTS group_permission (
    group_id INT NOT NULL,
    permission_id INT NOT NULL,
    FOREIGN KEY (group_id) REFERENCES `group`(id) ON DELETE RESTRICT,
    FOREIGN KEY (permission_id) REFERENCES permission(id) ON DELETE RESTRICT
);
 
CREATE TABLE IF NOT EXISTS secrets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    secret VARCHAR(255) NOT NULL
);

-- Group to permisisons mapping
CREATE OR REPLACE VIEW group_permission_vw AS
SELECT 
    `group`.id as group_id,
    `group`.`name` as group_name,
    permission.resource,
    operation.name
FROM `group_permission`
LEFT JOIN `group` ON group_permission.group_id = `group`.id
LEFT JOIN permission ON group_permission.permission_id = permission.id
LEFT JOIN operation ON operation.id = permission.operation_id;

-- Unique user permisisons
CREATE OR REPLACE VIEW unique_user_permission_vw AS
SELECT
DISTINCT
user_id,
username,
resource, 
name
FROM user_group 
LEFT JOIN group_permission_vw ON user_group.group_id=group_permission_vw.group_id
LEFT JOIN user ON user.id=user_group.user_id;

INSERT INTO operation(name) VALUES ('Read'), ('Create'), ('Delete'), ('Edit');


-- -- User to group mappings
-- SELECT user.username, group.name
-- FROM user_group
-- LEFT JOIN user on user_group.user_id=user.id
-- LEFT JOIN `group` on user_group.group_id=group.id
-- ORDER BY user.username;

-- -- Insert Operations

-- INSERT INTO user(username, password) VALUES ('bob', "JHDJFKDF"), ('alice', "JHDJFKDF");
-- --
-- INSERT INTO `group`(name) VALUES ('regular'), ('privelaged'), ('special');
-- --
-- INSERT INTO permission(resource, operation_id)
-- VALUES ('user.*', 1),
--     ('user.*', 2), ('user.1', 2);
-- --
-- INSERT INTO group_permission (group_id, permission_id)
-- VALUES 
-- (1, 1),
-- (2, 1),
-- (2, 2),
-- (3,1),
-- (3,3);
-- INSERT INTO user_group (user_id, group_id)
-- VALUES 
-- (1, 1),
-- (2, 1),
-- (2,2),
-- (1,3);