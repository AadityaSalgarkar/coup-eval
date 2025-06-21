import core.action as action
from core.player import Player
from core.game   import GameState

import random
import os

# Freemode allows the game to allow for any cards to be played
FreeMode = True
FreeMode = False

defaultNames = ["Leonardo", "Michelangelo", "Raphael", "Donatello", "Splinter", "April"]

Players = []
PlayersAlive = []
CurrentPlayer = 0

AvailableActions = []

CONSOLE = True

def print_red(message) :
    print("\033[91m%s\033[0m" % (message))

def get_input(message, name = "") :
    return display(message= message, name= name,input_needed= True)

def display(message, name = "", input_needed = False) : 
    if CONSOLE:
        if name != "" :
            print_red("This message is shown only to %s: %s" % (name, message))
        else :
            print(message)
        if input_needed:
            return input().strip()
    else :
        assert False, "CONSOLE is not supported in non-console mode"
    


class ConsolePlayer(Player):
    ShowBlockOptions = True         # global variable to showpossible options for blocking. set to True every turn

    def confirmCall(self, activePlayer, action): 
        """ return True if player confirms call for bluff on active player's action. returns False if player allows action. """
        if len(PlayersAlive) > 2:
            longestName = [len(player.name) for player in PlayersAlive]
            longestName = max(longestName)            
            name = self.name + "," + (" " * (longestName - len(self.name)))
        else:
            name = self.name + ","
        
        choice = get_input("%s do you think %s's %s is a bluff?\n Do you want to call (Y/N)? " % (name, activePlayer.name, action.name))
        choice = choice.upper()
        
        if not choice.strip() in ('Y', 'N', ''):
            display("\n Type Y to call bluff. \n Type N to allow %s's %s.\n" % (activePlayer.name, action.name))
            return self.confirmCall(activePlayer, action)
            
        if choice == 'Y':
            return True
               
        return False 
            
    def confirmBlock(self, activePlayer, opponentAction):
        """ returns action used by player to blocks action. return None if player allows action. """
        cardBlockers = []
        
        for card in GameState.CardsAvailable:
            if opponentAction.name in card.blocks:
                cardBlockers.append(card)

        totalBlockers = len(cardBlockers) + 1
        
        if ConsolePlayer.ShowBlockOptions:
            ConsolePlayer.ShowBlockOptions = False            
            
            display("\n%s's %s can be blocked with the following cards:" % (activePlayer.name, opponentAction.name))
            for i, card in enumerate(cardBlockers):
                display(" %i: %s" % (i + 1, card.name))
            display(" %i: (Do not block)\n" % (totalBlockers))            
        
        if len(PlayersAlive) > 2:
            longestName = [len(player.name) for player in PlayersAlive]
            longestName = max(longestName)
            name = self.name + "," + (" " * (longestName - len(self.name)))
        else:
            name = self.name + ","
        
        choice = get_input("%s do you wish to block %s (1-%i)? " % (name, opponentAction.name, totalBlockers))
        choice = choice.strip()
        if choice == "":
            choice = str(totalBlockers)      # do not block
        
        if not choice.isnumeric():
            assert False, "Choice is not numeric"
            # display(" Select a number between 1-%i. Press enter to allow %s's %s." % (totalBlockers, activePlayer.name, opponentAction.name))
            # return self.confirmBlock(activePlayer, opponentAction)
        choice = int(choice) - 1
        
        if choice == len(cardBlockers):
            return None         # player decides not to block
        
        if not (choice >= 0 and choice < len(cardBlockers)):
            display(" Select a number between 1-%i. Press enter to allow %s's %s." % (totalBlockers, activePlayer.name, opponentAction.name))
            return self.confirmBlock(activePlayer, opponentAction)
            
        block = cardBlockers[choice - 1]
        
        display("\n\n%s is blocking with %s" % (self.name, block.name))
        return block
        
    def selectInfluenceToDie(self):
        """ select an influence to die. returns the value from the influence list. """
        display("\n%s has lost an influence!" % (self.name))
        
        if len(self.influence) == 1:
            display("%s will lose their last card, %s" % (self.name, self.influence[0].name))
            return self.influence[0]
        
        display("%s, select influence to lose:" % (self.name), self.name)
        for i, card in enumerate(self.influence):
            display(" %i: %s" % (i + 1, card.name), self.name)
        choice = get_input("> ", self.name)

        if not choice.isnumeric():
            assert False, "Choice is not numeric"
        choice = int(choice)
        if not (choice == 1 or choice == 2):
            assert False, "Invalid choice, try again"
        if choice > len(self.influence):
            assert False, "Invalid choice, try again"
            
        return self.influence[choice - 1]

    def selectAmbassadorInfluence(self, choices, influenceRemaining):
        """ returns one or two cards from the choices. """
        finalChoices = []
        
        def askChoice(choices, get_inputMessage):
            for i, choice in enumerate(choices):
                display(" %i: %s" % (i + 1, choice.name), self.name)
            
            card = get_input(get_inputMessage, self.name)
            
            if not card.isnumeric():
                assert False, "Card is not numeric"
                
            card = int(card) - 1
            if card < 0 or card >= len(choices):
                assert False, "Card is out of range"
            
            card = choices[card]
            return card
        
        ClearScreen("Ambassador success", 24)

        display("\n%s, these are the cards you drew:" % (self.name), self.name)
        
        card1 = askChoice(choices, "Select the first card to take> ")
        choices.remove(card1)
        
        if (influenceRemaining == 1):
            return [card1]
        else:
            display("")
            card2 = askChoice(choices, "Select the second card to take>")
            return [card1, card2]

