(lambda c, t, r:  # Same as importing curses, time, random
	(lambda sc, dirs, **opt:  # c.initscreen(),  some dict, delay & starting_length
		(  # This is a "tuple * 0": This will execute (= evaluate) all instructions one after the other
			sc.nodelay(1), # Allows program to run even if there are no inputs from the player
			c.cbreak(),  # Allows curses to react instantly without requiring to hit Enter
			sc.keypad(1),  # Tells curses to return pre-parsed special codes for navigation keys
			sc.addstr(0,0, str(opt['delay'])),  # Useless as the screen is not refresh and 0,0 is overwritten
			(lambda x, y, snake, dir, lost, points, apple, key, _map:  # x,y = width, height of the screen
				(  # Another tuple *0 
					sc.addstr(0, 0, 'One-line Snake by JeromeJ (\'q\' to quit, \'+-\' to change speed)\n{}'.format('-'*x)),
					sc.addstr(0, x-12, 'POINTS: {}'.format(points[0])),
					
					# Draws the snake
					[sc.addstr(y, x, '+') for y, x in snake[:-1]] and None,  # Not sure what's the "and None" is for...
					[sc.addstr(y, x, '>') for y, x in (snake[-1],)] and None,  # Same here
					
					sc.refresh(),  # Text is only updated on screen when this is called
					
					(lambda spawn_apple:  # Spawn apple is the function to be called to spawn an apple
						# "or" can be used to chain calls if you know that the left side will evaluate to false-like.
						# Here, .append will return None which evaluate to False
						apple.append(spawn_apple()) or
						apple.pop(0) and  # In order to replace a variable value, we append then pop the list which is a ref
						list(
							iter(  # This creates an infinite loop, which breaks when "q" is hit
								lambda:
								(lambda key:
									(
										key,
										c.flushinp(),  # Clears the buffer
										
										not lost and  # Main loop will run until lost is evaluated as False
										(
											# (1) Tick + Speed control
											t.sleep(opt['delay'][0]) or  # This is the clock speed
											
											# The "and" here acts as a skip if the condtion is not met.
											key == 465 and  # 465 is "+" on the keypad.
											(
												opt['delay'].append(opt['delay'][0]/2) or 
												opt['delay'].pop(0)
											) or 
											
											key == 464 and   # 464 is the "-" on the keypad
											opt['delay'][0] < .3 and   # Restrict min delay to .3
											(
												opt['delay'].append(opt['delay'][0]*2) or 
												opt['delay'].pop(0)
											),
										
											# (2) Display info
											sc.addstr(y-1, 0, ' KEY: '+str(key)+'  ') or  # Display current key
											sc.addstr(y-1, int(x/2-10), ' SPEED: '+str(int(10/opt['delay'][0]))+'  ') or 
											sc.addstr(y-1, x-15, 'DIRECTION: '+str(dir[0].s)),
										
											# (3) Change dir:
											key in set(dirs) - {dir[0].opp} and  # If input is a valid direction
											(dir.append(dirs[key]) or dir.pop(0)),  # Replace current dir with new one
										
											# (4) Snake movement:
											snake.append(  # (4a) Grow snake in direction
												next(
													(
														new_head,  # The head being added
														
														# Checking if we lost
														(  
															new_head in snake or 
															not(1 < new_head[0] < y-1) or 
															not(0 < new_head[1] < x-1)
														) and 
														(
															sc.addstr(int(y/2), int(x/2-10), '[YOU LOST]') or 
															sc.refresh() or 
															lost.append(True)
														)
													)[0] for new_head in  # New head will be the one matching current dir's "v"
													[
														(snake[-1][0], snake[-1][1]+1) * (dir[0].v == c.KEY_RIGHT) +
														(snake[-1][0], snake[-1][1]-1) * (dir[0].v == c.KEY_LEFT) + 
														(snake[-1][0]-1, snake[-1][1]) * (dir[0].v == c.KEY_UP) + 
														(snake[-1][0]+1, snake[-1][1]) * (dir[0].v == c.KEY_DOWN)
													]
												)) or 
												
												# Did we eat an apple?
												(
													snake[-1] == apple[0] and
													(
														# Points are based on speed
														points.append(10/opt['delay'][0]/10) or 
														points.pop(0) or 
														
														sc.addstr(0, x-12, 'POINTS: {}'.format(int(points[0]))) or 
														
														# Replace apple with new one: Sometimes buggy
														apple.append(spawn_apple()) or 
														apple.pop(0)
													)
												) or 
												
												# If not, cut off tail
												(
													snake[-1] != apple[0] and 
													sc.addstr(*(snake.pop(0)+(' ',)))  # Replaces tail with " "
												) or 
												
												sc.addstr(*(snake[-2]+('+',))) or   # Draws the whole tail
												
												sc.addstr(*(snake[-1]+(dir[0].s,)))  # Draws the head pointing in the right direction
												
												# We do not need to refresh bc getch will do it automatically
										)*0
									)[0]  # Returns the key to be evaluated by iter to know if we should stop the game or not
								)(sc.getch(),),  # Reads the input - Variable "key"
								ord('q')  # Will stop the iteration when 'q' is hit
							)
						)
					)(lambda: 
						next(
							(apple, sc.addstr(apple[0], apple[1], '*')) for apple in  # Draws the apple
							[r.sample(_map - set(snake), 1)[0]]  # Pick a random position NOT on the snake
						)[0]
					)
				)*0
			)(*next(
				(
					x,
					y,
					[(int((y-2)/2), x) for x in range(5, 5+opt['starting_length'])],  # Variable "snake"
					[dirs[c.KEY_RIGHT]],  # Variable "dir": Starting direction
					[],  # Variable lost
					[0],  # Variable "points"
					[(0,0)],  # Variable "apple"
					-1,  # Variable "key"
					set((_y, _x) for _y in range(2, y-1) for _x in range(x)),  # Variable "_map" : All valid positions on screen
				) for y,x in (sc.getmaxyx(),)  # Another way to have temporary variables instead of using lambda
			)),
			sc.refresh(),
			c.endwin()
		)*0
	)(
		c.initscr(),  # Creates screen obj and assign it to "sc"
		dict(zip(  # Maps each key to a "Dir" class which has three prop: v, s and opp
			(c.KEY_UP, c.KEY_DOWN, c.KEY_RIGHT, c.KEY_LEFT),
			map(
				lambda el:__import__('collections').namedtuple('Dir', 'v s opp')(*el),
				(
					(c.KEY_UP, '^', c.KEY_DOWN),
					(c.KEY_DOWN, 'v', c.KEY_UP),
					(c.KEY_RIGHT, '>', c.KEY_LEFT),
					(c.KEY_LEFT, '<', c.KEY_RIGHT),
				)
			)
		)),
		delay=[.15],
		starting_length=6
	)
)(*map(__import__, ('curses', 'time', 'random')))
