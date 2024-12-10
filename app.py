import sqlite3
import os
import random
from datetime import datetime, timedelta

# clear the console screen to improve readability of the menu and content


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# display the main menu with available options for the recipe management system


def display_menu():
    clear_screen()
    print("Recipe Management System:")
    print("1. View Recipes")
    print("2. Add a Recipe")
    print("3. Update a Recipe")
    print("4. Delete a Recipe")
    print("5. Generate Shopping List")
    print("6. Generate Weekly Meal Plan")
    print("7. View All Meal Plans")
    print("8. Delete a Meal Plan")
    print("b. Exit")

# establish a connection to the SQLite database


def connect_db(db_file):
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        return None

# allow users to view recipes, with options to view all recipes or recipes by a specific user


def view_recipes(conn):
    while True:
        clear_screen()
        print("View Recipes:")
        print("1. View all recipes")
        print("2. View recipes by user")
        print("b. Go back to the main menu")

        choice = input("Enter your choice: ").strip().lower()
        if choice == 'b':
            return
        elif choice == '1':
            # fetch and display all recipes with details like category, creator, prep time, etc.
            clear_screen()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT Recipe.recipe_id, Recipe.name, Recipe.prep_time, Recipe.cook_time, Recipe.servings, 
                       Category.name AS category, User.username AS user
                FROM Recipe
                JOIN Category ON Recipe.category_id = Category.category_id
                JOIN User ON Recipe.user_id = User.user_id
            """)
            recipes = cursor.fetchall()
            if recipes:
                print("Recipes:")
                for idx, recipe in enumerate(recipes, start=1):
                    print(f"{idx}. {recipe[1]} (Category: {
                          recipe[5]}, Created by: {recipe[6]})")
                    print(f"   Prep Time: {recipe[2]} mins | Cook Time: {
                          recipe[3]} mins | Servings: {recipe[4]}")
                    print("-" * 30)

                # allow user to select a specific recipe to view more details
                recipe_choice = input(
                    "\nSelect a recipe to view details (number) or 'b' to go back: ").strip()
                if recipe_choice.lower() == 'b':
                    continue

                try:
                    recipe_choice = int(recipe_choice)
                    if 1 <= recipe_choice <= len(recipes):
                        recipe_id = recipes[recipe_choice - 1][0]
                        detailed_recipe_view(conn, recipe_id)
                    else:
                        print("Invalid choice. Please try again.")
                        input("\nPress Enter to continue.")
                except ValueError:
                    print("Invalid input. Please enter a valid number.")
                    input("\nPress Enter to continue.")
            else:
                print("No recipes found.")
                input("\nPress Enter to continue.")
        elif choice == '2':
            # fetch and display recipes by a specific user
            clear_screen()
            cursor = conn.cursor()
            try:  # retrieve list of users
                cursor.execute("SELECT user_id, username FROM User")
                users = cursor.fetchall()
                if not users:
                    print("No users found.")
                    input("\nPress Enter to go back.")
                    return

                print("Users:")
                for idx, user in enumerate(users, start=1):
                    print(f"{idx}. {user[1]}")
                user_choice = input(
                    "\nSelect a user (number) or 'b' to go back: ").strip()
                if user_choice.lower() == 'b':
                    return

                try:
                    user_choice = int(user_choice)
                    if 1 <= user_choice <= len(users):
                        user_id = users[user_choice - 1][0]
                    else:
                        print("Invalid choice. Please try again.")
                        input("\nPress Enter to continue.")
                        continue
                except ValueError:
                    print("Invalid input. Please enter a number.")
                    input("\nPress Enter to continue.")
                    continue

                # fetch recipes for the selected user
                cursor.execute("""
                    SELECT Recipe.recipe_id, Recipe.name, Recipe.prep_time, Recipe.cook_time, Recipe.servings, 
                           Category.name AS category
                    FROM Recipe
                    JOIN Category ON Recipe.category_id = Category.category_id
                    WHERE Recipe.user_id = ?
                """, (user_id,))
                recipes = cursor.fetchall()
                if recipes:
                    print(f"Recipes by {users[user_choice - 1][1]}:")
                    for idx, recipe in enumerate(recipes, start=1):
                        print(f"{idx}. {recipe[1]} (Category: {recipe[5]})")
                        print(f"   Prep Time: {recipe[2]} mins | Cook Time: {
                              recipe[3]} mins | Servings: {recipe[4]}")
                        print("-" * 30)

                    recipe_choice = input(
                        "\nSelect a recipe to view details (number) or 'b' to go back: ").strip()
                    if recipe_choice.lower() == 'b':
                        continue

                    try:
                        recipe_choice = int(recipe_choice)
                        if 1 <= recipe_choice <= len(recipes):
                            recipe_id = recipes[recipe_choice - 1][0]
                            detailed_recipe_view(conn, recipe_id)
                        else:
                            print("Invalid choice. Please try again.")
                            input("\nPress Enter to continue.")
                    except ValueError:
                        print("Invalid input. Please enter a valid number.")
                        input("\nPress Enter to continue.")
                else:
                    print(f"No recipes found for {users[user_choice - 1][1]}.")
                    input("\nPress Enter to continue.")
            except sqlite3.Error as e:
                print(f"Database error: {e}")
                input("\nPress Enter to go back.")

# display detailed information about a specific recipe


def detailed_recipe_view(conn, recipe_id):
    clear_screen()
    cursor = conn.cursor()
    try:  # fetch recipe details including name, instructions, and metadata
        cursor.execute("""
            SELECT Recipe.name, Recipe.instructions, Recipe.prep_time, Recipe.cook_time, Recipe.servings, 
                   Category.name AS category, User.username AS user
            FROM Recipe
            JOIN Category ON Recipe.category_id = Category.category_id
            JOIN User ON Recipe.user_id = User.user_id
            WHERE Recipe.recipe_id = ?
        """, (recipe_id,))
        recipe_details = cursor.fetchone()

        if recipe_details:
            print(f"Recipe: {recipe_details[0]} (Category: {
                  recipe_details[5]}, Created by: {recipe_details[6]})")
            print(f"Prep Time: {recipe_details[2]} mins | Cook Time: {
                  recipe_details[3]} mins | Servings: {recipe_details[4]}")
            print("\nIngredients:")

            # fetch and display ingredients for the recipe
            cursor.execute("""
                SELECT Ingredient.name, RecipeIngredient.quantity, Ingredient.unit_of_measure
                FROM RecipeIngredient
                JOIN Ingredient ON RecipeIngredient.ingredient_id = Ingredient.ingredient_id
                WHERE RecipeIngredient.recipe_id = ?
            """, (recipe_id,))
            ingredients = cursor.fetchall()

            if ingredients:
                for ingredient in ingredients:
                    print(
                        f"- {ingredient[0]}: {ingredient[1]} {ingredient[2]}")
            else:
                print("No ingredients found for this recipe.")

            print("\nInstructions:")
            print(recipe_details[1])
            print("-" * 50)
        else:
            print("Recipe details not found.")

        input("\nPress Enter to return.")
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        input("\nPress Enter to return.")

# user can add their own recipe


def add_recipe(conn):
    while True:
        clear_screen()
        print("Add a New Recipe:")

        cursor = conn.cursor()
        try:

            cursor.execute("SELECT category_id, name FROM Category")
            categories = cursor.fetchall()
            if not categories:
                print("No categories found. Please add categories first.")
                input("\nPress Enter to go back.")
                return

            print("\nAvailable Categories:")
            for idx, category in enumerate(categories, start=1):
                print(f"{idx}. {category[1]}")

            category_choice = input(
                "Select a category (number) or 'b' to go back: ").strip()
            if category_choice.lower() == 'b':
                return
            category_id = int(category_choice) if category_choice.isdigit(
            ) and 1 <= int(category_choice) <= len(categories) else None

            cursor.execute("SELECT user_id, username FROM User")
            users = cursor.fetchall()
            print("\nAvailable Users:")
            for idx, user in enumerate(users, start=1):
                print(f"{idx}. {user[1]}")

            user_choice = input(
                "Select a user (number) or 'b' to go back: ").strip()
            if user_choice.lower() == 'b':
                return
            user_id = int(user_choice) if user_choice.isdigit(
            ) and 1 <= int(user_choice) <= len(users) else None

            # user enters all fields
            name = input("Enter recipe name: ").strip()
            prep_time = input("Enter preparation time (in minutes): ").strip()
            cook_time = input("Enter cooking time (in minutes): ").strip()
            servings = input("Enter number of servings: ").strip()
            instructions = input("Enter instructions: ").strip()

            cursor.execute("""
                INSERT INTO Recipe (name, prep_time, cook_time, servings, instructions, category_id, user_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (name, prep_time, cook_time, servings, instructions, category_id, user_id))
            conn.commit()
            recipe_id = cursor.lastrowid
            print("Recipe added successfully!")

            while True:
                clear_screen()
                print("Add Ingredients:")
                cursor.execute(
                    "SELECT ingredient_id, name, unit_of_measure FROM Ingredient")
                ingredients = cursor.fetchall()
                print("\nAvailable Ingredients:")
                for idx, ingredient in enumerate(ingredients, start=1):
                    print(f"{idx}. {ingredient[1]} ({ingredient[2]})")

                ingredient_choice = input(
                    "\nSelect an ingredient (number) or 'c' to create a new ingredient: ").strip()
                if ingredient_choice.lower() == 'c':
                    create_ingredient(conn, auto_link_recipe_id=recipe_id)
                elif ingredient_choice.isdigit() and 1 <= int(ingredient_choice) <= len(ingredients):
                    ingredient_id = ingredients[int(ingredient_choice) - 1][0]
                    quantity = input(f"Enter quantity for '{
                                     ingredients[int(ingredient_choice) - 1][1]}': ").strip()
                    if quantity:
                        cursor.execute("""
                            INSERT INTO RecipeIngredient (recipe_id, ingredient_id, quantity)
                            VALUES (?, ?, ?)
                        """, (recipe_id, ingredient_id, quantity))
                        conn.commit()
                        print("Ingredient added successfully!")
                else:
                    print("Invalid choice. Please try again.")
                cont = input(
                    "\nWould you like to add another ingredient? (y/n): ").strip().lower()
                if cont != 'y':
                    break

            input("\nPress Enter to return.")
            return
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            input("\nPress Enter to go back.")

