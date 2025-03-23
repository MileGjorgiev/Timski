import pygame
import random
from transformers import pipeline

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 600, 650
GRID_SIZE = 8
TILE_SIZE = WIDTH // GRID_SIZE

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
COLORS = [
    (255, 0, 0),    # Red
    (0, 255, 0),    # Green
    (0, 0, 255),    # Blue
    (255, 255, 0),  # Yellow
    (255, 0, 255),  # Magenta
    (0, 255, 255),  # Cyan
]

# Initialize screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Candy Crush Clone")

# Clock
clock = pygame.time.Clock()

# Font
font = pygame.font.Font(None, 36)

# Grid
grid = [[random.choice(COLORS) for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

# Score and Level
score = 0
level = 1
target_score = 1000  # Target score for every level

# Move Limit
move_limit = 20  # Initial move limit
moves_remaining = move_limit

# Special Tiles
SPECIAL_TILE = (255, 255, 255)  # White color for special tiles

# Animation variables
falling_tiles = []  # Stores tiles that are currently falling

# Player performance history
player_performance = []  # Stores moves remaining for the last 3 levels

# Load Hugging Face's GPT-2 model for text generation
generator = pipeline("text-generation", model="gpt2")

# Function to get difficulty adjustment from Hugging Face's GPT-2
def get_difficulty_adjustment(player_performance):
    """
    Uses Hugging Face's GPT-2 to generate a difficulty adjustment recommendation.
    """
    prompt = (
        f"The player has completed {len(player_performance)} levels with the following moves remaining: {player_performance}. "
        "Based on this data, should the game become easier, harder, or stay the same? "
        "Respond with 'easier', 'harder', or 'same'."
    )

    # Generate a response using GPT-2
    response = generator(
        prompt,
        max_new_tokens=30,  # Generate up to 30 new tokens
        truncation=True,    # Explicitly enable truncation
        num_return_sequences=1
    )
    recommendation = response[0]["generated_text"].strip().lower()

    # Extract the recommendation
    if "easier" in recommendation:
        return "easier"
    elif "harder" in recommendation:
        return "harder"
    else:
        return "same"

# Function to adjust difficulty based on AI's recommendation
def adjust_difficulty(player_performance):
    recommendation = get_difficulty_adjustment(player_performance)

    global move_limit
    if recommendation == "easier":
        move_limit = min(30, move_limit + 2)  # Increase move limit (make easier)
    elif recommendation == "harder":
        move_limit = max(10, move_limit - 2)  # Decrease move limit (make harder)
    # If "same", do nothing

# Function to check if level is completed
def check_level_completed():
    global score, level, target_score, moves_remaining, player_performance
    if score >= target_score:
        # Store player performance (moves remaining)
        player_performance.append(moves_remaining)

        # Adjust difficulty based on AI recommendation
        adjust_difficulty(player_performance)

        # Reset for the next level
        level += 1
        score = 0
        moves_remaining = move_limit
        reset_grid()

# Function to reset the grid for a new level
def reset_grid():
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            grid[y][x] = random.choice(COLORS)

# Function to draw the grid
def draw_grid():
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            if grid[y][x] is not None:
                pygame.draw.rect(screen, grid[y][x], (x * TILE_SIZE, y * TILE_SIZE + 50, TILE_SIZE, TILE_SIZE))
                pygame.draw.rect(screen, BLACK, (x * TILE_SIZE, y * TILE_SIZE + 50, TILE_SIZE, TILE_SIZE), 1)

# Function to swap tiles
def swap_tiles(pos1, pos2):
    grid[pos1[1]][pos1[0]], grid[pos2[1]][pos2[0]] = grid[pos2[1]][pos2[0]], grid[pos1[1]][pos1[0]]

# Function to check for matches
def check_matches():
    matches = []
    # Check horizontal matches
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE - 2):
            if grid[y][x] == grid[y][x + 1] == grid[y][x + 2] and grid[y][x] is not None:
                matches.append(((x, y), (x + 1, y), (x + 2, y)))
    # Check vertical matches
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE - 2):
            if grid[y][x] == grid[y + 1][x] == grid[y + 2][x] and grid[y][x] is not None:
                matches.append(((x, y), (x, y + 1), (x, y + 2)))
    return matches

