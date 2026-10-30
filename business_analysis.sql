USE food_orders_analytics_db;

-- 1. Total order value
SELECT SUM(`Order Value`) AS total_order_value
FROM cleaned_food_orders;

-- 2. Average order value
SELECT AVG(`Order Value`) AS average_order_value
FROM cleaned_food_orders;

-- 3. Payment method with the highest number of orders
SELECT `Payment Method`, COUNT(*) AS order_count
FROM cleaned_food_orders
GROUP BY `Payment Method`
ORDER BY order_count DESC
LIMIT 1;

-- 4. Order channel with the highest number of orders
SELECT `Order Channel`, COUNT(*) AS order_count
FROM cleaned_food_orders
GROUP BY `Order Channel`
ORDER BY order_count DESC
LIMIT 1;

-- 5. Average delivery time in minutes
SELECT AVG(Delivery_Time_Minutes) AS average_delivery_minutes
FROM cleaned_food_orders
WHERE Delivery_Time_Minutes >= 0;

-- 6. Total platform net revenue
SELECT SUM(Platform_Net_Revenue) AS total_platform_net_revenue
FROM cleaned_food_orders;
