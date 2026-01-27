# Carola Car Rental - Entity Relationship Diagram

## ERD Diagram

```mermaid
erDiagram
    Brand {
        NUMBER brand_id PK
        VARCHAR2 brand_name
    }

    CarType {
        NUMBER carType_id PK
        VARCHAR2 carType_name
        VARCHAR2 carType_description
    }

    Customer {
        NUMBER cust_id PK
        VARCHAR2 cust_fname
        VARCHAR2 cust_lname
        NUMBER cust_age
        VARCHAR2 cust_email UK
        VARCHAR2 cust_phone
        VARCHAR2 cust_username UK
        VARCHAR2 cust_password
    }

    Staff {
        NUMBER staff_id PK
        VARCHAR2 staff_fname
        VARCHAR2 staff_lname
        VARCHAR2 staff_email UK
        VARCHAR2 staff_phone
        VARCHAR2 staff_dept
        VARCHAR2 staff_username UK
        VARCHAR2 staff_password
        NUMBER manager_id FK
    }

    Model {
        NUMBER model_id PK
        VARCHAR2 model_name
        NUMBER brand_id FK
        VARCHAR2 attachments
    }

    Location {
        NUMBER location_id PK
        VARCHAR2 location_name
        VARCHAR2 address
        VARCHAR2 city
        VARCHAR2 state
        VARCHAR2 postal_code
        VARCHAR2 country
        VARCHAR2 phone
        VARCHAR2 email
        VARCHAR2 opening_time
        VARCHAR2 closing_time
        NUMBER is_airport
        NUMBER is_active
    }

    Car {
        NUMBER car_id PK
        NUMBER model_id FK
        NUMBER carType_id FK
        NUMBER location_id FK
        NUMBER rate
        VARCHAR2 description
        NUMBER door
        NUMBER suitcase
        NUMBER seat
        VARCHAR2 colour
        VARCHAR2 car_status
        NUMBER allows_different_dropoff
    }

    Petrol {
        NUMBER car_id PK
        NUMBER octane_rating
        NUMBER fuel_tank_capacity
    }

    Diesel {
        NUMBER car_id PK
        VARCHAR2 diesel_emission
        NUMBER fuel_tank_capacity
    }

    Electric {
        NUMBER car_id PK
        NUMBER battery_range
        NUMBER charging_rate_kw
        DATE last_charging_date
    }

    Booking {
        NUMBER booking_id PK
        NUMBER cust_id FK
        NUMBER staff_id FK
        NUMBER car_id FK
        NUMBER pickup_location_id FK
        NUMBER dropoff_location_id FK
        DATE pickup_date
        DATE dropoff_date
        NUMBER price
        VARCHAR2 booking_status
        DATE created_at
    }

    Payment {
        NUMBER booking_id PK
        NUMBER amount
        DATE payment_date
    }

    Brand ||--o{ Model : has
    Model ||--o{ Car : has
    CarType ||--o{ Car : categorizes
    Location ||--o{ Car : stores
    Petrol ||--|| Car : extends
    Diesel ||--|| Car : extends
    Electric ||--|| Car : extends
    Staff ||--o{ Staff : manages
    Customer ||--o{ Booking : makes
    Staff ||--o{ Booking : handles
    Car ||--o{ Booking : booked-in
    Location ||--o{ Booking : pickup-at
    Location ||--o{ Booking : dropoff-at
    Booking ||--o| Payment : paid-via
```

## Table Summary

| Table | Description | Key Relationships |
|-------|-------------|-------------------|
| **Brand** | Car manufacturers (Toyota, Honda, etc.) | → Model |
| **CarType** | Vehicle categories (Sedan, SUV, etc.) | → Car |
| **Customer** | Registered customers | → Booking |
| **Staff** | Employees (self-referencing for managers) | → Booking, → Staff |
| **Model** | Car models with shared image | ← Brand, → Car |
| **Location** | Branch locations (airports, city centers) | → Car, → Booking |
| **Car** | Physical car units (fleet inventory) | ← Model, ← CarType, ← Location |
| **Petrol** | Petrol car specifications | ← Car (inheritance) |
| **Diesel** | Diesel car specifications | ← Car (inheritance) |
| **Electric** | Electric car specifications | ← Car (inheritance) |
| **Booking** | Rental reservations | ← Customer, ← Staff, ← Car, ← Location |
| **Payment** | Payment records (1:1 with Booking) | ← Booking |

## Key Features

### 🚗 Fleet Inventory System
- **One Model → Many Cars**: Same car model can have multiple physical units
- **Car ↔ Location**: Each car unit is assigned to one home location
- **Independent Availability**: Renting a car at KLIA doesn't affect the same model at Penang

### 📍 Location Management
- Supports airports (24-hour) and city branches
- Flexible pickup/dropoff locations
- `allows_different_dropoff` flag per car

### 🔋 Fuel Type Inheritance {Mandatory, Or}
**Disjoint Mandatory Specialization**: Every Car MUST be exactly ONE of:
- **Petrol**: octane_rating, fuel_tank_capacity
- **Diesel**: diesel_emission, fuel_tank_capacity  
- **Electric**: battery_range, charging_rate_kw, last_charging_date

> ⚠️ Note: Mermaid ERD cannot display the UML triangle notation. The `||--||` relationships indicate 1:1 mandatory from subtypes to Car.

### 📊 Status Tracking
- **Car Status**: Available, Rented, Maintenance, Dirty
- **Booking Status**: Confirmed, In Progress, Completed, Cancelled

### 🖼️ Image Management
- Images stored at **Model level** (not Car level)
- All cars of same model share one image