# creates ingredient not already in the database


def create_ingredient(conn, auto_link_recipe_id=None):
    clear_screen()
    print("Create New Ingredient:")
    name = input("Enter ingredient name: ").strip()
    unit_of_measure = input(
        "Enter unit of measure (e.g., g, ml, tbsp): ").strip()

    if not name or not unit_of_measure:
        print("Ingredient name and unit of measure cannot be empty.")
        input("\nPress Enter to return.")
        return None

    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO Ingredient (name, unit_of_measure) VALUES (?, ?)", (name, unit_of_measure))
        conn.commit()
        ingredient_id = cursor.lastrowid
        print(f"Ingredient '{name}' created successfully!")

        if auto_link_recipe_id:
            quantity = input(f"Enter quantity for '{
                             name}' (e.g., 200g): ").strip()
            if quantity:
                cursor.execute("""
                    INSERT INTO RecipeIngredient (recipe_id, ingredient_id, quantity)
                    VALUES (?, ?, ?)
                """, (auto_link_recipe_id, ingredient_id, quantity))
                conn.commit()
                print(f"Ingredient '{
                      name}' linked to the recipe successfully!")
        input("\nPress Enter to return.")
        return ingredient_id
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        input("\nPress Enter to return.")
        return None

# edit a recipe


def update_recipe(conn):
    while True:
        clear_screen()
        print("Update Recipe:")

        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT Recipe.recipe_id, Recipe.name, Recipe.prep_time, Recipe.cook_time, 
                       Recipe.servings, Category.name AS category, User.username AS user, Recipe.category_id, Recipe.user_id
                FROM Recipe
                JOIN Category ON Recipe.category_id = Category.category_id
                JOIN User ON Recipe.user_id = User.user_id
            """)
            recipes = cursor.fetchall()
            if not recipes:
                print("No recipes found. Please add recipes first.")
                input("\nPress Enter to go back.")
                return

            print("Available Recipes:")
            for idx, recipe in enumerate(recipes, start=1):
                print(f"{idx}. {recipe[1]} (Category: {
                      recipe[5]}, User: {recipe[6]})")
                print(f"   Prep Time: {recipe[2]} mins | Cook Time: {
                      recipe[3]} mins | Servings: {recipe[4]}")
                print("-" * 30)

            recipe_choice = input(
                "\nSelect a recipe to update (number) or 'b' to go back: ").strip()
            if recipe_choice.lower() == 'b':
                return

            try:
                recipe_choice = int(recipe_choice)
                if 1 <= recipe_choice <= len(recipes):
                    selected_recipe = recipes[recipe_choice - 1]
                    recipe_id = selected_recipe[0]
                else:
                    print("Invalid choice. Please try again.")
                    input("\nPress Enter to continue.")
                    continue
            except ValueError:
                print("Invalid input. Please enter a valid number.")
                input("\nPress Enter to continue.")
                continue

            print(
                "\nEnter new details for the recipe. Press Enter to keep the current value.")

            new_name = input(
                f"New recipe name [{selected_recipe[1]}]: ").strip() or selected_recipe[1]
            new_prep_time = input(f"New prep time (minutes) [{
                                  selected_recipe[2]}]: ").strip() or selected_recipe[2]
            new_cook_time = input(f"New cook time (minutes) [{
                                  selected_recipe[3]}]: ").strip() or selected_recipe[3]
            new_servings = input(
                f"New servings [{selected_recipe[4]}]: ").strip() or selected_recipe[4]

            cursor.execute("SELECT category_id, name FROM Category")
            categories = cursor.fetchall()
            print("\nAvailable Categories:")
            for idx, category in enumerate(categories, start=1):
                print(f"{idx}. {category[1]}")

            category_choice = input(f"Select a new category (number) or press Enter to keep [{
                                    selected_recipe[5]}]: ").strip()
            if category_choice:
                try:
                    category_choice = int(category_choice)
                    if 1 <= category_choice <= len(categories):
                        category_id = categories[category_choice - 1][0]
                    else:
                        print("Invalid category choice. Keeping current category.")
                        category_id = selected_recipe[7]
                except ValueError:
                    print("Invalid input. Keeping current category.")
                    category_id = selected_recipe[7]
            else:
                category_id = selected_recipe[7]

            cursor.execute("SELECT user_id, username FROM User")
            users = cursor.fetchall()
            print("\nAvailable Users:")
            for idx, user in enumerate(users, start=1):
                print(f"{idx}. {user[1]}")

            user_choice = input(f"Select a new user (number) or press Enter to keep [{
                                selected_recipe[6]}]: ").strip()
            if user_choice:
                try:
                    user_choice = int(user_choice)
                    if 1 <= user_choice <= len(users):
                        user_id = users[user_choice - 1][0]
                    else:
                        print("Invalid user choice. Keeping current user.")
                        user_id = selected_recipe[8]
                except ValueError:
                    print("Invalid input. Keeping current user.")
                    user_id = selected_recipe[8]
            else:
                user_id = selected_recipe[8]

            cursor.execute("""
                UPDATE Recipe
                SET name = ?, prep_time = ?, cook_time = ?, servings = ?, category_id = ?, user_id = ?
                WHERE recipe_id = ?
            """, (new_name, new_prep_time, new_cook_time, new_servings, category_id, user_id, recipe_id))
            conn.commit()
            print("Recipe updated successfully!")

            while True:
                clear_screen()
                print("Manage Ingredients:")
                cursor.execute("""
                    SELECT Ingredient.ingredient_id, Ingredient.name, RecipeIngredient.quantity, Ingredient.unit_of_measure
                    FROM RecipeIngredient
                    JOIN Ingredient ON RecipeIngredient.ingredient_id = Ingredient.ingredient_id
                    WHERE RecipeIngredient.recipe_id = ?
                """, (recipe_id,))
                ingredients = cursor.fetchall()
                print("\nCurrent Ingredients:")
                for idx, ingredient in enumerate(ingredients, start=1):
                    print(f"{idx}. {ingredient[1]}: {
                          ingredient[2]} {ingredient[3]}")

                print("\nOptions:")
                print("1. Add an ingredient")
                print("2. Remove an ingredient")
                print("b. Go back")

                choice = input("Enter your choice: ").strip().lower()
                if choice == 'b':
                    break
                elif choice == '1':

                    clear_screen()
                    cursor.execute(
                        "SELECT ingredient_id, name, unit_of_measure FROM Ingredient")
                    all_ingredients = cursor.fetchall()
                    print("\nAvailable Ingredients:")
                    for idx, ingredient in enumerate(all_ingredients, start=1):
                        print(f"{idx}. {ingredient[1]} ({ingredient[2]})")

                    ingredient_choice = input(
                        "\nSelect an ingredient (number) or 'c' to create a new ingredient: ").strip()
                    if ingredient_choice.lower() == 'c':
                        create_ingredient(conn, auto_link_recipe_id=recipe_id)
                    elif ingredient_choice.isdigit() and 1 <= int(ingredient_choice) <= len(all_ingredients):
                        ingredient_id = all_ingredients[int(
                            ingredient_choice) - 1][0]
                        quantity = input(f"Enter quantity for '{
                                         all_ingredients[int(ingredient_choice) - 1][1]}': ").strip()
                        if quantity:
                            cursor.execute("""
                                INSERT INTO RecipeIngredient (recipe_id, ingredient_id, quantity)
                                VALUES (?, ?, ?)
                            """, (recipe_id, ingredient_id, quantity))
                            conn.commit()
                            print("Ingredient added successfully!")
                    else:
                        print("Invalid choice. Please try again.")
                elif choice == '2':

                    if not ingredients:
                        print("No ingredients to remove.")
                        input("\nPress Enter to return.")
                        continue

                    ingredient_choice = input(
                        "Select an ingredient to remove (number): ").strip()
                    try:
                        ingredient_choice = int(ingredient_choice)
                        if 1 <= ingredient_choice <= len(ingredients):
                            ingredient_id = ingredients[ingredient_choice - 1][0]
                            cursor.execute("""
                                DELETE FROM RecipeIngredient
                                WHERE recipe_id = ? AND ingredient_id = ?
                            """, (recipe_id, ingredient_id))
                            conn.commit()
                            print("Ingredient removed successfully!")
                        else:
                            print("Invalid choice. Please try again.")
                    except ValueError:
                        print("Invalid input. Please enter a valid number.")
                    input("\nPress Enter to continue.")
                else:
                    print("Invalid choice. Please try again.")
            input("\nPress Enter to return.")
            return
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            input("\nPress Enter to go back.")

# user can delete a recipe


def delete_recipe(conn):
    while True:
        clear_screen()
        print("Delete Recipe:")

        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT Recipe.recipe_id, Recipe.name, Category.name AS category, User.username AS user
                FROM Recipe
                JOIN Category ON Recipe.category_id = Category.category_id
                JOIN User ON Recipe.user_id = User.user_id
            """)
            recipes = cursor.fetchall()
            if not recipes:
                print("No recipes found. Please add recipes first.")
                input("\nPress Enter to go back.")
                return

            print("Available Recipes:")
            for idx, recipe in enumerate(recipes, start=1):
                print(f"{idx}. {recipe[1]} (Category: {
                      recipe[2]}, User: {recipe[3]})")

            recipe_choice = input(
                "\nSelect a recipe to delete (number) or 'b' to go back: ").strip()
            if recipe_choice.lower() == 'b':
                return

            try:
                recipe_choice = int(recipe_choice)
                if 1 <= recipe_choice <= len(recipes):
                    recipe_id = recipes[recipe_choice - 1][0]
                else:
                    print("Invalid choice. Please try again.")
                    input("\nPress Enter to continue.")
                    continue
            except ValueError:
                print("Invalid input. Please enter a number.")
                input("\nPress Enter to continue.")
                continue

            confirm = input(f"Are you sure you want to delete the recipe '{
                            recipes[recipe_choice - 1][1]}'? (y/n): ").strip().lower()
            if confirm == 'y':
                cursor.execute(
                    "DELETE FROM Recipe WHERE recipe_id = ?", (recipe_id,))
                conn.commit()
                print("Recipe deleted successfully!")
            else:
                print("Deletion canceled.")

            input("\nPress Enter to continue.")
            return

        except sqlite3.Error as e:
            print(f"Database error: {e}")
            input("\nPress Enter to go back.")
            return

