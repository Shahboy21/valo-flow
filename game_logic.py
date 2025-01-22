'''Contains actions possible to be taken by the players and the game logic needed to play coup.'''

from game_objects import Card, Deck, Player, Actions

REQUIRES_TARGET: list[Actions] = [Actions.ASSASSINATE, Actions.COUP, Actions.STEAL]
UNCHALLANGED_ACTIONS: list[Actions] = [Actions.INCOME, Actions.FOREIGN_AID, Actions.COUP]
BLOCKABLE_ACTIONS: list[Actions] = [Actions.FOREIGN_AID, Actions.ASSASSINATE, Actions.STEAL]

CLAIM_MAP: dict[Actions:list[Card]] = {
    Actions.TAX: [Card.DUKE],
    Actions.STEAL: [Card.CAPTAIN],
    Actions.EXCHANGE: [Card.AMBASSADOR],
    Actions.ASSASSINATE: [Card.ASSASSIN],
    Actions.DENY_ASSASSINATION: [Card.CONTESSA],
    Actions.DENY_THEFT: [Card.CAPTAIN,Card.AMBASSADOR], 
    Actions.DENY_AID: [Card.DUKE]
}

BLOCKED_ACTION_MAP: dict[Actions,Actions] = {
    Actions.FOREIGN_AID: Actions.DENY_AID,
    Actions.ASSASSINATE: Actions.DENY_ASSASSINATION,
    Actions.STEAL: Actions.DENY_THEFT
}

def start_game(num_players = 3):
    assert 3 <= num_players <= 6, "Game supports 3-6 players currently."
    #Special mode needed for 2 players, expansion required for more players by default
    
    game_deck = Deck()
    game_deck.shuffle_cards()
    all_players: list[Player] = []
    turn_queue: list[Player] = []
    
    # FIXME: Currently this doesn't follow standard card dealing order 
    num_alive = num_players
    for i in range(num_players):
        all_players.append(Player(id = str(i+1), first_role=game_deck.draw(), second_role=game_deck.draw()))
        turn_queue = all_players.copy() 
        
    #Main game loop
    while num_alive > 1:
        main_player:Player = turn_queue.pop(0)

        if not main_player.alive: continue
        challengers: list[Player] = [p for p in turn_queue if p.alive]
        if main_player.alive:
            
            #Start turn 
            #TODO: Add a seperate broadcast message function. These represent messages that everyone can see during gameplay if choices were hidden.
            print(f"It is Player {main_player.id}'s turn! They have {main_player.bal} coins.") # BROADCAST
            
            #Pick Action
            action_str = f"What would you like to do from the following list:\n"
            action_map: dict[int,Actions] = dict(enumerate(main_player.get_available_actions()))
            for key,action in action_map:
                action_str += f"{key}) {action.value}\n"
                desired_action = validate_response(action_str, list(action_map.keys()))
            
            action:Actions = action_map(desired_action)
            
            #Determine target if needed
            targetted_action:bool = action in REQUIRES_TARGET                           
            if targetted_action:
                valid_targets: dict[int, Player] = dict(enumerate(challengers))
                target_str = "Which player would you like to target from: \n"
                for target_index,target in valid_targets:
                    target_str += f"{target_index}) Player {target.id}\n"
                target_player_index:int = validate_response(target_str, list(valid_targets.keys()))
                target = valid_targets[target_player_index]
            
            # Announce Action 
            announcement = f"Player {main_player.id} will {action.value} "
            if targetted_action: announcement += f" from Player {target.id}!"
            print(announcement) # BROADCAST
                     
            end_turn = False
            # Check for challenges
            if action not in UNCHALLANGED_ACTIONS:
                claimed_role: Card = CLAIM_MAP[action][0] 
                for p in challengers:
                    choice = validate_response(f'Player {p.id} would you like to challenge (Y/N)?', ['Y','N'])
                    if choice.capitalize == 'Y':
                        end_turn = challenge_last_action(main_player, p, claimed_role) # On challenge if main_player does not have the proper role, the turn ends.                         
                        break # After the first challenge no more challenges need to be checked
            
            # Check for blocks if needed
            blocked, successfully_blocked = False, False
            if action in BLOCKABLE_ACTIONS and (not end_turn):
                for p in challengers: #FIXME: Clean up action blocking to make more clear which role is being claimed before asking for input
                    choice = validate_response(f'Player {p.id} would you like to block the action (Y/N)?',['Y','N']) 
                    if choice.capitalize == 'Y':
                        blocked = True
                        blocking_action = BLOCKED_ACTION_MAP[action]
                        claimed_role = CLAIM_MAP(blocking_action)[0] 
                        if blocking_action == Actions.DENY_THEFT:
                            claim_choice = validate_response("To block stealing do you claim: 0) Captain or 1) Ambassador?", ['0','1'])
                            claimed_role = CLAIM_MAP[blocking_action][claim_choice] 
                        elif blocking_action == Actions.DENY_AID:
                            claimed_role = CLAIM_MAP[blocking_action][0]
                        elif blocking_action == Actions.ASSASSINATE:
                            claimed_role = CLAIM_MAP[blocking_action][0]
                        else:
                            pass #TODO: Implemeent INVALID GAME STATE
                            
                        
                        # Check for block counter challenges
                        counter_players: list[Player] = [main_player] + [c for c in challengers if c != p]
                        for counter_p in counter_players:
                            counter = validate_response(f'Player {counter_p.id}, player {p.id} is claiming they are a {claimed_role}! would you like to challenge the block (Y/N)?', ['Y','N'])
                            
                            if counter.capitalize =='Y':
                                #TODO: Complete CHALLENGE function
                                successfully_blocked = not challenge_last_action(p, counter_p,claimed_role)
                                if not successfully_blocked: blocked = False
                                break  # After the first challenge no more challenges need to be checked
                        
                        if successfully_blocked:
                            break # No need to go check if other players want to block
                        
            if not blocked and not successfully_blocked:
                #Resolve Action
                pass #TODO: Call appropriate function based on action
            
            turn_queue.append(main_player)
            
    
    #Create deck
    #Create Players
    #Start turn 1
    # Declare Action
    # Check for Challenges and Resolve
    # If no challenges or Proven Valid correct
    # Check for Blocks
    # Check for Blocker Challenges and Resolve
    # If no blockers or valid blocker Resolve action
    
    #Next Turn
    #Check if player is alive, remove from queues if dead
    
    pass