def ClearScreen(headerMessage, headerSize = 10):
    display("%s" % (headerMessage))
    # os.system('cls' if os.name == 'nt' else 'clear')    # http://stackoverflow.com/a/2084628/1599
    
    # # http://stackoverflow.com/questions/17254780/showing-extended-ascii-characters-in-python-3-in-both-windows-and-linux
    # dic = {
    # '\\' : b'\xe2\x95\x9a',
    # '-'  : b'\xe2\x95\x90',
    # '/'  : b'\xe2\x95\x9d',
    # '|'  : b'\xe2\x95\x91',
    # '+'  : b'\xe2\x95\x94',
    # '%'  : b'\xe2\x95\x97',
    # }

    # def decode(x):
    #     return (''.join(dic.get(i, i.encode('utf-8')).decode('utf-8') for i in x))

    # display(decode("+%s%%" % ('-' * headerSize)))
    # display(decode("|%s|"  % (headerMessage.center(headerSize))))
    # display(decode("\\%s/" % ('-' * headerSize)))
    
def showTurnOrder(currentPlayerShown):
    header = [" Turn order", ""]    
    
    for i, player in enumerate(Players):
        headerStr = "   %i: %s" % (i + 1, player.name)
        if player == currentPlayerShown:
            headerStr = "  >" + headerStr.strip()
        header.append(headerStr)
        
    maxLen = max([len(row) for row in header]) + 2
    for i, row in enumerate(header):
        header[i] = row + (" " * (maxLen - len(row)))
        
    # header[1] = "-" * maxLen
        
    ClearScreen("\n".join(header), maxLen)
        

def showDeckList():
    display("There are %i cards in the Court Deck" % (len(GameState.Deck)))
    
    if FreeMode:
        # calculate what cards can be in the court deck
        deck = GameState.CardsAvailable * 3
        for player in Players:
            for card in player.influence:
                try:
                    deck.remove(card)
                except ValueError:
                    # one of the players received more than 3 copies of a card.
                    # add a "fake card" into the deck as indicator
                    class FakeCard(action.Action):  pass
                    FakeCard.name = "%s (Extra)" % (card.name)
                    deck.append(FakeCard)
        for card in GameState.RevealedCards:
            deck.remove(card)
            
        deck = [card.name for card in deck]
        deck.sort()
        
        display("Theoritical cards are:")
        for card in deck:
            display(" ", card)

