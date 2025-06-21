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


def send_api_request(name) :
    """
    Send an API request to the LLM.
    read content from buffers/name.txt 
    returns the answer as a string
    """
    with open(f"buffers/{name}.txt", "r") as f :
        content = f.read()

    async def chat(message):

        content = f"You are a master player of the game of Coup. You are given the following information: {message}."
        AdditionalRules= [
            "When forced Coup is the only allowed move, then choose the action to do the coup, typically 3.",
            "Read carefully the instructions at the end which specify the actions allowed. Only pick one of the actions allowed. For example,select influence to lose: 1: Duke 2: Captain. Then, pick either 1 or 2, never 3 or higher number.",
            "Write your answer within the block <answer> </answer>.  e.g. <answer> 1 </answer>.  Be brief and to the point."
            ]
        content += "\n\n".join(AdditionalRules)
        
        rich.print(content)
        response = await AsyncClient().generate(model='gemma3:1b',prompt=content)
        rich.print(response.response)
        answer = response.response.strip("<answer>").strip("</answer>")
        return answer

    answer = asyncio.run(chat(content)).strip()
    rich.print(f"++++Answer: {answer}++++")
    return answer