def validate_response(msg:str, valid_responses: list[str]) -> str:
    """ Takes an input message and continues taking inputs until a response from valid_responses is given."""
    str_valid_responses = [str(resp) for resp in valid_responses]
    output:str = input(msg.strip()+'\n')
    while output not in str_valid_responses:
        print(f'Please enter a valid response from one of: {str_valid_responses}...')
        output = input(msg.strip()+'\n')
    return output
  
    
def print_board_status(): #TODO: Finish me
    pass

def lose_influence(target:Player) -> None:
    if not target.alive:
        print(f'Player {target} is already dead... was this an error?')
        return None
    elif len(target.active_roles) == 1:
        lost_role_num = 0
    else:
        message = f'Player {target.id} which of your cards will you give up?\n' 
        for num, role in enumerate(target.active_roles):
            message += f'{num}) {role}'
        lost_role_num = validate_response(message, valid_responses=list(range(len(target.active_roles))))
    lost_role = target.reveal_role(lost_role_num)
    print(f'Player {target.id } was a {lost_role}!')
    if not target.alive:
        print(f'Unfortunately, that was Player {target.id}\'s last role and they are now out of the game!')
    
    
def launch_coup(origin:Player, target: Player) -> None:
    """ The origin player causes the target player to lose influence after paying 7 coins.
    Target player gets to chose which card they lose if they have more than one role.
    
    origin: Player launching the coup and paying 7 coins
    target: Player deciding which role to lose.
    """
    origin.increment_bal(-7)
    lose_influence(target)


def take_income(origin:Player):
    """ Origin player gains one coin."""
    origin.increment_bal(increment=1)


def take_foreign_aid(origin:Player):
    """ Origin player gains two coins.
    This action is BLOCKABLE by someone claiming DUKE.
    """
    origin.increment_bal(increment=2)


#Claiming Duke
def take_tax(origin:Player) -> None:
    """ Origin player gains three coins.
    This can only be done if the origin player is claiming they are a DUKE.
    """
    origin.increment_bal(increment=3)


#Claiming Captain
def steal(origin:Player, target:Player):
    """ Origin player takes two coins from the target player.
    This can only be done if the origin player is claiming they are a CAPTAIN.
    This action is BLOCKABLE by someone claiming CAPTAIN or AMBASSADOR.
    """
    if target.bal >= 2:
        origin.increment_bal(2)
        target.increment_bal(-2)
    else:
        origin.increment_bal(target.bal)
        target.increment_bal(-1*target.bal)


#Claiming Assassin
def assassinate(origin:Player, target:Player):
    """ Origin player pays 3 coins to cause target player to lose influence.
    This can only be done if the origin player is claiming they are an ASSASSIN.
    This action is BLOCKABLE by someone claiming CONTESSA.
    """
    try: origin.increment_bal(-3)
    except ValueError as e:
        raise ValueError(f"Player {origin} cannot afford to assissinate. Illegal game action taken.") from e
    lose_influence(target)


#Claim Ambassador
def exchange_roles(origin:Player, game_deck:Deck):
    """ Origin player draws two roles from the deck and returns any two that they have to the deck. The deck is then shuffled.
    This action can only be done if the origin player is claiming they are an AMBASSADOR.
    
    Revealed roles cannot be exchanged (except when revealed to confirm a challenge). 
    """
    origin.active_roles.append(game_deck.draw())
    origin.active_roles.append(game_deck.draw())
    for i in [0,1]:
        message = add_enumerated_options(f'Player {origin} which role would you like to return?', origin.active_roles)
        selected_role_num = validate_response(message, list(range(len(origin.active_roles))))
        game_deck.return_card(origin.remove_role(int(selected_role_num)))
    game_deck.shuffle_cards()


def challenge_role_loser(defendant:Player, prosecutor:Player, role:Card) -> Player:
    """ Returns the losing player of the challenge based on if the defendant has the input role. 
    If the defendant has the input role, the prosecutor is the losing player. 
    If not, the defendant is the losing player.
    """
    pos = defendant.find_claim(role) #TODO: FINISH Functionality
    if pos > -1: return prosecutor
    else: return defendant

    
def add_enumerated_options(message:str, options:list[str]) -> str:
    """ Given an input message, adds all items in a user friendly selection format and returns the resulting string.
    Format is as follows:
    index) Item
    index2) Item 2
    etc...
    """
    output = message.rstrip() + '\n'
    for index, item in enumerate(options):
        output += f'{index}) {item}\n'
    return output