def showRevealedCards():
    size = len(GameState.RevealedCards)
    if size == 0:
        return
        
    display("There are %i cards that has been revealed:" % (size))

    reveals = [card.name for card in GameState.RevealedCards]
    reveals.sort()
    for card in reveals:
        display("   ", card)

def showActions():
    for i, action in enumerate(AvailableActions):
        if action.name != "Contessa":   # ignore Contessa as a possible action.
            display(" %i: %s" % (i + 1, action.name))
    # display(" X: Exit the game")

def SelectCards(message, twoCards):
    display(message)
    for i, card in enumerate(GameState.CardsAvailable):
        display("%i: %s" % (i + 1, card.name))
    
    def get_inputCard(message):
        card = get_input(message)
        if not card.isnumeric():
            return get_inputCard(message)
        card = int(card) - 1
        
        if not (card >= 0 and card < len(GameState.CardsAvailable)):
            return get_inputCard(message)
            
        return GameState.CardsAvailable[card]
    
    card1 = get_inputCard("Card #1: ")
    
    if not twoCards:
        return [card1]
    else:
        card2 = get_inputCard("Card #2: ")
        return [card1, card2]
        
def SetupActions():
    global AvailableActions
    for action in GameState.CommonActions:
        AvailableActions.append(action)
    for action in GameState.CardsAvailable:
        AvailableActions.append(action)

def SetupRNG():
    """ This setups the RNG to have the cards come from the user instead """
    if not FreeMode:
        return
    
    def randomShuffle(deck):    pass            # does not shuffle
    def randomSelector(deck):    
        message = "Select the card the player received: "
        cards = SelectCards(message, False)
        return cards[0]
    
    GameState.randomShuffle  = randomShuffle
    GameState.randomSelector = randomSelector
    

def Setup():
    # How many people are playing?
    # Generate the player list
    # Shuffle the player list    
    GameState.reset()
    SetupActions()
    
    def GetNumberOfPlayers():
        # PlayerCount = get_input("How many players (2-6)? ")
        PlayerCount = 6
        return PlayerCount
        
    PlayerCount = GetNumberOfPlayers()
    #PlayerCount = 2        # for testing purposes
    
    def CreatePlayer(Number):
        player = ConsolePlayer()
        
        player.name = ""
                
        if player.name.strip() == "":
            player.name = random.choice(defaultNames)
            defaultNames.remove(player.name)
            display(" Player %i's name is %s\n" % (Number + 1, player.name))
            
        if FreeMode:                
            message = "Select %s's cards" % (player.name)
            player.influence = SelectCards(message, True)
            
            display(" Player %s is holding: %s and %s\n" % (player.name, player.influence[0].name, player.influence[1].name))
                
        return player

    display("\n")
    for i in range(PlayerCount):
        Players.append(CreatePlayer(i))
        
    SetupRNG()
    random.shuffle(Players)

    global PlayersAlive
    PlayersAlive = [player for player in Players if player.alive]
    
