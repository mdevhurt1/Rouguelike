import curses
import random
import heapq

class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.char = 'E'
        self.move_counter = 0
        self.state = 'wander'  # Can be 'chase', 'search', or 'wander'
        self.last_known_position = None
    
    def is_valid_move(self, x, y, walls, width, height):
        return (x, y) not in walls and 0 < x < width - 1 and 0 < y < height - 1
    
    def has_line_of_sight(self, player_x, player_y, walls):
        """ Check if there is a clear line of sight between the enemy and the player within 20 spaces """
        dx = player_x - self.x
        dy = player_y - self.y
        steps = max(abs(dx), abs(dy))
        
        if steps == 0 or steps > 20:
            return False
        
        step_x = dx / steps
        step_y = dy / steps
        
        for i in range(1, steps + 1):
            check_x = round(self.x + step_x * i)
            check_y = round(self.y + step_y * i)
            if (check_x, check_y) in walls:
                return False
        
        return True
    
    def find_path(self, target_x, target_y, walls, width, height):
        """ Implements A* pathfinding algorithm """
        open_set = [(0, self.x, self.y)]
        came_from = {}
        g_score = {(self.x, self.y): 0}
        f_score = {(self.x, self.y): abs(self.x - target_x) + abs(self.y - target_y)}
        
        while open_set:
            _, current_x, current_y = heapq.heappop(open_set)
            
            if (current_x, current_y) == (target_x, target_y):
                path = []
                while (current_x, current_y) in came_from:
                    path.append((current_x, current_y))
                    current_x, current_y = came_from[(current_x, current_y)]
                return path[::-1]
            
            for dx, dy in [(1,0), (-1,0), (0,1), (0,-1)]:
                neighbor = (current_x + dx, current_y + dy)
                if self.is_valid_move(neighbor[0], neighbor[1], walls, width, height):
                    tentative_g_score = g_score[(current_x, current_y)] + 1
                    if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                        came_from[neighbor] = (current_x, current_y)
                        g_score[neighbor] = tentative_g_score
                        f_score[neighbor] = tentative_g_score + abs(neighbor[0] - target_x) + abs(neighbor[1] - target_y)
                        heapq.heappush(open_set, (f_score[neighbor], neighbor[0], neighbor[1]))
        return []
    
    def move(self, player_x, player_y, walls, width, height):
        if self.has_line_of_sight(player_x, player_y, walls):
            self.state = 'chase'
            self.last_known_position = (player_x, player_y)
        elif self.state == 'chase' and self.last_known_position:
            self.state = 'search'
        elif self.state == 'search' and (self.x, self.y) == self.last_known_position:
            self.state = 'wander'
            self.last_known_position = None
        
        if self.state == 'chase':
            if self.move_counter % 2 == 0:
                path = self.find_path(player_x, player_y, walls, width, height)
                if path:
                    self.x, self.y = path[0]
        elif self.state == 'search' and self.last_known_position:
            if self.move_counter % 2 == 0:
                path = self.find_path(*self.last_known_position, walls, width, height)
                if path:
                    self.x, self.y = path[0]
        else:
            if self.move_counter % 2 == 0:
                random_move = random.choice([(1,0), (-1,0), (0,1), (0,-1)])
                new_x, new_y = self.x + random_move[0], self.y + random_move[1]
                if self.is_valid_move(new_x, new_y, walls, width, height):
                    self.x, self.y = new_x, new_y
        
        self.move_counter += 1
    
    def teleport(self, walls, width, height):
        while True:
            x, y = random.randint(1, width-2), random.randint(1, height-2)
            if self.is_valid_move(x, y, walls, width, height):
                self.x, self.y = x, y
                break

def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(1)
    stdscr.timeout(100)
    
    height, width = stdscr.getmaxyx()
    player = {'x': width // 2, 'y': height // 2, 'char': '@', 'hp': 10}
    enemy = Enemy(random.randint(1, width-2), random.randint(1, height-2))
    walls = [(random.randint(1, width-2), random.randint(1, height-2)) for _ in range(30)]
    
    while True:
        stdscr.clear()
        stdscr.addch(player['y'], player['x'], player['char'])
        stdscr.addch(enemy.y, enemy.x, enemy.char)
        for wall in walls:
            stdscr.addch(wall[1], wall[0], '#')
        
        stdscr.addstr(0, 2, f"HP: {player['hp']}")
        
        key = stdscr.getch()
        if key == ord('q'):
            break
        
        new_x, new_y = player['x'], player['y']
        if key == curses.KEY_UP:
            new_y -= 1
        elif key == curses.KEY_DOWN:
            new_y += 1
        elif key == curses.KEY_LEFT:
            new_x -= 1
        elif key == curses.KEY_RIGHT:
            new_x += 1
        
        if enemy.is_valid_move(new_x, new_y, walls, width, height):
            player['x'], player['y'] = new_x, new_y
        
        enemy.move(player['x'], player['y'], walls, width, height)
        
        if player['x'] == enemy.x and player['y'] == enemy.y:
            player['hp'] -= 1
            if player['hp'] <= 0:
                stdscr.addstr(height//2, width//2 - 5, "YOU DIED!")
                stdscr.refresh()
                curses.napms(2000)
                break
            enemy.teleport(walls, width, height)
        
        stdscr.refresh()
    
if __name__ == "__main__":
    curses.wrapper(main)
