-- Menu Items table
CREATE TABLE IF NOT EXISTS menu_items (
  id              SERIAL PRIMARY KEY,
  title           VARCHAR(255) NOT NULL,
  price           NUMERIC(10, 2) NOT NULL,
  image_url       TEXT,
  description     TEXT,
  main_category   VARCHAR(100) NOT NULL,
  sub_category    VARCHAR(100)
);

-- Orders table
CREATE TABLE IF NOT EXISTS orders (
  id                SERIAL PRIMARY KEY,
  customer_id       VARCHAR(255) NOT NULL,
  status            VARCHAR(50) NOT NULL DEFAULT 'pending',
  total_price       NUMERIC(10, 2),
  order_time        TIMESTAMP DEFAULT NOW()
);

-- Order Items table
CREATE TABLE IF NOT EXISTS order_items (
  id                SERIAL PRIMARY KEY,
  order_id          INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
  item_id           INTEGER NOT NULL REFERENCES menu_items(id) ON DELETE CASCADE,
  quantity          INTEGER NOT NULL DEFAULT 1,
  customizations    TEXT
);

