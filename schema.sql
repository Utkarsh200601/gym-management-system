-- =====================================================================
-- GYM & FITNESS MANAGEMENT SYSTEM - DATABASE SCHEMA
-- Target Environment: MySQL Server (8.0+) / MySQL Workbench
-- Host: 127.0.0.1 | Port: 3306
-- =====================================================================

CREATE DATABASE IF NOT EXISTS gym_db;
USE gym_db;

-- ---------------------------------------------------------------------
-- Table: members
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS payments;
DROP TABLE IF EXISTS members;

CREATE TABLE members (
    member_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    join_date DATE NOT NULL,
    plan_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'Active'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------------------------------------------------------------------
-- Table: payments
-- ---------------------------------------------------------------------
CREATE TABLE payments (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    member_id INT NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    payment_date DATE NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'Paid',
    CONSTRAINT fk_payments_members
        FOREIGN KEY (member_id)
        REFERENCES members(member_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------------------------------------------------------------------
-- Seed Data: 5 Initial Member Records
-- ---------------------------------------------------------------------
INSERT INTO members (member_id, name, phone, email, join_date, plan_type, status) VALUES
(1, 'Alex Mercer', '555-0192', 'alex.mercer@example.com', '2026-01-15', 'Monthly', 'Active'),
(2, 'Sarah Connor', '555-0348', 'sarah.connor@example.com', '2026-02-01', 'Annual', 'Active'),
(3, 'Marcus Vance', '555-0811', 'marcus.v@example.com', '2026-03-10', 'Quarterly', 'Inactive'),
(4, 'Elena Rostova', '555-0924', 'elena.rostova@example.com', '2026-04-05', 'Annual', 'Active'),
(5, 'David Kim', '555-0477', 'david.kim@example.com', '2026-05-18', 'Monthly', 'Active');

-- ---------------------------------------------------------------------
-- Seed Data: Sample Payment Records
-- ---------------------------------------------------------------------
INSERT INTO payments (payment_id, member_id, amount, payment_date, status) VALUES
(1, 1, 49.99, '2026-01-15', 'Paid'),
(2, 2, 499.99, '2026-02-01', 'Paid'),
(3, 3, 139.99, '2026-03-10', 'Paid'),
(4, 4, 499.99, '2026-04-05', 'Paid'),
(5, 5, 49.99, '2026-05-18', 'Paid');

-- Reset Auto-Increment sequence
ALTER TABLE members AUTO_INCREMENT = 6;
ALTER TABLE payments AUTO_INCREMENT = 6;
