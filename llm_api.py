"""
This module is used to send API requests to the LLM.
ollama model is gemma3:1b
use the template 
import asyncio
from ollama import AsyncClient

async def chat():
  message = {'role': 'user', 'content': 'Why is the sky blue?'}
  response = await AsyncClient().chat(model='llama3.2', messages=[message])

asyncio.run(chat())
"""
import rich 
import asyncio
from ollama import AsyncClient

model_name = [
"gemma3:1b",
"deepseek-r1:8b",
"qwen3:4b"
]

def send_api_request(name, model_name=model_name[0]) :
    """
    Send an API request to the LLM.
    read content from buffers/name.txt 
    returns the answer as a string
    """
    with open(f"buffers/{name}.txt", "r") as f :
        content = f.read()

    async def chat(message):
        GameRules = [
            "Each player has two face-down character cards, with the remaining cards being placed in a Court Deck in the centre of the play area. Players take turns performing actions, while the other players have the opportunity to challenge or enact a counteraction.",
            "Players have 2 coins at the start of the game.",
            "For all players, one action is income, that is to take 1 coin",
            "For all players, one action is foreign aid, that is to take 2 coins",
            "For all players, one action is coup, that is to pay 7 coins to force any alive player to lose a character card",
            "If a player has 10 coins, then must do a coup",
            "For the character Duke, the action is to take 3 coins and counteraction is to block foreign aid",
            "For the character Assassin, the action is to assassinate a player and pay 3 coins to force a player to lose a character card",
            "For the character Captain, the action is to steal two coins from another player and counteraction is to block stealing.",
            "For the character Ambassador, the action is to exchange two cards and return two cards to Court Deck and counteraction is to block stealing initiated by the Captain.",
            "For the character Contessa, the counteraction is to block assassination and there is no action.",
            "Some actions and counteractions require a player to claim to have a specific character card (which they can do regardless of whether or not they have it). Such claims can be challenged by anyone in the game, sequentially. If a player is challenged, they must prove they had the played character card by revealing it from their face-down cards. If they can not or do not want to prove it, they lose the challenge, but if they can, the challenger loses. Whoever loses the challenge immediately loses one of their character cards. When a player loses both their character cards, that player is eliminated. The winner is the remaining player after all others have been eliminated."
            ]

        AdditionalRules= [
            "\nWhen forced Coup is the only allowed move, then choose the action to do the coup, typically 3.",
            "\nRead carefully the instructions at the end which specify the actions allowed. Only pick one of the actions allowed. For example,select influence to lose: 1: Duke 2: Captain. Then, pick either 1 or 2, never 3 or higher number.",
            "\nWrite your answer within the block <answer> </answer>.  e.g. <answer> 1 </answer>.  Be brief and to the point."
            "\nWhen asked for a choice between (Y/N), pick either Y or N as an answer",
            "String between <answer></answer> must be one of the following: Y/N/1/2/3/4/5/6/7/8"
            ]
        content = f"You are a master player of the game of Coup. GameRules: {"".join(GameRules)}. {"".join(AdditionalRules)} You are given the following information about the game state till now: {message}."
        
        rich.print(content)
        response = await AsyncClient().generate(model=model_name,prompt=content)
        rich.print(response.response)
        answer = response.response.strip("<answer>").strip("</answer>")
        return answer

    answer = asyncio.run(chat(content)).strip()
    rich.print(f"++++Answer: {answer}++++")
    return answer



