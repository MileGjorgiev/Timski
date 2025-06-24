import pygame
import random
import os
import json
from transformers import pipeline

from AIModule import AIModule

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 600, 650
GRID_SIZE = 8
TILE_SIZE = WIDTH // GRID_SIZE
LEVEL_TRANSITION_DELAY = 1500  # 1.5 seconds

# Initialize screen FIRST (before loading images)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Candy Crush Clone")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (255, 0, 0)

# Font initialization (after screen is created)
font = pygame.font.Font(None, 36)
large_font = pygame.font.Font(None, 72)

SAVE_FILE = "sava_data.json"
player_data = None


def load_player_data():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, 'r') as f:
            return json.load(f)
    return None


def save_player_data(name, highscore):
    with open(SAVE_FILE, 'w') as f:
        json.dump({'name': name, 'highscore': highscore}, f)


def get_name_input(screen, font):
    name = ""
    active = True
    input_font = pygame.font.Font(None, 48)
    input_box = pygame.Rect(WIDTH // 2 - 150, 270, 300, 50)

    while active:
        screen.fill(WHITE)
        prompt = font.render("Enter your name:", True, BLACK)
        pygame.draw.rect(screen, (230, 230, 230), input_box)  # background
        pygame.draw.rect(screen, BLACK, input_box, 2)  # border
        text_surface = input_font.render(name, True, BLACK)
        screen.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, 200))
        screen.blit(text_surface, (input_box.x + 10, input_box.y + 10))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and name.strip():
                    return name.strip()
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif len(name) < 12 and event.unicode.isprintable():
                    name += event.unicode