# Function to remove matches and update score
def remove_matches(matches):
    global score
    for match in matches:
        if len(match) == 3:  # Match of 3 tiles
            score += 50
        elif len(match) >= 4:  # Match of 4 or more tiles
            score += 100
        for x, y in match:
            if grid[y][x] == SPECIAL_TILE:
                # Clear entire row or column
                if random.choice([True, False]):
                    for i in range(GRID_SIZE):
                        if grid[y][i] != SPECIAL_TILE:
                            grid[y][i] = None
                else:
                    for i in range(GRID_SIZE):
                        if grid[i][x] != SPECIAL_TILE:
                            grid[i][x] = None
            grid[y][x] = None

# Function to handle falling tiles animation
def handle_falling_tiles():
    global falling_tiles
    for tile in falling_tiles:
        tile["y"] += 5  # Move tile down
        if tile["y"] >= (tile["target_y"] * TILE_SIZE) + 50:
            grid[tile["target_y"]][tile["x"]] = tile["color"]
            falling_tiles.remove(tile)

# Function to fill empty spaces with falling animation
def fill_empty_spaces_with_animation():
    global falling_tiles
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE - 1, -1, -1):
            if grid[y][x] is None:
                for y2 in range(y - 1, -1, -1):
                    if grid[y2][x] is not None:
                        falling_tiles.append({
                            "x": x,
                            "y": y2 * TILE_SIZE + 50,
                            "target_y": y,
                            "color": grid[y2][x]
                        })
                        grid[y2][x] = None
                        break
                else:
                    grid[y][x] = random.choice(COLORS)

# Function to create special tiles
def create_special_tiles(matches):
    for match in matches:
        if len(match) >= 4:
            x, y = match[0]
            grid[y][x] = SPECIAL_TILE

# Function to check for cascading matches
def check_cascading_matches():
    """
    Checks for new matches after tiles fall and resolves them.
    """
    while True:
        matches = check_matches()
        if not matches:
            break
        create_special_tiles(matches)
        remove_matches(matches)
        fill_empty_spaces_with_animation()
        # Wait for falling tiles to settle
        while falling_tiles:
            handle_falling_tiles()
            draw_grid()
            draw_score_level_and_moves()
            pygame.display.flip()
            clock.tick(30)  # Limit the frame rate to avoid freezing
            # Process events to prevent "Not Responding"
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

# Function to draw score, level, and moves remaining
def draw_score_level_and_moves():
    score_text = font.render(f"Score: {score}", True, BLACK)
    level_text = font.render(f"Level: {level}", True, BLACK)
    moves_text = font.render(f"Moves: {moves_remaining}", True, BLACK)
    screen.blit(score_text, (10, 10))
    screen.blit(level_text, (WIDTH - 150, 10))
    screen.blit(moves_text, (WIDTH // 2 - 50, 10))

# Function to display game over message
def display_game_over():
    game_over_text = font.render("Game Over: Out of Moves", True, BLACK)
    screen.blit(game_over_text, (WIDTH // 2 - 150, HEIGHT // 2))
    pygame.display.flip()
    pygame.time.wait(3000)  # Wait for 3 seconds before quitting
    pygame.quit()

# Main game loop
selected_tile = None
running = True
while running:
    screen.fill(WHITE)
    draw_grid()
    draw_score_level_and_moves()

    # Handle falling tiles animation
    handle_falling_tiles()

    # Check if moves are exhausted
    if moves_remaining <= 0:
        display_game_over()
        running = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if moves_remaining > 0:  # Only allow moves if moves are remaining
                x, y = event.pos
                grid_x, grid_y = x // TILE_SIZE, (y - 50) // TILE_SIZE
                if 0 <= grid_x < GRID_SIZE and 0 <= grid_y < GRID_SIZE:
                    if selected_tile is None:
                        selected_tile = (grid_x, grid_y)
                    else:
                        # Check if the same tile is clicked twice
                        if selected_tile == (grid_x, grid_y):
                            selected_tile = None  # Deselect the tile
                        else:
                            # Swap tiles
                            swap_tiles(selected_tile, (grid_x, grid_y))
                            matches = check_matches()
                            if not matches:
                                # Swap back if no match is found
                                swap_tiles(selected_tile, (grid_x, grid_y))
                            else:
                                # If a match is found, process the match
                                create_special_tiles(matches)
                                remove_matches(matches)
                                fill_empty_spaces_with_animation()
                                # Check for cascading matches after tiles settle
                                check_cascading_matches()
                                # Check if level is completed
                                check_level_completed()
                                # Deduct a move only if the swap resulted in a valid match
                                moves_remaining -= 1
                            selected_tile = None

    pygame.display.flip()
    clock.tick(30)  # Limit the frame rate to avoid freezing

pygame.quit()