import pygame
import time
import random
from collections import Counter

pygame.init()
screen = pygame.display.set_mode((480, 480), pygame.RESIZABLE)
clock = pygame.time.Clock()
dt = clock.tick(60) / 1000

DEPTH = 1
MENU_SELECT = 0   
FIRST_PLAYER = 0
state = FIRST_PLAYER
COLUMN = 7
LINE = 6
PA_RATIO = 0.8 #player area ratio. The bigger the ratio is, the bigger is the play area
COLOR = [pygame.Color(255, 0, 0), pygame.Color(0,0, 255)]
CIRCLE_SIZE = 0.7
CONNECT = 4

class Score:
    ''' We track the amount of way a series of k of the same color, that can be completed to a CONNECT-series '''
    def __init__(self, count = 0):
        self.p1 = [0]*CONNECT
        self.p2 = [0]*CONNECT
        self.count = count
        self.win = None

    def incr(self, t):
        counter = Counter(t)
        if counter[0] and not counter[1]:
            self.p1[counter[0]-1] += 1
        if counter[1] and not counter[0]:
            self.p2[counter[1]-1] += 1
        if counter[0] == CONNECT or counter[1] == CONNECT:
            return True
    def is_finished(self):
        return bool(self.p1[-1]) or bool(self.p2[-1]) or self.count == COLUMN*LINE


    def __lt__(self, other):
        #Bigger score mean player wins more
        if self.p1[-1] != 0 and other.p1[-1] != 0: #Case : both score are a win for player
            return self.count > other.count
        if self.p2[-1] != 0 and other.p2[-1] != 0: #Case : both score are a win for computer
            return self.count < other.count
        return tuple([ self.p1[i]-self.p2[i] for i in range(CONNECT-1, -1, -1)]) < tuple([ other.p1[i]-other.p2[i] for i in range(CONNECT-1, -1, -1)])

class AntiScore:
    ''' We track the amount of way a series of k of the same color, that can be completed to a CONNECT-series '''
    def __init__(self, count = 0):
        self.p1 = [0]*CONNECT
        self.p2 = [0]*CONNECT
        self.count = count
        self.win = None

    def incr(self, t):
        counter = Counter(t)
        if counter[0] and not counter[1]:
            self.p1[counter[0]-1] += 1
        if counter[1] and not counter[0]:
            self.p2[counter[1]-1] += 1
        if counter[0] == CONNECT or counter[1] == CONNECT:
            return True
    def is_finished(self):
        return bool(self.p1[-1]) or bool(self.p2[-1]) or self.count == COLUMN*LINE


    def __lt__(self, other):
        #Bigger score mean player wins more
        if self.p1[-1] != 0 and other.p1[-1] != 0: #Case : both score are a win for player
            return self.count < other.count
        if self.p2[-1] != 0 and other.p2[-1] != 0: #Case : both score are a win for computer
            return self.count > other.count
        return tuple([ self.p1[i]-self.p2[i] for i in range(CONNECT-1, -1, -1)]) > tuple([ other.p1[i]-other.p2[i] for i in range(CONNECT-1, -1, -1)])
    
SCORE_ID = 0
SCORE_LIST = [Score, AntiScore]


def map_position(p):
    ''' Map a point from [0, 1]x[0, 1] to a point on screen in the play area'''
    x,y = p
    w,h = screen.get_width(), screen.get_height()
    s = PA_RATIO*min(w,h)#len of the side of the PA square
    rc, rl = COLUMN/max(COLUMN, LINE), LINE/max(COLUMN, LINE)
    wo = (w - s*rc)//2  #width offset of the bottom left corner
    ho = (h - s*rl)//2  #height offset of the bottom left corner
    x,y = x*s*rc + wo, y*s*rl + ho
    return (x,y)