# user can make a shopping list from ingredients of a recipe


def generate_shopping_list(conn):
    while True:
        clear_screen()
        print("Generate Shopping List:")

        cursor = conn.cursor()
        try:

            cursor.execute("""
                SELECT Recipe.recipe_id, Recipe.name
                FROM Recipe
            """)
            recipes = cursor.fetchall()
            if not recipes:
                print("No recipes found. Please add recipes first.")
                input("\nPress Enter to go back.")
                return

            print("Available Recipes:")
            for idx, recipe in enumerate(recipes, start=1):
                print(f"{idx}. {recipe[1]}")

            recipe_choices = input(
                "\nSelect recipes to include in the shopping list (comma-separated numbers) or 'b' to go back: ").strip()
            if recipe_choices.lower() == 'b':
                return

            try:
                selected_recipe_ids = [
                    recipes[int(idx.strip()) - 1][0]
                    for idx in recipe_choices.split(',')
                    if idx.strip().isdigit() and 1 <= int(idx.strip()) <= len(recipes)
                ]
                if not selected_recipe_ids:
                    print("No valid recipes selected. Please try again.")
                    input("\nPress Enter to continue.")
                    continue
            except ValueError:
                print("Invalid input. Please enter valid numbers separated by commas.")
                input("\nPress Enter to continue.")
                continue

            placeholders = ', '.join(['?'] * len(selected_recipe_ids))
            cursor.execute(f"""
                SELECT Ingredient.name, SUM(RecipeIngredient.quantity) AS total_quantity, Ingredient.unit_of_measure
                FROM RecipeIngredient
                JOIN Ingredient ON RecipeIngredient.ingredient_id = Ingredient.ingredient_id
                WHERE RecipeIngredient.recipe_id IN ({placeholders})
                GROUP BY Ingredient.name, Ingredient.unit_of_measure
            """, selected_recipe_ids)
            ingredients = cursor.fetchall()

            if ingredients:
                clear_screen()
                print("Shopping List:")
                for ingredient in ingredients:
                    print(
                        f"- {ingredient[0]}: {ingredient[1]} {ingredient[2]}")
            else:
                print("No ingredients found for the selected recipes.")

            input("\nPress Enter to continue.")
            return
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            input("\nPress Enter to go back.")