def show_opening_screen(screen, font, player_data):
    screen.fill(WHITE)
    try:
        title_img = pygame.image.load("images/Candy Crush Clone.png")
        title_img = pygame.transform.scale(title_img, (500, 300))
        screen.blit(title_img, (WIDTH // 2 - 250, 80))
    except:
        fallback = font.render("Candy Crush Clone", True, BLACK)
        screen.blit(fallback, (WIDTH // 2 - fallback.get_width() // 2, 100))

    if player_data:
        welcome = font.render(f"Welcome, {player_data['name']}!", True, BLACK)
        highscore = font.render(f"Highscore: {player_data['highscore']}", True, BLACK)
        screen.blit(welcome, (WIDTH // 2 - welcome.get_width() // 2, 330))
        screen.blit(highscore, (WIDTH // 2 - highscore.get_width() // 2, 360))
        prompt = font.render("Press any key to start", True, BLACK)
        screen.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, 420))
    else:
        prompt = font.render("Press any key to begin", True, BLACK)
        screen.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, 420))

    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                waiting = False


# Load player data and show intro screen
player_data = load_player_data()
show_opening_screen(screen, font, player_data)

if not player_data:
    name = get_name_input(screen, font)
    player_data = {'name': name, 'highscore': 0}
    save_player_data(name, 0)

# Now load images (with proper error handling)
IMAGESDICT = {}
candy_colors = ['blue', 'green', 'orange', 'purple', 'red', 'yellow']

try:
    # Try to load actual images
    for color in candy_colors:
        try:
            IMAGESDICT[f'{color} candy'] = pygame.image.load(f"images/{color}-candy.png").convert_alpha()
        except:
            # If specific image fails, create a colored rectangle
            surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            if color == 'blue':
                pygame.draw.rect(surf, (0, 0, 255), (2, 2, TILE_SIZE - 4, TILE_SIZE - 4), 0, 10)
            elif color == 'green':
                pygame.draw.rect(surf, (0, 255, 0), (2, 2, TILE_SIZE - 4, TILE_SIZE - 4), 0, 10)
            elif color == 'orange':
                pygame.draw.rect(surf, (255, 165, 0), (2, 2, TILE_SIZE - 4, TILE_SIZE - 4), 0, 10)
            elif color == 'purple':
                pygame.draw.rect(surf, (128, 0, 128), (2, 2, TILE_SIZE - 4, TILE_SIZE - 4), 0, 10)
            elif color == 'red':
                pygame.draw.rect(surf, (255, 0, 0), (2, 2, TILE_SIZE - 4, TILE_SIZE - 4), 0, 10)
            elif color == 'yellow':
                pygame.draw.rect(surf, (255, 255, 0), (2, 2, TILE_SIZE - 4, TILE_SIZE - 4), 0, 10)
            IMAGESDICT[f'{color} candy'] = surf
        try:
            IMAGESDICT['blocker'] = pygame.image.load("images/rock.png").convert_alpha()
        except:
            surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
            surf.fill((100, 100, 100))  # Gray color
            pygame.draw.rect(surf, (50, 50, 50), (2, 2, TILE_SIZE - 4, TILE_SIZE - 4), 0, 8)
            IMAGESDICT['blocker'] = surf



except Exception as e:
    print(f"Error loading images: {e}")
    # Fallback: create all colored rectangles
    IMAGESDICT = {}
    colors = [
        ('blue candy', (0, 0, 255)),
        ('green candy', (0, 255, 0)),
        ('orange candy', (255, 165, 0)),
        ('purple candy', (128, 0, 128)),
        ('red candy', (255, 0, 0)),
        ('yellow candy', (255, 255, 0))
    ]
    for name, color in colors:
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(surf, color, (2, 2, TILE_SIZE - 4, TILE_SIZE - 4), 0, 10)
        IMAGESDICT[name] = surf

CANDY_TILES = [key for key in IMAGESDICT.keys() if key != 'blocker']


# Game state class with all necessary methods
class GameState:
    def __init__(self):
        self.grid = [[random.choice(CANDY_TILES) for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.score = 0
        self.level = 1
        self.total_score = 0
        self.target_score = 1000
        self.move_limit = 20
        self.moves_remaining = self.move_limit
        self.falling_tiles = []
        self.player_performance = []
        self.selected_tile = None
        self.animating = False
        self.game_over = False
        self.ensure_no_matches_at_start()
        self.blocker_positions = set()
        self.place_blockers_for_level()
        self.ai = AIModule()
        self.level_start_time = pygame.time.get_ticks()
        self.level_time_limit = 60  # Initial time limit (seconds)
        self.time_remaining = self.level_time_limit
        self.level_start_time = pygame.time.get_ticks()

    def place_blockers_for_level(self):
        self.blocker_positions.clear()

        if self.level < 2:
            return  # No blockers on level 1

        num_blockers = (self.level - 1) * 2

        placed = 0
        while placed < num_blockers:
            x = random.randint(0, GRID_SIZE - 1)
            y = random.randint(0, GRID_SIZE - 1)
            # Only place if empty or candy, NOT if blocker or something else
            if self.grid[y][x] != 'blocker':
                self.grid[y][x] = 'blocker'
                self.blocker_positions.add((x, y))
                placed += 1

    def ensure_no_matches_at_start(self):
        """Ensure there are no matches when the game starts or level resets"""
        while True:
            matches = self.check_matches()
            if not matches:
                break
            # Reshuffle the grid if there are matches at start
            for y in range(GRID_SIZE):
                for x in range(GRID_SIZE):
                    self.grid[y][x] = random.choice(CANDY_TILES)  # Only candy tiles, no blockers

    def check_matches(self):
        """Check for all matches on the board, ignoring blockers"""
        matches = []

        # Check horizontal matches
        for y in range(GRID_SIZE):
            x = 0
            while x < GRID_SIZE - 2:
                current = self.grid[y][x]
                if current is None or current == 'blocker':
                    x += 1
                    continue
                match_length = 1
                while x + match_length < GRID_SIZE and self.grid[y][x + match_length] == current:
                    if self.grid[y][x + match_length] == 'blocker':
                        break  # Stop match at blocker
                    match_length += 1
                if match_length >= 3:
                    matches.append([(x + i, y) for i in range(match_length)])
                    x += match_length
                else:
                    x += 1

        # Check vertical matches
        for x in range(GRID_SIZE):
            y = 0
            while y < GRID_SIZE - 2:
                current = self.grid[y][x]
                if current is None or current == 'blocker':
                    y += 1
                    continue
                match_length = 1
                while y + match_length < GRID_SIZE and self.grid[y + match_length][x] == current:
                    if self.grid[y + match_length][x] == 'blocker':
                        break  # Stop match at blocker
                    match_length += 1
                if match_length >= 3:
                    matches.append([(x, y + i) for i in range(match_length)])
                    y += match_length
                else:
                    y += 1

        return matches

    def remove_matches(self, matches):
        """Remove matched tiles and update score"""
        if not matches:
            return False

        # Flatten the list of matches and remove duplicates
        all_positions = set()
        for match in matches:
            for pos in match:
                all_positions.add(pos)

        # Score calculation (more points for longer matches)
        for match in matches:
            length = len(match)
            if length == 3:
                points = 50
            elif length == 4:
                points = 100
            else:  # 5 or more
                points = 150

            self.score += points
            self.total_score += points
        for x, y in all_positions:
            if self.grid[y][x] != 'blocker':
                self.grid[y][x] = None

        return True

    def handle_falling_tiles(self):
        """Handle the animation of falling tiles"""
        if not self.falling_tiles:
            return False

        for tile in self.falling_tiles[:]:
            tile["y"] += 10  # Falling speed

            # Check if tile has reached its destination
            if tile["y"] >= (tile["target_y"] * TILE_SIZE) + 50:
                self.grid[tile["target_y"]][tile["x"]] = tile["type"]
                self.falling_tiles.remove(tile)

        return True

    def handle_swap(self, pos1, pos2, screen):
        """Handle the complete swap logic with match checking"""
        # First swap the tiles
        self.swap_tiles(pos1, pos2)

        # Check if this created any matches
        matches = self.check_matches()

        if matches:
            # If we have matches:
            self.animating = True
            self.animate_swap(pos1, pos2, screen)

            # Process all matches and cascades
            while True:
                # Remove matches and get score
                self.remove_matches(matches)

                # Make candies fall
                self.fill_empty_spaces()

                # Wait for all candies to finish falling
                while self.handle_falling_tiles():
                    self.draw_all(screen)
                    pygame.display.flip()
                    clock.tick(60)

                # Check for new matches from cascades
                matches = self.check_matches()
                if not matches:
                    break


        else:
            # If no matches, swap back but still count the move
            self.animate_swap(pos1, pos2, screen)  # Visual swap back
            self.swap_tiles(pos1, pos2)  # Actually swap back in grid
            self.animate_swap(pos2, pos1, screen)  # Visual return to original

        # ALWAYS decrease moves, whether match was made or not
        self.moves_remaining -= 1
        self.selected_tile = None
        self.animating = False

    def draw_all(self, screen):
        """Helper to draw everything"""
        screen.fill(WHITE)
        self.draw_grid(screen)
        self.draw_score_level_and_moves(screen)

    def fill_empty_spaces(self):
        """Fill empty spaces in the grid with falling tiles, ignoring blockers"""
        made_changes = False

        for x in range(GRID_SIZE):
            empty_slots = []

            # Step 1: From bottom to top, collect empty y positions (but skip blockers)
            for y in range(GRID_SIZE - 1, -1, -1):
                if self.grid[y][x] is None:
                    empty_slots.append(y)
                elif self.grid[y][x] == 'blocker':
                    continue
                elif empty_slots:
                    # Move this tile down to the lowest available empty slot
                    new_y = empty_slots.pop(0)
                    self.falling_tiles.append({
                        "x": x,
                        "y": y * TILE_SIZE + 50,
                        "target_y": new_y,
                        "type": self.grid[y][x]
                    })
                    self.grid[y][x] = None
                    empty_slots.append(y)  # The tile just moved creates a new empty spot
                    made_changes = True

            # Step 2: Add new tiles from the top for remaining empty slots
            for i, y in enumerate(reversed(empty_slots)):
                self.falling_tiles.append({
                    "x": x,
                    "y": -((i + 1) * TILE_SIZE) + 50,
                    "target_y": y,
                    "type": random.choice(list(IMAGESDICT.keys() - {'blocker'}))
                })
                made_changes = True

        return made_changes

    def process_matches(self):
        """Process all matches and cascading effects"""
        while True:
            # Handle any falling tiles first
            if self.handle_falling_tiles():
                return True  # Need to wait for animation

            # Check for matches
            matches = self.check_matches()
            if not matches:
                break

            # Remove matches and fill empty spaces
            self.remove_matches(matches)
            self.fill_empty_spaces()

        return False

    def draw_grid(self, screen):
        """Draw the game grid with tiles"""
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                if self.grid[y][x] is not None:
                    screen.blit(IMAGESDICT[self.grid[y][x]], (x * TILE_SIZE, y * TILE_SIZE + 50))

        # Draw selection highlight
        if self.selected_tile:
            x, y = self.selected_tile
            pygame.draw.rect(screen, (255, 255, 255), (x * TILE_SIZE, y * TILE_SIZE + 50, TILE_SIZE, TILE_SIZE), 3)

    def is_adjacent(self, pos1, pos2):
        """Check if two positions are adjacent"""

        x1, y1 = pos1
        x2, y2 = pos2
        return (abs(x1 - x2) == 1 and y1 == y2) or (abs(y1 - y2) == 1 and x1 == x2)

    def swap_tiles(self, pos1, pos2):
        """Swap two tiles on the grid"""
        x1, y1 = pos1
        x2, y2 = pos2
        self.grid[y1][x1], self.grid[y2][x2] = self.grid[y2][x2], self.grid[y1][x1]

    def animate_swap(self, tile1_pos, tile2_pos, screen, speed=8):
        """Animate the swap between two tiles"""
        x1, y1 = tile1_pos
        x2, y2 = tile2_pos

        # Get initial positions
        tile1_rect = pygame.Rect(x1 * TILE_SIZE, y1 * TILE_SIZE + 50, TILE_SIZE, TILE_SIZE)
        tile2_rect = pygame.Rect(x2 * TILE_SIZE, y2 * TILE_SIZE + 50, TILE_SIZE, TILE_SIZE)

        # Calculate direction vectors
        dx1 = (x2 - x1) * speed
        dy1 = (y2 - y1) * speed
        dx2 = (x1 - x2) * speed
        dy2 = (y1 - y2) * speed

        # Perform the animation
        distance = max(abs(x2 - x1), abs(y2 - y1)) * TILE_SIZE
        steps = distance // speed

        for _ in range(steps):
            screen.fill(WHITE)

            # Move tiles
            tile1_rect.x += dx1
            tile1_rect.y += dy1
            tile2_rect.x += dx2
            tile2_rect.y += dy2

            # Draw everything
            self.draw_grid(screen)
            self.draw_score_level_and_moves(screen)

            # Draw the moving tiles on top
            screen.blit(IMAGESDICT[self.grid[y1][x1]], tile1_rect)
            screen.blit(IMAGESDICT[self.grid[y2][x2]], tile2_rect)

            pygame.display.flip()
            clock.tick(60)

        # Finalize the swap
        self.swap_tiles(tile1_pos, tile2_pos)

    def draw_score_level_and_moves(self, screen):
        """Draw the score, level, and moves remaining"""
        # Background panel
        pygame.draw.rect(screen, GRAY, (0, 0, WIDTH, 50))

        # Format time as MM:SS
        minutes = self.time_remaining // 60
        seconds = self.time_remaining % 60
        time_text = f"{minutes:02d}:{seconds:02d}"

        # Color based on remaining time (red when <10 seconds)
        time_color = RED if self.time_remaining < 10 else BLACK

        # Texts
        score_text = font.render(f"Score: {self.score}/{self.target_score}", True, BLACK)
        level_text = font.render(f"Level: {self.level}", True, BLACK)
        moves_text = font.render(f"Moves: {self.moves_remaining}", True, BLACK)
        timer_text = font.render(time_text, True, time_color)

        # Positions
        screen.blit(score_text, (10, 10))
        screen.blit(level_text, (WIDTH - 250, 10))
        screen.blit(moves_text, (WIDTH // 2 - 100, 10))
        screen.blit(timer_text, (WIDTH - 100, 10))  # Bottom right of panel

    def check_level_completed(self):
        if self.score >= self.target_score:
            time_taken = (pygame.time.get_ticks() - self.level_start_time) / 1000

            self.ai.record_performance(
                level=self.level,
                moves_left=self.moves_remaining,
                score=self.score,
                time_taken=time_taken
            )

            # Get both move limit and time limit from AI
            self.move_limit, self.level_time_limit = self.ai.calculate_difficulty()

            # Prepare for next level
            self.level += 1
            self.score = 0
            self.moves_remaining = self.move_limit
            self.time_remaining = self.level_time_limit
            self.reset_grid()
            self.level_start_time = pygame.time.get_ticks()

            self.display_level_complete(screen)
            return True
        return False

    def display_level_transition(self):
        """Show level transition message"""
        screen.fill(BLACK)
        level_text = large_font.render(f"LEVEL {self.level} START!", True, WHITE)
        screen.blit(level_text, (WIDTH // 2 - level_text.get_width() // 2, HEIGHT // 2))
        pygame.display.flip()
        pygame.time.delay(1500)  # Show for 1.5 seconds

    def adjust_difficulty(self):
        """Adjust game difficulty based on player performance"""
        if not self.player_performance:
            return

        avg_moves = sum(self.player_performance) / len(self.player_performance)

        if avg_moves > self.move_limit * 0.7:
            # Player is doing well - make harder
            self.move_limit = max(10, self.move_limit - 2)
        elif avg_moves < self.move_limit * 0.3:
            # Player is struggling - make easier
            self.move_limit = min(30, self.move_limit + 2)

    def reset_grid(self):
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                self.grid[y][x] = random.choice(CANDY_TILES)
        self.ensure_no_matches_at_start()
        self.place_blockers_for_level()

    def display_game_over(self, screen):
        """Display game over screen with guaranteed visibility"""
        self.game_over = True

        # 1. Create a solid dark background
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.fill((0, 0, 0))  # Solid black background
        screen.blit(overlay, (0, 0))

        # 2. Create text with fallback fonts
        try:
            # Try using Arial first
            large_font = pygame.font.SysFont('Arial', 72, bold=True)
            font = pygame.font.SysFont('Arial', 36)
        except:
            # Fallback to default fonts
            large_font = pygame.font.Font(None, 72)
            font = pygame.font.Font(None, 36)

        # 3. Render bright red text (guaranteed visibility)
        game_over_text = large_font.render("GAME OVER", True, (255, 0, 0))
        restart_text = font.render("Press R to restart - Q to quit", True, (255, 255, 255))

        # 4. Center the text with more spacing
        screen.blit(game_over_text,
                    (WIDTH // 2 - game_over_text.get_width() // 2,
                     HEIGHT // 2 - 50))
        screen.blit(restart_text,
                    (WIDTH // 2 - restart_text.get_width() // 2,
                     HEIGHT // 2 + 50))

        pygame.display.flip()

        # 5. High score update logic
        try:
            if player_data and self.total_score > player_data['highscore']:
                player_data['highscore'] = self.total_score
                save_player_data(player_data['name'], self.total_score)
        except Exception as e:
            print(f"Error saving high score: {e}")

    def display_level_complete(self, screen):
        """Display and wait on level complete screen"""
        # 1. Create a solid overlay (more reliable than SRCALPHA for some systems)
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(180)  # Semi-transparent
        screen.blit(overlay, (0, 0))

        # 2. Render text with fallback fonts
        try:
            # Try to use Arial if available
            title_font = pygame.font.SysFont('Arial', 72, bold=True)
            prompt_font = pygame.font.SysFont('Arial', 36)
        except:
            # Fallback to default fonts
            title_font = large_font
            prompt_font = font

        # 3. Create text with outline for better visibility
        # Main text (white with red outline)
        title_text = title_font.render(f"LEVEL {self.level - 1} COMPLETE!", True, WHITE)
        title_outline = title_font.render(f"LEVEL {self.level - 1} COMPLETE!", True, RED)

        # Prompt text (yellow with dark outline)
        prompt_text = prompt_font.render("Press any key to continue", True, (255, 255, 0))
        prompt_outline = prompt_font.render("Press any key to continue", True, (50, 50, 50))

        # 4. Draw text with outline effect
        title_pos = (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 2 - 80)
        prompt_pos = (WIDTH // 2 - prompt_text.get_width() // 2, HEIGHT // 2 + 20)

        # Draw outlines (offset by 1 pixel)
        screen.blit(title_outline, (title_pos[0] + 1, title_pos[1] + 1))
        screen.blit(prompt_outline, (prompt_pos[0] + 1, prompt_pos[1] + 1))
        # Draw main text
        screen.blit(title_text, title_pos)
        screen.blit(prompt_text, prompt_pos)

        # 5. Add decorative elements
        pygame.draw.rect(screen, (255, 215, 0),  # Gold border
                         (WIDTH // 2 - 200, HEIGHT // 2 - 120, 400, 200), 3)

        pygame.display.flip()

        # 7. Wait for key press
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return False
                elif event.type == pygame.KEYDOWN:
                    waiting = False
            clock.tick(30)

        return True


# Clock
clock = pygame.time.Clock()

# Initialize game state
game_state = GameState()

# Main game loop
running = True
last_level_transition = 0
while running:
    current_time = pygame.time.get_ticks()
    elapsed_seconds = (current_time - game_state.level_start_time) // 1000
    game_state.time_remaining = max(0, game_state.level_time_limit - elapsed_seconds)

    # Game over if time runs out
    if game_state.time_remaining <= 0 and not game_state.game_over:
        game_state.game_over = True
        game_state.display_game_over(screen)

    current_time = pygame.time.get_ticks()
    screen.fill(WHITE)

    # Event handling - MOVED TO TOP
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

            # Skip input during transitions
        if current_time - last_level_transition < LEVEL_TRANSITION_DELAY:
            continue

        # Handle input both during game and game over
        if event.type == pygame.KEYDOWN:
            if game_state.game_over:
                if event.key == pygame.K_r:
                    # Restart game
                    game_state = GameState()
                elif event.key == pygame.K_q:
                    running = False

        elif (event.type == pygame.MOUSEBUTTONDOWN
              and not game_state.animating
              and not game_state.game_over):
            x, y = event.pos
            grid_x, grid_y = x // TILE_SIZE, (y - 50) // TILE_SIZE

            if 0 <= grid_x < GRID_SIZE and 0 <= grid_y < GRID_SIZE:
                if game_state.selected_tile is None:
                    game_state.selected_tile = (grid_x, grid_y)
                else:
                    if game_state.grid[grid_y][grid_x] == 'blocker' or (
                            game_state.selected_tile and
                            game_state.grid[game_state.selected_tile[1]][game_state.selected_tile[0]] == 'blocker'):
                        game_state.selected_tile = None  # Deselect on invalid click
                        continue  # Skip the swap

                    if game_state.is_adjacent(game_state.selected_tile, (grid_x, grid_y)):
                        game_state.handle_swap(
                            game_state.selected_tile,
                            (grid_x, grid_y),
                            screen
                        )
                    else:
                        game_state.selected_tile = (grid_x, grid_y)

    # Draw everything
    game_state.draw_grid(screen)
    game_state.draw_score_level_and_moves(screen)

    # Check level completion (NEW)
    game_state.check_level_completed()

    # Game over check (existing)
    if game_state.moves_remaining <= 0 and not game_state.game_over:
        game_state.game_over = True
        game_state.display_game_over(screen)
    elif game_state.game_over:
        game_state.display_game_over(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
