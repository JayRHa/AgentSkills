# Worked Example: E-commerce Schema (PostgreSQL)

## Input requirements

> We sell products organized into categories. Customers place orders; each order
> contains many line items, each line item is a quantity of one product. Products
> can be tagged with many tags, and a tag applies to many products. We must record
> the price the customer actually paid (prices change over time). Show me the schema.

## Step 1 — Entities

`category`, `product`, `customer`, `order`, `order_item` (line item), `tag`, plus the
many-to-many link `product_tag`.

## Step 2 — Relationships & cardinality

- category 1 : N product
- customer 1 : N order
- order 1 : N order_item   (line items are *owned* by the order)
- product 1 : N order_item
- product M : N tag        (junction table product_tag)

## Step 3 — Key decisions

- Surrogate `*_id` identity PKs everywhere except the junction table.
- `product_tag` uses a composite PK `(product_id, tag_id)` — no surrogate needed.
- Natural keys protected by UNIQUE: `customer.email`, `product.sku`, `category.name`, `tag.name`.
- `order_item.unit_price` is a deliberate **snapshot** of price at sale time (intentional, not a 3NF violation).

## Step 4 — DDL (dependency order)

```sql
CREATE TABLE category (
  category_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  name        VARCHAR(100) NOT NULL,
  CONSTRAINT uq_category_name UNIQUE (name)
);

CREATE TABLE tag (
  tag_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  name   VARCHAR(60) NOT NULL,
  CONSTRAINT uq_tag_name UNIQUE (name)
);

CREATE TABLE product (
  product_id  BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  sku         VARCHAR(40)   NOT NULL,
  name        VARCHAR(200)  NOT NULL,
  unit_price  NUMERIC(12,2) NOT NULL CHECK (unit_price >= 0),
  category_id BIGINT NOT NULL REFERENCES category(category_id)
                ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT uq_product_sku UNIQUE (sku)
);
CREATE INDEX ix_product_category ON product(category_id);

CREATE TABLE product_tag (
  product_id BIGINT NOT NULL REFERENCES product(product_id) ON DELETE CASCADE,
  tag_id     BIGINT NOT NULL REFERENCES tag(tag_id)         ON DELETE CASCADE,
  PRIMARY KEY (product_id, tag_id)
);
CREATE INDEX ix_product_tag_tag ON product_tag(tag_id);  -- reverse-direction joins

CREATE TABLE customer (
  customer_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  email       VARCHAR(254) NOT NULL,
  full_name   VARCHAR(200) NOT NULL,
  created_at  TIMESTAMPTZ  NOT NULL DEFAULT now(),
  CONSTRAINT uq_customer_email UNIQUE (email)
);

CREATE TABLE "order" (
  order_id    BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  customer_id BIGINT NOT NULL REFERENCES customer(customer_id)
                ON UPDATE CASCADE ON DELETE RESTRICT,
  status      VARCHAR(20) NOT NULL DEFAULT 'pending'
                CHECK (status IN ('pending','paid','shipped','cancelled')),
  ordered_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX ix_order_customer ON "order"(customer_id);
CREATE INDEX ix_order_status   ON "order"(status);

CREATE TABLE order_item (
  order_id   BIGINT  NOT NULL REFERENCES "order"(order_id) ON DELETE CASCADE,
  product_id BIGINT  NOT NULL REFERENCES product(product_id) ON DELETE RESTRICT,
  quantity   INTEGER NOT NULL CHECK (quantity > 0),
  unit_price NUMERIC(12,2) NOT NULL CHECK (unit_price >= 0),  -- snapshot
  PRIMARY KEY (order_id, product_id)
);
CREATE INDEX ix_order_item_product ON order_item(product_id);
```

## Step 5 — Why each anomaly is avoided

- **1NF:** tags are rows in `product_tag`, not a CSV column on product.
- **2NF:** `order_item` holds only quantity/price (depend on whole PK); product name lives in `product`.
- **3NF:** category name is in `category`, not duplicated on product.
- **Snapshot:** historical price preserved via `order_item.unit_price` while current price stays on `product`.

## Optional denormalization (only if reporting is slow)

Add `order.total_amount NUMERIC(14,2)` maintained by a trigger on `order_item`
insert/update/delete. Documented: source of truth = sum of `order_item`; sync =
trigger; staleness = none (synchronous).