# make a meal plan for the week based on recipes in the db


def generate_and_save_meal_plan(conn, user_id):
    clear_screen()
    print("Generate Weekly Meal Plan:")

    cursor = conn.cursor()
    try:

        cursor.execute("""
            SELECT Recipe.recipe_id, Recipe.name, Category.name AS category
            FROM Recipe
            JOIN Category ON Recipe.category_id = Category.category_id
            WHERE Category.name NOT IN ('Appetizer', 'Dessert')
        """)
        recipes = cursor.fetchall()

        if not recipes:
            print("No recipes available for meal planning. Please add more recipes.")
            input("\nPress Enter to return.")
            return

        categorized_recipes = {}
        for recipe in recipes:
            category = recipe[2]
            if category not in categorized_recipes:
                categorized_recipes[category] = []
            categorized_recipes[category].append(recipe)

        required_categories = ['Breakfast', 'Lunch', 'Dinner']
        for category in required_categories:
            if category not in categorized_recipes or not categorized_recipes[category]:
                print(f"Insufficient recipes for {
                      category}. Please add more recipes.")
                input("\nPress Enter to return.")
                return

        days = ['Monday', 'Tuesday', 'Wednesday',
                'Thursday', 'Friday', 'Saturday', 'Sunday']
        meal_plan = {}

        shuffled_recipes = {category: random.sample(recipes, len(
            recipes)) for category, recipes in categorized_recipes.items()}

        for day in days:
            meal_plan[day] = {}
            for meal_type in ['Breakfast', 'Lunch', 'Dinner']:

                if not shuffled_recipes[meal_type]:
                    shuffled_recipes[meal_type] = random.sample(
                        categorized_recipes[meal_type], len(categorized_recipes[meal_type]))

                selected_recipe = shuffled_recipes[meal_type].pop()
                meal_plan[day][meal_type] = selected_recipe

        start_date = datetime.now().date()
        end_date = start_date + timedelta(days=6)
        created_at = datetime.now()

        cursor.execute("""
            INSERT INTO MealPlan (user_id, start_date, end_date, created_at)
            VALUES (?, ?, ?, ?)
        """, (user_id, start_date, end_date, created_at))
        conn.commit()
        plan_id = cursor.lastrowid

        for day, meals in meal_plan.items():
            for recipe in meals.values():
                cursor.execute("""
                    INSERT INTO MealPlanRecipe (plan_id, recipe_id)
                    VALUES (?, ?)
                """, (plan_id, recipe[0]))
        conn.commit()

        clear_screen()
        print("Weekly Meal Plan:")
        for day, meals in meal_plan.items():
            print(f"\n{day}:")
            for meal_type, recipe in meals.items():
                print(f"  {meal_type}: {recipe[1]} (Category: {recipe[2]})")
        print(f"\nMeal plan saved successfully with ID: {plan_id}")
        input("\nPress Enter to return.")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        input("\nPress Enter to return.")
    except Exception as e:
        print(f"Unexpected error: {e}")
        input("\nPress Enter to return.")
    finally:
        cursor.close()