def draw_grid_layout():
    ''' This function only draw the lines of the grid '''
    for i in range(COLUMN+1):
        p1 = map_position((i/COLUMN, 0))
        p2 = map_position((i/COLUMN, 1))
        pygame.draw.line(screen, "black", p1, p2, 1)
    for i in range(LINE+1):
        p1 = map_position((0,i/LINE))
        p2 = map_position((1,i/LINE))
        pygame.draw.line(screen, "black", p1, p2, 1)



def get_mouse_column():
    ''' Check if the mouse is in the player area
        Check in which column it is if any
        Return bool, int '''
    x0,y0 = map_position((0,0))
    x1,y1 = map_position((1,1))  
    xp, yp = pygame.mouse.get_pos()
    if x0 < xp < x1 and y0 < yp < y1:
        return (True,int((xp-x0)/(x1-x0)*COLUMN))
    else:
        return (False,None)

def highlight_column(player):
    b,n = get_mouse_column()
    if b:
        p = map_position((n/COLUMN, 0))
        l = map_position(((n+1)/COLUMN, 1))
        color = pygame.Color(COLOR[player].r//10+225, COLOR[player].g//10+225, COLOR[player].b//10+225)
        pygame.draw.rect(screen, color, pygame.Rect(p[0], p[1], 1+l[0]-p[0], 1+l[1]-p[1]))#, pygame.BLEND_RGBA_MULT))

def draw_grid_content(grid):
    for col in range(COLUMN):
        for line in range(len(grid[col])):
            o = map_position( ( (col+0.5)/COLUMN, (LINE-line-0.5)/LINE ) )
            r = (o[0] - map_position( (col/COLUMN, 0))[0])*CIRCLE_SIZE
            pygame.draw.circle(screen, COLOR[grid[col][line]], o, r)

def draw_grid_winner(grid):
    score = calculate_score_raw(grid)
    if not score.win is None:
        t1, t2 = score.win
        p1 = map_position( ((t1[0]+0.5)/COLUMN, (LINE-t1[1]-0.5)/LINE))
        p2 = map_position( ((t2[0]+0.5)/COLUMN, (LINE-t2[1]-0.5)/LINE))
        pygame.draw.line(screen, 'Black', p1, p2, 4)

def init_grid():
    return [ [] for _ in range(COLUMN)]

def play_move(grid, col, player):
    if len(grid[col]) < LINE:
        grid[col].append(player)
def unplay_move(grid, col):
    grid[col].pop()

def bottom_text(state):
    size = int(min(screen.get_height(),screen.get_width()) *(1-PA_RATIO)/4)
    font = pygame.font.SysFont('Courier New', size)
    font2 = pygame.font.SysFont('Courier New', 3*size//5)
    if state == 0:
        font_surface = font.render("It's your turn to play", False, (0, 0, 0))
        w, h = font_surface.get_size()
        screen.blit(font_surface, ((screen.get_width()-w)/2 ,screen.get_height() * (1-(1-PA_RATIO)/2)))

    if state == 1:
        font_surface = font.render("BlounardBot is playing ...", False, (0, 0, 0))
        w, h = font_surface.get_size()
        screen.blit(font_surface, ((screen.get_width()-w)/2 ,screen.get_height() * (1-(1-PA_RATIO)/2)))

    if state == 2:
        font_surface = font.render("Congratulation, you won!", False, (0, 0, 0))
        w, h = font_surface.get_size()
        screen.blit(font_surface, ((screen.get_width()-w)/2 ,screen.get_height() * (1-(1-PA_RATIO)/2)))
        
    if state == 3:
        font_surface = font.render("Too bad, you lost!", False, (0, 0, 0))
        w, h = font_surface.get_size()
        screen.blit(font_surface, ((screen.get_width()-w)/2 ,screen.get_height() * (1-(1-PA_RATIO)/2))) 

def get_diff_text(depth):
    match depth:
        case 0 :
            return 'Noob'
        case 1 :
            return 'Easy'
        case 2:
            return 'Medium'
        case 3:
            return 'Hard'
        case 4:
            return 'Harder'
def top_text(state, depth):
    if state < 2:            
        size = int(min(screen.get_height(),screen.get_width()) *(1-PA_RATIO)/5)
        font1 = pygame.font.SysFont('Courier New', size)
        font2 = pygame.font.SysFont('Courier New', (9*size)//10)
        font_surface1 = font1.render("You got challenged by BlounardBot!" , False, (0, 0, 0))
        font_surface2 = font2.render("Win, or your infodisplay will turn french" , False, (0, 0, 0))
        w1, h1 = font_surface1.get_size()
        w2, h2 = font_surface2.get_size()
        screen.blit(font_surface1, ((screen.get_width()-w1)/2 , screen.get_height() * (1-PA_RATIO)/6))
        screen.blit(font_surface2, ((screen.get_width()-w2)/2 , screen.get_height() * (1-PA_RATIO)/2))
    else:
        size = int(min(screen.get_height(),screen.get_width()) *(1-PA_RATIO)/5)
        font1 = pygame.font.SysFont('Courier New', size)
        font_surface1 = font1.render("Press R to retry" , False, (0, 0, 0))
        diftext = get_diff_text(depth)
        font_surface2 = font1.render("Checkout TTK Save GUI aswell" , False, (0, 0, 0))
        w1, h1 = font_surface1.get_size()
        w2, h2 = font_surface2.get_size()
        screen.blit(font_surface1, ((screen.get_width()-w1)/2 , screen.get_height() * (1-PA_RATIO)/6))
        if state ==2:
            screen.blit(font_surface2, ((screen.get_width()-w2)/2 , screen.get_height() * (1-PA_RATIO)/2))

def draw_settings():
    size = int(min(screen.get_height(),screen.get_width()))//20
    font = pygame.font.SysFont('Courier New', size)

    settings_text = font.render("Settings" , False, (0, 0, 0))
    input_text = font.render("Use arrow keys to navigate" , False, (0, 0, 0))
    enter_text = font.render("Press ENTER to save" , False, (0, 0, 0))
    w1, h1 = settings_text.get_size()
    w2, h2 = input_text.get_size()
    w3, h3 = enter_text.get_size()
    fp = "You" if FIRST_PLAYER == 0 else "BlounardBot"
    first_player_text = font.render("Who start : "+fp , False, (int(MENU_SELECT==0)*255, 0, 0))    
    column_text = font.render(f"Amount of columns : {COLUMN}" , False, (int(MENU_SELECT==1)*255, 0, 0))
    line_text = font.render(f"Amount of rows : {LINE}" , False, (int(MENU_SELECT==2)*255, 0, 0))
    connect_text = font.render(f"Connect {CONNECT} in a row to win" , False, (int(MENU_SELECT==3)*255, 0, 0))
    st = "Classic" if SCORE_ID == 0 else "Inting"
    score_text = font.render("BlounardBot behavior : "+st , False, (int(MENU_SELECT==4)*255, 0, 0))
    depth_text = font.render(f"Depth : {DEPTH}" , False, (int(MENU_SELECT==5)*255, 0, 0))

    
    screen.blit(settings_text, ((screen.get_width()-w1)/2 , 0))
    screen.blit(input_text, ((screen.get_width()-w2)/2 , 1*size +screen.get_height()//20))
    screen.blit(first_player_text, ((screen.get_width()//20 , 4*size +screen.get_height()//20)))
    screen.blit(column_text, ((screen.get_width()//20 , 6*size + screen.get_height()//20)))
    screen.blit(line_text, ((screen.get_width()//20 , 8*size +screen.get_height()//20)))
    screen.blit(connect_text, ((screen.get_width()//20 , 10*size +screen.get_height()//20)))
    screen.blit(score_text, ((screen.get_width()//20 ,12*size + screen.get_height()//20)))
    screen.blit(depth_text, ((screen.get_width()//20 ,14*size + screen.get_height()//20)))
    screen.blit(enter_text, ((screen.get_width()-w3)/2 ,screen.get_height()-size*2))
def get_list_available_slot(grid):
    res = []
    for col in range(COLUMN):
        if len(grid[col]) < LINE :
            res.append(col)
    return res

def calculate_score_raw(grid):
    score = SCORE_LIST[SCORE_ID](count = sum( [len(grid[col]) for col in range(COLUMN)] ))
    #columns
    for col in range(COLUMN):
        for line in range(LINE-CONNECT+1):
            t = []
            for c in range(CONNECT):
                if len(grid[col]) > line + c:
                    t.append(grid[col][line+c])
                else:
                    t.append(None)
            if score.incr(t):
                score.win = ( (col, line), (col, line+CONNECT-1))

    #lines
    for col in range(COLUMN-CONNECT+1):
        for line in range(LINE):
            t = []
            for c in range(CONNECT):
                if len(grid[col+c]) > line:
                    t.append(grid[col+c][line])
                else:
                    t.append(None)
            if score.incr(t):
                score.win = ( (col, line), (col+CONNECT-1, line))

    #diag
    for col in range(COLUMN-CONNECT+1):
        for line in range(LINE-CONNECT+1):
            t = []
            for c in range(CONNECT):
                if len(grid[col+c]) > line+c:
                    t.append(grid[col+c][line+c])
                else:
                    t.append(None)
            if score.incr(t):
               score.win = ( (col, line), (col+CONNECT-1, line+CONNECT-1))

    #adiag
    for col in range(COLUMN-CONNECT+1):
        for line in range(CONNECT-1, LINE):
            t = []
            for c in range(CONNECT):
                if len(grid[col+c]) > line-c:
                    t.append(grid[col+c][line-c])
                else:
                    t.append(None)
            if score.incr(t):
                score.win = ( (col, line), (col+CONNECT-1, line-CONNECT+1))   
    return score

def best_computer_raw_move(grid):
    highscore = None
    best_move = None
    for col in get_list_available_slot(grid):
        play_move(grid, col, 1)
        score = calculate_score_raw(grid)
        if highscore is None or score < highscore: #LOW SCORE MEAN BETTER POSITION FOR COMPUTER DON'T FORGET
            highscore = score
            best_move = col
        unplay_move(grid, col)
    if best_move is None:
        raise ValueError("No move left isn't supposed to happen")
    return best_move

def sort_move(grid, player):
    ''' Return a list of (score, column) ordered by score'''
    L = []
    for col in get_list_available_slot(grid):
        play_move(grid, col, player)
        score = calculate_score_raw(grid)
        L.append((score, col))
        unplay_move(grid, col)
    #L.sort(key = lambda x : x[0])
    return L

def alpha_beta_score(grid, depth, alpha, beta, maxPlayer):
    # https://en.wikipedia.org/wiki/Alpha-beta_pruning
    score = calculate_score_raw(grid)
    if depth == 0 or score.is_finished():
        return score
    if maxPlayer:
        highscore = None
        possible_move = sort_move(grid, 0)
        possible_move.reverse()
        for t in possible_move:
            col = t[1]
            play_move(grid, col, 0)
            score = alpha_beta_score(grid, depth-1, alpha, beta, False)
            unplay_move(grid, col)
            if highscore is None or highscore < score:
                highscore = score
            if (not beta is None) and beta < highscore:
                break
            if alpha is None or alpha < highscore:
                alpha = highscore
        return highscore
    else:
        highscore = None
        possible_move = sort_move(grid, 1)
        for t in possible_move:
            col = t[1]
            play_move(grid, col, 1)
            score = alpha_beta_score(grid, depth-1, alpha, beta, True)
            unplay_move(grid, col)
            if highscore is None or score < highscore:
                highscore = score
            if (not alpha is None) and highscore < alpha:
                break
            if beta is None or highscore < beta:
                beta = highscore
        return highscore

def best_move(grid, player, depth):
    highscore = None
    best_move = None
    if player == 1:
        for col in get_list_available_slot(grid):
            play_move(grid, col, 1)
            score = alpha_beta_score(grid, depth, None, None, True)
            if highscore is None or score < highscore: #LOW SCORE MEAN BETTER POSITION FOR COMPUTER DON'T FORGET
                highscore = score
                best_move = col
            unplay_move(grid, col)
        if best_move is None:
            raise ValueError("No move left isn't supposed to happen")
        return best_move
    else:
        for col in get_list_available_slot(grid):
            play_move(grid, col, 0)
            score = alpha_beta_score(grid, depth, None, None, False)
            if highscore is None or highscore < score:
                highscore = score
                best_move = col
            unplay_move(grid, col)
        if best_move is None:
            raise ValueError("No move left isn't supposed to happen")
        return best_move
    
    
GRID = init_grid()
running = True
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if state == 0 and event.type == pygame.MOUSEBUTTONDOWN:   #The player play a move
            b, col = get_mouse_column()
            if b and col in get_list_available_slot(GRID) :
                play_move(GRID, col, 0)
                state = 1
        if state == 0 and event.type == pygame.KEYDOWN and event.key == pygame.K_a:   
            state = 3
        if state > 1 and event.type == pygame.KEYDOWN and (event.key == pygame.K_r or event.key == pygame.K_RETURN):  #Game is over, you can retry, or change difficulty
            state = FIRST_PLAYER
            GRID = init_grid()
        if state in [2,3] and event.type == pygame.KEYDOWN and event.key == pygame.K_s:
            state = 4
            MENU_SELECT = 0
        if state == 4 and event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
            match MENU_SELECT:
                case 0:
                    FIRST_PLAYER = 1-FIRST_PLAYER
                case 1:
                    COLUMN += 1
                case 2:
                    LINE += 1
                case 3:
                    CONNECT += 1
                case 4:
                    SCORE_ID = (SCORE_ID+1)%len(SCORE_LIST)
                case 5:
                    DEPTH = min(5, DEPTH+1)
        if state == 4 and event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
            match MENU_SELECT:
                case 0:
                    FIRST_PLAYER = 1-FIRST_PLAYER
                case 1:
                    COLUMN = max(1, COLUMN-1)
                case 2:
                    LINE = max(1, LINE-1)
                case 3:
                    CONNECT = max(1, CONNECT-1)
                case 4:
                    SCORE_ID = (SCORE_ID-1)%len(SCORE_LIST)
                case 5:
                    DEPTH = max(0, DEPTH-1)
        if state == 4 and event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
            MENU_SELECT -= 1
            MENU_SELECT = MENU_SELECT%6
        if state == 4 and event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
            MENU_SELECT += 1
            MENU_SELECT = MENU_SELECT%6
            
    if state in [0,1]:
        score = calculate_score_raw(GRID)
        if score.is_finished():
            state = 2
            print('you won')
            print( 'w', end='')
    screen.fill("white")

    if state == 0:
        highlight_column(0)

    if state<4:
        draw_grid_layout()

        draw_grid_content(GRID)

        bottom_text(state)
        top_text(state, DEPTH)

    if state in [2,3]:
        draw_grid_winner(GRID)

    if state == 4:
        draw_settings()

    pygame.display.flip()

    if state == 1:
        t = time.time()
        l = get_list_available_slot(GRID)
        if l :
            col = best_move(GRID, 1, DEPTH)
            play_move(GRID, col, 1)
            state = 0
        #print(time.time() - t)
        time.sleep(1)

    if state in [0,1]:
        score = calculate_score_raw(GRID)
        if score.is_finished():
            state = 3    

    dt = clock.tick(60) / 1000

    
pygame.quit()
