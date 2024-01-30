from openai import OpenAI
from dotenv import load_dotenv
import json
import argparse
import tqdm
import time
import os


if __name__ == '__main__':
# ====================================== SETTINGS ====================================== #
    load_dotenv(".env")

    model = "gpt-4-0125-preview"
    openai_key = os.getenv("OPENAI_API_KEY")
    summeval_file_path = os.getenv("summeval_20sample_file_path")
    prompt_file_path =  os.getenv("prompt_file_path")
    save_file_path = os.getenv("save_file_path")

    # system_id: M17 = T5
# =================================================================================== #

    client = OpenAI(api_key=openai_key)
    summeval = json.load(open(summeval_file_path))
    prompt = open(prompt_file_path).read()

    ignore = 0

    new_json = []
    for instance in tqdm.tqdm(summeval):
        source = instance['source']
        system_output = instance['system_output']
        cur_prompt = prompt.replace('{{Document}}', source).replace('{{Summary}}', system_output)
        instance['prompt'] = cur_prompt

        while True:
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "system", "content": cur_prompt}],
                    temperature=1,
                    max_tokens=5,
                    top_p=1,
                    frequency_penalty=0,
                    presence_penalty=0,
                    stop=None,
                    n=20
                )
                time.sleep(0.5)

                all_responses = [response.choices[i].message.content for i in range(len(response.choices))]
                instance['all_responses'] = all_responses
                new_json.append(instance)
                break
            except Exception as e:
                print(e)
                if ("limit" in str(e)):
                    time.sleep(2)
                else:
                    ignore += 1
                    print('ignored', ignore)

                    break
        

    print('ignored total', ignore)
    with open(save_file_path, 'w') as f:
        json.dump(new_json, f, indent=4, ensure_ascii = False)