def MainLoop():
    # Infinite loop until one player remains
    global PlayersAlive, CurrentPlayer, GameIsRunning
    
    GameIsRunning = True
    while GameIsRunning and len(PlayersAlive) > 1:
        player = Players[CurrentPlayer]
        ConsolePlayer.ShowBlockOptions = True
        
        def showInfo():            
            PlayerList = Players[CurrentPlayer:] + Players[0:CurrentPlayer]
            paddingWidth = 16
            headerList = []
            headerStr = ""
            rowWidth = 0
            
            for playerInfo in PlayerList:            
                name = playerInfo.name 
                coins = playerInfo.coins
                headerStr += f"{name} has {coins} coins.\n"

            headerList.append(headerStr)
            ClearScreen("\n".join(headerList), rowWidth)
            
            display("")
            showDeckList()
            showRevealedCards()
            heldCards = " and ".join([card.name for card in player.influence])
            display("\n\n%s's cards are: %s" % (player.name, heldCards), player.name)
        
        def Cleanup():
            global CurrentPlayer
            CurrentPlayer += 1
            if CurrentPlayer >= len(Players): CurrentPlayer = 0
            
            global PlayersAlive 
            PlayersAlive = [player for player in Players if player.alive]
        
        def ChooseAction():    
            move = get_input("Action> ")

            if not move.isnumeric():

                assert False, "Move invalid, write numbers"
            move = int(move) - 1
            
            if not (move >= 0 and move < len(AvailableActions)):
                assert False, "Move out of range"
            
            status = False
            
            def ChooseTarget():
                PossibleTargets = list(Players)
                PossibleTargets.remove(player)
                
                PossibleTargets = [player for player in PossibleTargets if player.alive]
                
                if len(PossibleTargets) == 1:
                    return PossibleTargets[0]
                
                display("\nPossible targets:")
                for i, iterPlayer in enumerate(PossibleTargets):
                    display(" %i: %s" % (i + 1, iterPlayer.name))
                target = get_input("Choose a target> ")
                
                if not target.isnumeric():
                    return ChooseTarget()
                target = int(target) - 1
                if target < 0 or target >= len(PossibleTargets):
                    return ChooseTarget()
                
                return PossibleTargets[target]

            if player.coins < AvailableActions[move].coinsNeeded:
                display(" You need %i coins to play %s. You only have %i coins." % (AvailableActions[move].coinsNeeded, AvailableActions[move].name, player.coins))
                ChooseAction()
                return
                
            if player.coins >= action.ForceCoupCoins and AvailableActions[move].name != "Coup":
                display("Player has %i coins. Forced Coup is the only allowed action" % (player.coins))
                ChooseAction()
                return            
            
            target = None
            if AvailableActions[move].hasTarget:
                target = ChooseTarget()

            try:
                header = []
                headerStr = "%s is playing %s" % (player.name, AvailableActions[move].name)
                headerLen = len(headerStr) + 4
                headerStr = headerStr.center(headerLen)
                header.append(headerStr)
                
                if not target is None:
                    headerStr = " (target: %s)" % (target.name)
                    headerStr += " " * (headerLen - len(headerStr))
                    header.append(headerStr)
                
                ClearScreen("\n".join(header), headerLen)
                
                status, response = player.play(AvailableActions[move], target)
            except action.ActionNotAllowed as e:
                display(e.message)
                ChooseAction()
                return
            except action.NotEnoughCoins as exc:
                display(" You need %i coins to play %s. You only have %i coins." % (exc.coinsNeeded, AvailableActions[move].name, player.coins))
                ChooseAction()
                return
            except action.BlockOnly:
                display("You cannot play %s as an action" % (AvailableActions[move].name))
                ChooseAction()
                return
            except action.TargetRequired:
                display("You need to select a valid target.\n")
                showActions()
                ChooseAction()
                return
                
            if status == False:
                display(response)
            
        if player.alive:
            showInfo()
            display("\nAvailable actions:")
            showActions()
            ChooseAction()
            
        Cleanup()
        
    if len(PlayersAlive) == 1: 
        ClearScreen("The winner is %s" % (PlayersAlive[0].name), 79)
    
def main():
    ClearScreen("Game Setup", 50)
    Setup()

    for player in Players:
        showTurnOrder(player)
        
        display("\n%s, please see your cards" % player.name, player.name)
        heldCards = " and ".join([card.name for card in player.influence])
        display("\n%s\n" % (heldCards), player.name)
        # get_input("%sPress ENTER to hide your cards" % (padding))

    ClearScreen("Game start", 14)
    # get_input("\n%s, press enter key to start the game..." % (Players[0].name))
    MainLoop()
    
if __name__ == "__main__":
    main()