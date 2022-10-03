CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE,
    password TEXT,
    role TEXT
);

CREATE TABLE IF NOT EXISTS reviews (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users,
    product_id INTEGER REFERENCES products,
    grade INTEGER,
    content TEXT,
    created_at TIMESTAMP
)

CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    creator_id INTEGER REFERENCES users,
    name TEXT UNIQUE,
    price NUMERIC(11,2),
    description TEXT,
    active BOOLEAN,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES order_details,
    product_id INTEGER REFERENCES products,
    quantity INTEGER,
    unit_price NUMERIC(11,2),
    created_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS cart_items (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users,
    product_id INTEGER REFERENCES products,
    quantity INTEGER,
    created_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS order_details (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users,
    handler_id INTEGER REFERENCES users,
    total_sum NUMERIC(11,2),
    order_state TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

