CREATE DATABASE medibook;
GO
USE medibook
GO

CREATE TABLE users (
    user_id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(255) NOT NULL,
    age INT,
    gender NVARCHAR(20),
    address NVARCHAR(MAX),
    phone NVARCHAR(50) UNIQUE,
    email NVARCHAR(255) UNIQUE,
    password NVARCHAR(255)
);
GO

CREATE TABLE doctors (
    doctor_id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(255) NOT NULL,
    specialty NVARCHAR(255),
    phone NVARCHAR(50) UNIQUE,
    email NVARCHAR(255) UNIQUE
);
GO

CREATE TABLE medicine (
    medicine_id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(255) NOT NULL,
    description NVARCHAR(MAX)
);
GO

CREATE TABLE appointments (
    appointment_id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT,
    doctor_id INT,
    appointment_date DATETIME,
    status NVARCHAR(50),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id)
);
GO

CREATE TABLE prescriptions (
    prescription_id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT,
    doctor_id INT,
    medicine_id INT,
    dosage NVARCHAR(255),
    prescription_date DATETIME,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id),
    FOREIGN KEY (medicine_id) REFERENCES medicine(medicine_id)
);
GO

INSERT INTO users (name, age, gender, address, phone, email, password) VALUES
('Ammar Yaser', 22, 'Male', 'Cairo', '01000000001', 'ammar@example.com', 'pass123'),
('Sara Ahmed', 25, 'Female', 'Giza', '01000000002', 'sara@example.com', 'pass123');
GO

INSERT INTO doctors (name, specialty, phone, email) VALUES
('Dr. Mohamed Ali', 'Cardiology', '01000000003', 'drmo@example.com'),
('Dr. Lina Samir', 'Dermatology', '01000000004', 'drlina@example.com');
GO

INSERT INTO medicine (name, description) VALUES
('Paracetamol', 'Pain reliever'),
('Amoxicillin', 'Antibiotic');
GO

INSERT INTO appointments (user_id, doctor_id, appointment_date, status) VALUES
(1, 1, '2025-01-10 10:00:00', 'Scheduled'),
(2, 2, '2025-01-12 14:30:00', 'Completed');
GO

INSERT INTO prescriptions (user_id, doctor_id, medicine_id, dosage, prescription_date) VALUES
(1, 1, 1, '1 tablet every 8 hours', '2025-01-10 10:10:00'),
(2, 2, 2, '500mg twice daily', '2025-01-12 14:40:00');
GO

SELECT * FROM users;
SELECT * FROM doctors;
SELECT * FROM medicine;
SELECT * FROM appointments;
SELECT * FROM prescriptions;
GO