# user can see all the meal plans they have generated


def view_all_meal_plans(conn):
    clear_screen()
    print("All Generated Meal Plans:")

    cursor = conn.cursor()
    try:

        cursor.execute("""
            SELECT plan_id, start_date, end_date, created_at
            FROM MealPlan
            ORDER BY created_at DESC
        """)
        meal_plans = cursor.fetchall()

        if not meal_plans:
            print("No meal plans found.")
            input("\nPress Enter to return.")
            return

        for idx, plan in enumerate(meal_plans, start=1):
            print(f"Meal Plan {idx}:")
            print(f"  Start Date: {plan[1]} | End Date: {
                  plan[2]} | Created At: {plan[3]}")
            print("-" * 30)

            cursor.execute("""
                SELECT Recipe.name, Category.name AS category
                FROM MealPlanRecipe
                JOIN Recipe ON MealPlanRecipe.recipe_id = Recipe.recipe_id
                JOIN Category ON Recipe.category_id = Category.category_id
                WHERE MealPlanRecipe.plan_id = ?
            """, (plan[0],))
            recipes = cursor.fetchall()

            for recipe in recipes:
                print(f"  {recipe[1]}: {recipe[0]}")  # Category: Recipe Name
            print("=" * 50)

        input("\nPress Enter to return.")
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        input("\nPress Enter to return.")
    finally:
        cursor.close()

