-- Select all recipes
SELECT * FROM Recipe;

-- Select all recipes for breakfast
SELECT * FROM Recipe WHERE category_id = 1;

-- Select all recipes created by user with user_id = 1
SELECT * FROM Recipe WHERE user_id = 1;

-- Select all ingredients needed for recipe with recipe_id = 1
SELECT i.name, sli.quantity
FROM Ingredient i
JOIN ShoppingListItem sli ON i.ingredient_id = sli.ingredient_id
JOIN ShoppingList sl ON sli.list_id = sl.list_id
JOIN MealPlanRecipe mpr ON sl.list_id = mpr.plan_id
WHERE mpr.recipe_id = 1;

-- Update the name of recipe with recipe_id = 1
UPDATE Recipe SET name = 'Buttermilk Pancakes' WHERE recipe_id = 1;

UPDATE Recipe SET name = 'Update' WHERE recipe_id = 2;

-- Delete the recipe with recipe_id = 1
DELETE FROM Recipe WHERE recipe_id = 1;

-- Select all categories
SELECT * FROM Category;

-- Select all recipes with cook time less than 30 minutes
SELECT * FROM Recipe WHERE cook_time < 30;

-- Select all meal plans created by user with user_id = 1
SELECT * FROM MealPlan WHERE user_id = 1;

-- Select all recipes in the "Dinner" category (assuming category_id = 2 for Dinner)
SELECT * FROM Recipe WHERE category_id = 2;

-- Select the most recent recipe added by the user with user_id = 1
SELECT * FROM Recipe WHERE user_id = 1 ORDER BY created_at DESC LIMIT 1;

-- Select all ingredients in the shopping list with list_id = 1
SELECT i.name, sli.quantity
FROM Ingredient i
JOIN ShoppingListItem sli ON i.ingredient_id = sli.ingredient_id
WHERE sli.list_id = 1;

-- Update the description of category with category_id = 1
UPDATE Category SET description = 'Updated description' WHERE category_id = 1;

-- Delete the shopping list with list_id = 2
DELETE FROM ShoppingList WHERE list_id = 2;

-- Select all users who created a recipe in the last 7 days
SELECT * FROM User WHERE user_id IN (
    SELECT user_id FROM Recipe WHERE created_at >= DATE('now', '-7 days')
);

-- Select recipes with more than 4 servings
SELECT * FROM Recipe WHERE servings > 4;

-- Select all ingredients not currently assigned to any shopping list
SELECT * FROM Ingredient i
LEFT JOIN ShoppingListItem sli ON i.ingredient_id = sli.ingredient_id
WHERE sli.list_id IS NULL;

-- Select the top 3 most recent meal plans for user_id = 1
SELECT * FROM MealPlan WHERE user_id = 1 ORDER BY created_at DESC LIMIT 3;

-- Count the total number of recipes in each category
SELECT category_id, COUNT(*) AS total_recipes FROM Recipe GROUP BY category_id;

-- Select all recipes with a prep time between 10 and 20 minutes
SELECT * FROM Recipe WHERE prep_time BETWEEN 10 AND 20;