# deletes meal plan user has made


def delete_meal_plan(conn):
    clear_screen()
    print("Delete a Meal Plan:")

    cursor = conn.cursor()
    try:

        cursor.execute("""
            SELECT plan_id, start_date, end_date, created_at
            FROM MealPlan
            ORDER BY created_at DESC
        """)
        meal_plans = cursor.fetchall()

        if not meal_plans:
            print("No meal plans found.")
            input("\nPress Enter to return.")
            return

        for idx, plan in enumerate(meal_plans, start=1):
            print(f"{idx}. Meal Plan (Start Date: {plan[1]} | End Date: {
                  plan[2]} | Created At: {plan[3]})")

        choice = input(
            "\nEnter the number of the meal plan to delete or 'b' to go back: ").strip()
        if choice.lower() == 'b':
            return

        try:
            choice = int(choice)
            if 1 <= choice <= len(meal_plans):
                selected_plan_id = meal_plans[choice - 1][0]

                cursor.execute(
                    "DELETE FROM MealPlanRecipe WHERE plan_id = ?", (selected_plan_id,))
                cursor.execute(
                    "DELETE FROM MealPlan WHERE plan_id = ?", (selected_plan_id,))
                conn.commit()
                print("Meal plan deleted successfully!")
            else:
                print("Invalid selection. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")
        input("\nPress Enter to return.")
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        input("\nPress Enter to return.")
    finally:
        cursor.close()

# exit


def exit_application(conn):
    print("Exiting the application.")
    conn.close()
    exit()


def main():
    db_file = 'Checkpoint2-dbase.sqlite3'
    conn = connect_db(db_file)
    if not conn:
        print("Failed to connect to the database.")
        return

    user_id = 1

    while True:
        display_menu()
        choice = input("\nEnter your choice: ").strip().lower()
        if choice == '1':
            view_recipes(conn)
        elif choice == '2':
            add_recipe(conn)
        elif choice == '3':
            update_recipe(conn)
        elif choice == '4':
            delete_recipe(conn)
        elif choice == '5':
            generate_shopping_list(conn)
        elif choice == '6':
            generate_and_save_meal_plan(conn, user_id)
        elif choice == '7':
            view_all_meal_plans(conn)
        elif choice == '8':
            delete_meal_plan(conn)
        elif choice == 'b':
            print("Goodbye!")
            exit_application(conn)
            break
        else:
            print("Invalid choice. Please try again.")
            input("\nPress Enter to continue.")


if __name__ == "__main__":
    main()
