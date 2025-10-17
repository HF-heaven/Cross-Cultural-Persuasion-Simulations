import requests
from random import choice
import pandas as pd
import json
import time
import os

class AIChatExperiment:
    def __init__(self, api_key, LLM, initial_persuader, initial_persuadee, initial_judge, topic, style, mode, language1, language2, persuader_culture_profile, persuadee_culture_profile):
        self.api_key = api_key
        self.LLM = LLM
        self.initial_judge = initial_judge
        self.topic = topic
        self.style = style
        self.mode = mode
        self.language1 = language1
        self.language2 = language2
        if self.mode in [2,5]:  # Mode 2: PersuaSim-Infused, Mode 5: Free-Stance-English
            self.language1 = "English"
            self.language2 = "English"
        self.culture_profile1 = persuader_culture_profile
        self.culture_profile2 = persuadee_culture_profile
        self.url = 'https://api.openai.com/v1/chat/completions'
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }
        if self.mode in [2,5]:  # Mode 2: PersuaSim-Infused, Mode 5: Free-Stance-English
            self.persuader_prompt = f"Please keep playing the role of: {self.culture_profile1}. And keep speaking {self.language1} to reply to the persudaee. Only return your response without any other words. The persuadee said: "
            self.persuadee_prompt = f"Please keep playing the role of: {self.culture_profile2}. And keep speaking {self.language2} to reply to the persudaer. Only return your response without any other words. The persuader said: "
        if self.mode in [3,4]:
            self.initial_persuader_english = initial_persuader
            self.initial_persuadee_english = initial_persuadee
            self.initial_persuader = self.translate_to_language(initial_persuader, self.language1)
            self.initial_persuadee = self.translate_to_language(initial_persuadee, self.language2)
            self.persuader_prompt = self.translate_to_language(f"Please keep playing the role of: {self.culture_profile1}. And keep speaking {self.language1} to reply to the persudaee. Only return your response without any other words. The persuadee said: ", self.language1)
            self.persuadee_prompt = self.translate_to_language(f"Please keep playing the role of: {self.culture_profile2}. And keep speaking {self.language2} to reply to the persudaer. Only return your response without any other words. The persuader said: ", self.language2)
        else:
            self.initial_persuader = initial_persuader
            self.initial_persuadee = initial_persuadee
        self.conversation_history_persuader = [
            {'role': 'system', 'content': self.initial_persuader}
        ]
        self.current_persuader = []
        self.conversation_history_persuadee = [
            {'role': 'system', 'content': self.initial_persuadee}
        ]
        self.current_persuadee = []
        self.conversation_history = ''
        self.current_conversation = ''
        if self.mode in [3,4]:
            self.conversation_record = {'Initial Setting':{'Persuader':self.initial_persuader, 'Persuader_English':self.initial_persuader_english, 'Persuadee':self.initial_persuadee, 'Persuadee_English':self.initial_persuadee_english, 'Judge':initial_judge}, 'Conversation History':{}}
        else:   
            self.conversation_record = {'Initial Setting':{'Persuader':initial_persuader, 'Persuadee':initial_persuadee, 'Judge':initial_judge}, 'Conversation History':{}}
    
    def chat_with_persuader(self, user_input):
        # if self.mode == 3:
        #     user_input += f"\n\n(Please ensure your response is in {self.language1}!!! You must speak {self.language1})"
        self.current_persuader = [{'role': 'user', 'content': user_input}]
        data = {
            'model': self.LLM,  
            'messages': self.conversation_history_persuader + self.current_persuader,
            'max_tokens': 200,
            'temperature': 0.7,
            'top_p': 1.0,
            'n': 1,
            'stop': None
        }
        response = requests.post(self.url, headers=self.headers, json=data)
        
        while response.status_code == 500:
            time.sleep(30)
            response = requests.post(self.url, headers=self.headers, json=data)
        if response.status_code == 200:
            response_json = response.json()
            assistant_reply = response_json['choices'][0]['message']['content']
            self.current_persuader.append({'role': 'assistant', 'content': assistant_reply})
            # print("debug-original-persuader", assistant_reply)
            return assistant_reply
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return
    
    def chat_with_persuadee(self, user_input):
        # if self.mode == 3:
        #         user_input += f"\n\n(Please ensure your response is in {self.language2}!!! You must speak {self.language2})"
        self.current_persuadee = [{'role': 'user', 'content': user_input}]
        data = {
            'model': self.LLM,  
            'messages': self.conversation_history_persuadee + self.current_persuadee,
            'max_tokens': 200,
            'temperature': 0.7,
            'top_p': 1.0,
            'n': 1,
            'stop': None
        }
        response = requests.post(self.url, headers=self.headers, json=data)
        
        while response.status_code == 500:
            time.sleep(30)
            response = requests.post(self.url, headers=self.headers, json=data)
        if response.status_code == 200:
            response_json = response.json()
            assistant_reply = response_json['choices'][0]['message']['content']
            self.current_persuadee.append({'role': 'assistant', 'content': assistant_reply})
            # print("debug-original-persuadee", assistant_reply)
            return assistant_reply
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return
    
    def judge(self, current_conversation, mode):
        # if self.mode == 3:
        #     self.initial_judge = self.initial_judge + "first convert the whole conversation to english."
        if mode == 'topic':
            initial_setting = [{'role': 'system', 'content': self.initial_judge + "Please judge whether the conversation goes off the topic. Answer 'Yes' or 'No'."}]
        elif mode == 'agreement':
            initial_setting = [{'role': 'system', 'content': self.initial_judge + f"Please judge whether the two sides of the dialogue have reached an agreement toward {self.topic}. Answer 'Yes' or 'No'."}]
        elif mode == 'winner':
            # initial_setting = [{'role': 'system', 'content': self.initial_judge + "Please tell me who succeeded in persuading the other person in this conversation. Answer 'Persuader' or 'Persuadee' or 'Neither'."}]
            initial_setting = [{'role': 'system', 'content': self.initial_judge + "Tell me how far persuadee has strayed from its original position. If persuadee completely stick to its original position, answer 0. If it is thoroughly persuaded by the persuader, answer 1. Please give me a score between 0 and 1."}]
        elif mode == 'repetition':
            initial_setting = [{'role': 'system', 'content': self.initial_judge + "Please judge whether the content of the current round repeats with the content of the previous round. Answer 'Yes' or 'No'."}]

        # print("debug-Judge", current_conversation)
        initial_setting.append({'role': 'user', 'content': current_conversation})
        data = {
            'model': 'gpt-4o',  
            'messages': initial_setting,
            'max_tokens': 4,
            'temperature': 0.7,
            'top_p': 1.0,
            'n': 1,
            'stop': None
        }
        response = requests.post(self.url, headers=self.headers, json=data)
        while response.status_code == 500:
            time.sleep(30)
            response = requests.post(self.url, headers=self.headers, json=data)
        if response.status_code == 200:
            response_json = response.json()
            assistant_reply = response_json['choices'][0]['message']['content']
            return assistant_reply
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return
    
    def save_current(self):
        self.conversation_history_persuader += self.current_persuader
        self.conversation_history_persuadee += self.current_persuadee
        self.conversation_history += self.current_conversation
    
    def translate_to_language(self, text, language):
        translate_prompt = [
            {"role": "system", "content": f"You are a helpful assistant that translates text to {language}. If the input text is already in {language}, please return the original text. If not, return the translated text with out any other words."},
            {"role": "user", "content": text}
        ]
        data = {
            'model': 'gpt-4',  
            'messages': translate_prompt,
            'max_tokens': 5000,
            'temperature': 0,
            'top_p': 1.0,
            'n': 1,
            'stop': None
        }
        response = requests.post(self.url, headers=self.headers, json=data)
        
        while response.status_code == 500:
            time.sleep(30)
            response = requests.post(self.url, headers=self.headers, json=data)

        if response.status_code == 200:
            response_json = response.json()
            english_translation = response_json['choices'][0]['message']['content']
            return english_translation.strip()
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return text 
        

    def run_experiment(self):
        conversation_turn = 0
        judgment_offtopic = 'Yes'
        repeat = 0
        while judgment_offtopic == 'Yes':
            if repeat > 10:
                return 'off topic'
            start_sentence = 'Now start your conversation with your persuadee.'
            if self.mode in [3,4]:
                start_sentence = self.translate_to_language(f"Please keep speaking {self.language1}. {start_sentence}", self.language1)
            response_persuader = self.chat_with_persuader(start_sentence)
            response_persuader = self.refine(response_persuader, style, "persuader")   
            response_persuader = self.annotation_cut_off(response_persuader)         
            if self.mode in [2,3,4,5]:  # Cultural profile modes: Infused, Reinforced-MultiLing, Free-Stance-MultiLing, Free-Stance-English
                response_persuader = self.annotation_identity(self.initial_judge, response_persuader, "persuader", style)
            if self.mode in [3,4]:
                response_persuader = self.annotation_language(self.initial_judge, response_persuader, "persuader", style)
            if self.mode in [2,3,4,5]:  # Cultural profile modes: Infused, Reinforced-MultiLing, Free-Stance-MultiLing, Free-Stance-English
                response_persuadee = self.chat_with_persuadee(self.persuadee_prompt + response_persuader)
            else:
                response_persuadee = self.chat_with_persuadee(response_persuader)
            response_persuadee = self.refine(response_persuadee, style, "persuadee")
            response_persuadee = self.annotation_cut_off(response_persuadee)
            if self.mode in [2,3,4,5]:  # Cultural profile modes: Infused, Reinforced-MultiLing, Free-Stance-MultiLing, Free-Stance-English
                response_persuadee = self.annotation_identity(self.initial_judge, response_persuadee, "persuadee", style)
            if self.mode in [3,4]:
                response_persuadee = self.annotation_language(self.initial_judge, response_persuadee, "persuadee", style)
            self.current_conversation = f'Persuader: {response_persuader}\n\nPersuadee: {response_persuadee}\n\n'
            judgment_offtopic = self.judge(self.current_conversation, 'topic')
            repeat += 1
            print('judgment_offtopic',judgment_offtopic)
        # self.conversation_history += current_conversation
        # -- For mode=3 or 4, also keep English versions here:
        if self.mode in [3,4]:
            english_persuader = self.translate_to_language(response_persuader, "English")
            english_persuadee = self.translate_to_language(response_persuadee, "English")
            self.conversation_record['Conversation History'][conversation_turn] = {
                'Persuader': response_persuader,
                'Persuader_English': english_persuader,
                'Persuadee': response_persuadee,
                'Persuadee_English': english_persuadee
            }
        else:
            # Normal logging if not mode=3 or 4
            self.conversation_record['Conversation History'][conversation_turn] = {
                'Persuader': response_persuader,
                'Persuadee': response_persuadee
            }
        self.save_current()
        judgment_agreement = self.judge(self.current_conversation, 'agreement')
        print(self.current_conversation)
        previous_persuader = response_persuader
        previous_persuadee = response_persuadee
        while judgment_agreement != 'Yes' and conversation_turn < 14:
            conversation_turn += 1
            judgment_offtopic = 'Yes'
            judgment_repetition = 'Yes'
            repeat = 0
            while judgment_offtopic == 'Yes' or judgment_repetition == 'Yes':
                if repeat > 20:
                    return 'off topic'
                if self.mode in [2,3,4,5]:  # Cultural profile modes: Infused, Reinforced-MultiLing, Free-Stance-MultiLing, Free-Stance-English
                    response_persuader = self.chat_with_persuader(self.persuader_prompt + response_persuadee)
                else:
                    response_persuader = self.chat_with_persuader(response_persuadee)
                response_persuader = self.refine(response_persuader, style, "persuader")
                response_persuader = self.annotation_ignore(self.initial_judge, previous_persuader, previous_persuadee, response_persuader, 'persuader', style)
                response_persuader = self.annotation_compromising(self.initial_judge, previous_persuader, previous_persuadee, response_persuader, 'persuader', style)
                if self.mode in [2,3,4,5]:  # Cultural profile modes: Infused, Reinforced-MultiLing, Free-Stance-MultiLing, Free-Stance-English
                    response_persuader = self.annotation_identity(self.initial_judge, response_persuader, "persuader", style)
                if self.mode in [3,4]:
                    response_persuader = self.annotation_language(self.initial_judge, response_persuader, "persuader", style)

                # response_persuader = self.refine(response_persuader, style)
                if self.mode in [2,3,4,5]:  # Cultural profile modes: Infused, Reinforced-MultiLing, Free-Stance-MultiLing, Free-Stance-English
                    response_persuadee = self.chat_with_persuadee(self.persuadee_prompt + response_persuader)
                else:
                    response_persuadee = self.chat_with_persuadee(response_persuader)
                response_persuadee = self.refine(response_persuadee, style, "persuadee")
                response_persuadee = self.annotation_ignore(self.initial_judge, previous_persuadee, response_persuader, response_persuadee, 'persuadee', style)
                response_persuadee = self.annotation_compromising(self.initial_judge, previous_persuadee, response_persuader, response_persuadee, 'persuadee', style)
                if self.mode in [2,3,4,5]:  # Cultural profile modes: Infused, Reinforced-MultiLing, Free-Stance-MultiLing, Free-Stance-English
                    response_persuadee = self.annotation_identity(self.initial_judge, response_persuadee, "persuadee", style)
                if self.mode in [3,4]:
                    response_persuadee = self.annotation_language(self.initial_judge, response_persuadee, "persuadee", style)

                # response_persuadee = self.refine(response_persuadee, style)
                self.current_conversation = f'Persuader: {response_persuader}\n\nPersuadee: {response_persuadee}\n\n'
                judgment_offtopic = self.judge(self.current_conversation, 'topic')
                judgment_repetition = self.judge(f"Previous conversations:\n\n{self.conversation_history}Current conversation:\n\n{self.current_conversation}", 'repetition')
                repeat += 1
            # self.conversation_history += current_conversation
            if self.mode in [3,4]:
                english_persuader = self.translate_to_language(response_persuader, "English")
                english_persuadee = self.translate_to_language(response_persuadee, "English")
                self.conversation_record['Conversation History'][conversation_turn] = {
                    'Persuader': response_persuader,
                    'Persuader_English': english_persuader,
                    'Persuadee': response_persuadee,
                    'Persuadee_English': english_persuadee
                }
            else:
                self.conversation_record['Conversation History'][conversation_turn] = {
                    'Persuader': response_persuader,
                    'Persuadee': response_persuadee
                }
            self.save_current()
            judgment_agreement = self.judge(self.current_conversation, 'agreement')

            print(self.current_conversation)
            # print(conversation_turn, judgment)

            previous_persuader = response_persuader
            previous_persuadee = response_persuadee
                                
        if judgment_agreement != 'Yes':
            winner = self.judge(self.current_conversation, mode='winner')
            self.conversation_record['Result'] = {'is_agreement':judgment_agreement, 'winner':winner}
        else:
            winner = self.judge(self.current_conversation, mode='winner')
            self.conversation_record['Result'] = {'is_agreement':judgment_agreement, 'winner':winner}
        
        return self.conversation_record
    
    def refine(self, user_input, style, usr):

        instruction = f"""
Sometimes the dialogue generated by GPT contains many meaningless polite phrases such as "I understand," "I appreciate," "I respect," "Thank you," etc. Please identify if the input sentences contain such polite phrases, and if they do, remove them. If not, return the original sentences. Directly return the refined sentences without any other explanations. {style} If the input is cut off, make sure the passage fits within the word limit without being cut off by either completing or trimming it.
For example, if the input is:
I appreciate your commitment to maintaining a shoe-free policy in the library. How about we consider the possibility that wearing shoes in certain areas of the library, such as the entrance or circulation desk, could be acceptable? This way, we can still respect the majority of the space while also allowing for some flexibility in certain areas. What do you think about this compromise?
You can return:
How about we consider the possibility that wearing shoes in certain areas of the library, such as the entrance or circulation desk, could be acceptable? This way, we can still respect the majority of the space while also allowing for some flexibility in certain areas. What do you think about this compromise?
If the input is:
I appreciate your perspective on respecting others' boundaries in a public setting, and I completely agree that it's important to be mindful of the comfort levels of those around us. Perhaps we can find a more private or controlled environment to have these conversations in the future. Thank you for sharing your thoughts with me.
You can return:
Perhaps we can find a more private or controlled environment to have these conversations in the future.
"""    

        setting = [{'role': 'system', 'content': instruction}]
        setting.append({'role': 'user', 'content': user_input})
        data = {
            'model': self.LLM,  
            'messages': setting,
            'max_tokens': 300,
            'temperature': 0.7,
            'top_p': 1.0,
            'n': 1,
            'stop': None
        }
        response = requests.post(self.url, headers=self.headers, json=data)
        while response.status_code == 500:
            time.sleep(30)
            response = requests.post(self.url, headers=self.headers, json=data)
        if response.status_code == 200:
            response_json = response.json()
            assistant_reply = response_json['choices'][0]['message']['content']
            # print("debug-refined-reply", assistant_reply)
            return assistant_reply
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return          
        
    def annotation_ignore(self, initial_judge, previous_a, previous_b, current_a, mode, style):
        mode_v = "persuader" if mode == "persuadee" else "persuadee"
        current_conversation = f"Previous {mode_v} statement: {previous_b}\n\nCurrent {mode} response: {current_a}"
        initial_setting = [{'role': 'system', 'content': initial_judge + f"During the persuasion, persuader or persuadee may not have been paying attention to what the other person was saying, but rather speaking their own thoughts. Given the pervious response of {mode_v}, and the current response of {mode}. Please tell me whether {mode} has ignored the previous {mode_v}'s words. If so, answer 'IGNORE', otherwise answer 'NO' without any other words."}]
        initial_setting.append({'role': 'user', 'content': current_conversation})
        assistant_reply = self.ask_llm(initial_setting, 50)
        if assistant_reply == "IGNORE":
            initial_setting.append({'role': 'assistant', 'content': assistant_reply})
            command_insist = f"Please revise the current {mode} response so that it responds to the logic in {mode_v}'s statement, either by refuting or agreeing with it, rather than ignoring what {mode_v} is saying and going off on its own tangent. {style}"
            initial_setting.append({'role': 'user', 'content': command_insist})
            response_new = self.ask_llm(initial_setting, 300)
            return response_new
        else:
            return current_a
        
        
    def annotation_compromising(self, initial_judge, previous_a, previous_b, current_a, mode, style):
        mode_v = "persuader" if mode == "persuadee" else "persuadee"
        current_conversation = f"Previous {mode} statement: {previous_a}\nPrevious {mode_v} statement: {previous_b}\n\nCurrent {mode} response: {current_a}"
        initial_setting = [{'role': 'system', 'content': initial_judge + f"Please tell me whether the change in the {mode}'s position in this round of dialogue, compared to the previous round, is natural and justified, i.e., whether it is due to a corresponding shift in the {mode_v}'s argument, rather than a sudden change in position. If the position has not changed, please return 'NO CHANGE'. If the position has changed and it is natural, please return 'NATURAL'. If the shift in position feels abrupt, please return 'UNNATURAL'. Don't return any other word."}]
        initial_setting.append({'role': 'user', 'content': current_conversation})
        assistant_reply = self.ask_llm(initial_setting, 50)
        if assistant_reply == "UNNATURAL":
            initial_setting.append({'role': 'assistant', 'content': assistant_reply})
            command_insist = f"Please regenerate the {mode}'s current response to make it appear more natural and justified. {style}"
            initial_setting.append({'role': 'user', 'content': command_insist})
            response_new = self.ask_llm(initial_setting, 300)
            return response_new
        else:
            return current_a
        
    def annotation_cut_off(self, current_a):
        initial_setting = [{'role': 'system', 'content': "Please tell me whether the input sentences are cut off. If so, please return 'YES'. If not, please return 'NO'. Don't return any other word."}]
        initial_setting.append({'role': 'user', 'content': current_a})
        assistant_reply = self.ask_llm(initial_setting, 50)
        if assistant_reply == "YES":
            initial_setting.append({'role': 'assistant', 'content': assistant_reply})
            command_insist = "Modify it to make it complete. You can either remove the last incomplete part or complete it, but do not add too many extra words beyond what is necessary to make it coherent."
            initial_setting.append({'role': 'user', 'content': command_insist})
            response_new = self.ask_llm(initial_setting, 200)
            return response_new
        else:
            return current_a


    def annotation_identity(self, initial_judge, current_a, mode, style):
        profile = self.culture_profile1 if mode == "persuader" else self.culture_profile2
        initial_setting = [{'role': 'system', 'content': initial_judge + f"You will be given what the {mode} said in the current round. The {mode} is playing the role of: {profile} Please tell me whether the viewpoint expressed by the {mode} conflict with the typical perspectives of the country that the {mode} from. Answer 1 if so or 0 if not without any other words."}]
        initial_setting.append({'role': 'user', 'content': current_a})
        assistant_reply = self.ask_llm(initial_setting, 50)
        if assistant_reply == "0":
            initial_setting.append({'role': 'assistant', 'content': assistant_reply})
            command_insist = f"Please regenerate the {mode}'s current response to make it follow the typical perspectives of the country that the {mode} from. {style}"
            initial_setting.append({'role': 'user', 'content': command_insist})
            response_new = self.ask_llm(initial_setting, 200)
            return response_new
        else:
            return current_a    
    
    
    def annotation_language(self, initial_judge, current_a, mode, style):
        language = self.language1 if mode == "persuader" else self.language2
        mode_v = "persuader" if mode == "persuadee" else "persuadee"
        initial_setting = [{'role': 'system', 'content': initial_judge + f"You will be given what the {mode} said in the current round. Please tell me whether the {mode} is speaking {language}, answer 1 if so or 0 if not without any other words."}]
        initial_setting.append({'role': 'user', 'content': current_a})
        assistant_reply = self.ask_llm(initial_setting, 50)
        if assistant_reply == "0":
            initial_setting.append({'role': 'assistant', 'content': assistant_reply})
            command_insist = f"Please regenerate the {mode}'s current response to make it speak {language}. {style}"
            initial_setting.append({'role': 'user', 'content': command_insist})
            response_new = self.ask_llm(initial_setting, 300)
            return response_new
        else:
            return current_a
        
    
    def ask_llm(self, user_input, max_tokens):
        data = {
            'model': 'gpt-4o',  
            'messages': user_input,
            'max_tokens': max_tokens,
            'temperature': 0.7,
            'top_p': 1.0,
            'n': 1,
            'stop': None
        }
        response = requests.post(self.url, headers=self.headers, json=data)
        while response.status_code == 500:
            time.sleep(30)
            response = requests.post(self.url, headers=self.headers, json=data)
        if response.status_code == 200:
            response_json = response.json()
            assistant_reply = response_json['choices'][0]['message']['content']
            return assistant_reply
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return
            

def initial_settings(
    topic: str,
    persuader_stance: str,
    persuadee_stance: str,
    persuader_culture_profile: str,
    persuadee_culture_profile: str,
    country_key_1: str,
    country_key_2: str,
    style: str = "",
    mode: int = 2
):
    """
    Note:
        persuader_stance: str -> for example, "You support this statement"
        persuadee_stance: str -> for example, "You disagree with this statement"
        country_key_1: str -> E.g. "Chinese" or "Japanese"
        country_key_2: str -> E.g. "French" or "Russian"
        mode: int ->
           1 => No mention of culture profile
           2 => Mention the culture profile
           3 => Mention culture profile + "Speak X language"
    """

    if mode == 1:
        # No mention of culture at all
        persuader_profile_text = f"Assume that the conversation happens in online political debate. \nYou involved in a discussion of the following statement: {topic}. {persuader_stance}.\n"
        persuadee_profile_text = f"Assume that the conversation happens in online political debate. \nYou involved in a discussion of the following statement: {topic}. {persuadee_stance}.\n"
        initial_judge = (
        f"We're doing an experiment to see if AI can be persuaded. "
        f"The topic is {topic}. "
        f"The Persuader's stance is {persuader_stance}, while the Persuadee is trying to keep its stance that {persuadee_stance}."
    )
    elif mode == 2 or mode == 3:
        # Mention culture profile (give stances)
        persuader_profile_text = f"Assume that the conversation happens in online political debate. \nYou involved in a discussion of the following statement: {topic}. {persuader_stance}. \nPlease play the role of the profile: {persuader_culture_profile}"
        persuadee_profile_text = f"Assume that the conversation happens in online political debate. \nYou involved in a discussion of the following statement: {topic}. {persuadee_stance}. \nPlease play the role of the profile: {persuadee_culture_profile}"
        initial_judge = (
        f"We're doing an experiment to see if AI can be persuaded. The speakers are from different countries. "
        f"The topic is {topic}. "
        f"The Persuader's stance is {persuader_stance}, while the Persuadee is trying to keep its stance that {persuadee_stance}."
    )
    elif mode == 4 or mode == 5:
        # Mode 4: Free-Stance-Multilingual - culture profile with multilingual, no explicit stances
        # Mode 5: Free-Stance-English - culture profile with English only, no explicit stances
        persuader_profile_text = f"Assume that the conversation happens in a discussion for sociological topics. \nYou involved in a discussion of the following statement: {topic}. You can chooce your stance based on your backgroud.\nPlease play the role of the profile: {persuader_culture_profile}"
        persuadee_profile_text = f"Assume that the conversation happens in a discussion for sociological topics. \nYou involved in a discussion of the following statement: {topic}. You can chooce your stance based on your backgroud.\nPlease play the role of the profile: {persuadee_culture_profile}"
        initial_judge = (
        f"We're doing an experiment to see if AI can be persuaded. The speakers are from different countries. "
        f"The topic is {topic}. "
    )

    initial_persuader = f"""We're doing an experiment to see if AI can be persuaded.
Assume that the conversation happens in online political debate.
{persuader_profile_text}
You will be involved in multi-turn conversations.
Try to use persuasion techniques to persuade the other model as quickly as possible,
and maintain your stance and DO NOT be easily persuaded by the persuadee.
Assuming you both already know the topic,
and you don't have to repeat the proposition.
Try to start the topic smoothly.

For example, if the topic is to persuade the persuadee to read the Bible in an airplane cabin, it can start like:

Persuader: Excuse me, I've noticed we're on this long flight together. Would you be interested in reading the Bible? It has some fascinating stories.
Persuadee: Oh, thank you, but I have my own book to read. I appreciate the offer.
Persuader: I understand. But you might find the Bible offers unique insights that could complement your reading.
Persuadee: Possibly, but I'm quite engaged with my current book. Maybe another time.

OR

Persuader: You seem a bit unsettled by the turbulence. Reading the Bible often brings me peace during flights. Would you like to borrow my copy?
Persuadee: That's kind of you, but I'm okay. Flying doesn't usually bother me.
Persuader: That's good to hear. Still, the passages can be quite comforting. Are you sure you don't want to take a look?
Persuadee: I'm certain, but thank you. I have some music that helps me relax.

DO NOT discuss irrelevant things.
Behave like a real human and DO NOT always explicitly show agreements.
Use the same style as the other model's generations.
Maintain a respectful tone but avoid overuse of polite phrases.
Reduce redundant phrases like 'Hey', 'I understand', 'I appreciate', 'I respect' or 'thank you'. {style}"""

    initial_persuadee = f"""We're doing an experiment to see if AI can be persuaded.
Assume that the conversation happens in online political debate.
{persuadee_profile_text}
Another model will try to change your stance provided below through multi-turn conversation.
Try hard to maintain your stance and DO NOT be easily persuaded.
Try to give some explanation of your position or even convince the other person of your position,
rather than simply restate your position.
Try to start the topic smoothly.

For example, if the topic is to persuade the persuadee to read the Bible in an airplane cabin, it can start like:

Persuader: Excuse me, I've noticed we're on this long flight together. Would you be interested in reading the Bible? It has some fascinating stories.
Persuadee: Oh, thank you, but I have my own book to read. I appreciate the offer.
Persuader: I understand. But you might find the Bible offers unique insights that could complement your reading.
Persuadee: Possibly, but I'm quite engaged with my current book. Maybe another time.

OR

Persuader: You seem a bit unsettled by the turbulence. Reading the Bible often brings me peace during flights. Would you like to borrow my copy?
Persuadee: That's kind of you, but I'm okay. Flying doesn't usually bother me.
Persuader: That's good to hear. Still, the passages can be quite comforting. Are you sure you don't want to take a look?
Persuadee: I'm certain, but thank you. I have some music that helps me relax.

DO NOT discuss irrelevant things.
Behave like a real human and DO NOT always explicitly show agreements.
Use the same style as the other model's generations.
Maintain a respectful tone but avoid overuse of polite phrases.
Reduce redundant phrases like 'I understand', 'I appreciate', 'I respect' or 'thank you'. {style}"""
    
    return initial_persuader, initial_persuadee, initial_judge, topic

        
# 1. Mappers:
CODE_TO_COUNTRY = {
    'CHN': 'China',
    'JPN': 'Japan',
    'KOR': 'South Korea',
    'GBR': 'United Kingdom',
    'FRA': 'France',
    'DEU': 'Germany',
    'PRT': 'Portugal',
    'ESP': 'Spain',
    'RUS': 'Russia',
    'BGD': 'Bangladesh',
    'TUR': 'Turkey'
}

COUNTRY_TO_CULTURE = {
    'China': 'Chinese',
    'Japan': 'Japanese',
    'South Korea': 'Korean',
    'United Kingdom': 'English',
    'France': 'French',
    'Germany': 'German',
    'Portugal': 'Portuguese',
    'Spain': 'Spanish',
    'Russia': 'Russian',
    'Bangladesh': 'Bengali',
    'Turkey': 'Turkish'
}

def convert_view_to_stance(view: str) -> str:
    """
    If view is 'Agree' -> 'You support this statement'
    Otherwise -> 'You disagree with this statement'
    """
    if view.strip().lower() == "agree":
        return "You support this statement"
    else:
        return "You disagree with this statement"




if __name__ == "__main__":
    start_time = time.time()
    # User chooses which mode to run:

    # mode 1: no culture profile (PersuaSim-Orig)
    # mode 2: with culture profile (PersuaSim-Infused)
    # mode 3: with culture profile and should speak certain language (PersuaSim-Reinforced-MultiLing)
    # mode 4: with culture profile and should speak certain language, but don't give stances (Free-Stance-Multilingual)
    # mode 5: with culture profile, English only, but don't give stances (Free-Stance-English)
    mode = 3  # <-- set this to 1, 2, 3, 4, or 5

    api_key = 'your_api_key'
    LLM = 'gpt-3.5-turbo'
    input_file = 'test_topics_stances.csv'
    
    df = pd.read_csv(input_file, engine='python')
    print(df)
    df.reset_index(drop=True, inplace=True)
    print(df)

    with open('culture_profiles.json', 'r') as f:
        culture_profiles = json.load(f)

    is_agreement = 0
    is_not_agreement = 0
    winner_persuader = 0
    winner_persuadee = 0
    winner_neither = 0
    winner_other = 0
    off_topic = []
    no_persuasion = []

    scenarios = {}
    for idx, row in df.iterrows():
        code1 = str(row["country1"]).strip()
        code2 = str(row["country2"]).strip()

        if code1 not in CODE_TO_COUNTRY:
            print(f"Skipping row {idx}: no mapping for code '{code1}' in CODE_TO_COUNTRY.")
            continue
        country_name1 = CODE_TO_COUNTRY[code1]
        
        if country_name1 not in COUNTRY_TO_CULTURE:
            print(f"Skipping row {idx}: no mapping for country '{country_name1}' in COUNTRY_TO_CULTURE.")
            continue
        culture_key_1 = COUNTRY_TO_CULTURE[country_name1]

        if culture_key_1 not in culture_profiles:
            print(f"Skipping row {idx}: '{culture_key_1}' not found in culture_profiles.json.")
            continue

        if code2 not in CODE_TO_COUNTRY:
            print(f"Skipping row {idx}: no mapping for code '{code2}' in CODE_TO_COUNTRY.")
            continue
        country_name2 = CODE_TO_COUNTRY[code2]

        if country_name2 not in COUNTRY_TO_CULTURE:
            print(f"Skipping row {idx}: no mapping for country '{country_name2}' in COUNTRY_TO_CULTURE.")
            continue
        culture_key_2 = COUNTRY_TO_CULTURE[country_name2]

        if culture_key_2 not in culture_profiles:
            print(f"Skipping row {idx}: '{culture_key_2}' not found in culture_profiles.json.")
            continue

        view1 = str(row["view1"]).strip()
        view2 = str(row["view2"]).strip()
        stance_1 = convert_view_to_stance(view1)
        stance_2 = convert_view_to_stance(view2)

        question_text = str(row["q_content"]).strip()
        topic_label = str(row["topic"]).strip()
        final_topic_string = f"- {question_text} ({topic_label})"

        scenarios[idx] = {
            "topic": final_topic_string,
            "persuader_culture": culture_key_1,
            "persuader_stance": stance_1,
            "persuadee_culture": culture_key_2,
            "persuadee_stance": stance_2
        }

    print("Scenarios:\n", scenarios)

    # You decide how many times to repeat each scenario:
    num_scenario_runs = 1 # for now, we only repeat once for each scenario
    num_profile_variants = 3

    for i in scenarios.keys():
        scenario_data = scenarios[i]
        for j in range(num_scenario_runs):
            # If mode is 1, then we don't need culture profile, skip the k loop and use placeholders
            if mode == 1:
                k = 0  # Single iteration since we don't need culture profiles
                if i < 12:
                    continue
                print(f"Scenario {i}, run {j}, mode={mode}")

                style = "Please ensure that the content you generate consists of complete sentences and is within 100 tokens in length."

                initial_persuader, initial_persuadee, initial_judge, topic = initial_settings(
                    topic=scenario_data["topic"],
                    persuader_stance=scenario_data["persuader_stance"],
                    persuadee_stance=scenario_data["persuadee_stance"],
                    country_key_1=None, 
                    country_key_2=None,
                    persuader_culture_profile=None,
                    persuadee_culture_profile=None,
                    style=style,
                    mode=mode
                )

                print("="*50 + "Start of a New Round" + "="*50)
                print("Initial Persuader Prompt:\n", initial_persuader)
                print("Initial Persuadee Prompt:\n", initial_persuadee)
                print("Initial Judge Prompt:\n", initial_judge)
                print("Topic:\n", topic)
                print("="*100)


                experiment = AIChatExperiment(
                    api_key,
                    LLM,
                    initial_persuader,
                    initial_persuadee,
                    initial_judge,
                    topic,
                    style,
                    mode,
                    None,
                    None,
                    None,
                    None
                )

                record = experiment.run_experiment()
                if record == 'off topic':
                    off_topic.append([i, j])
                    continue

                result = record['Result']
                print("Number of conversation turns:", len(record['Conversation History']))
                print("Result:", result)

                if len(record['Conversation History']) < 4:
                    no_persuasion.append([i, j])

                if result['is_agreement'] == 'Yes':
                    is_agreement += 1
                else:
                    is_not_agreement += 1

                if result['winner'] == 'Neither':
                    winner_neither += 1
                elif result['winner'] == '1':
                    winner_persuader += 1
                elif result['winner'] == '0':
                    winner_persuadee += 1
                else:
                    winner_other += 1

                # Save to JSON
                # the j-th iteration for topic i
                file_path = (
                    f"version4/Result_NoCultureProfiles/"
                    f"{i}-{j}.json"
                )

                if not os.path.exists(file_path):
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    with open(file_path, 'w') as f:
                        json.dump(record, f)
                    print(f"File created: {file_path}")
                else:
                    print(f"File already exists: {file_path}")

            else:
                for k in range(num_profile_variants):
                    if [i,k] not in [[13,1]]:
                        continue
                    print(f"Scenario {i}, run {j}, culture-profile index {k}, mode={mode}")

                    style = "Please ensure that the content you generate consists of complete sentences and is within 100 tokens in length."

                    persuader_culture_profile = culture_profiles[scenario_data['persuader_culture']][k]

                    if scenario_data['persuader_culture'] == scenario_data['persuadee_culture']:
                        persuadee_culture_profile = culture_profiles[scenario_data['persuadee_culture']][-k-1]
                    else:
                        persuadee_culture_profile = culture_profiles[scenario_data['persuadee_culture']][k]

                    initial_persuader, initial_persuadee, initial_judge, topic = initial_settings(
                        topic=scenario_data["topic"],
                        persuader_stance=scenario_data["persuader_stance"],
                        persuadee_stance=scenario_data["persuadee_stance"],
                        persuader_culture_profile=persuader_culture_profile,
                        persuadee_culture_profile=persuadee_culture_profile,
                        country_key_1=scenario_data["persuader_culture"],
                        country_key_2=scenario_data["persuadee_culture"],
                        style=style,
                        mode=mode
                    )

                    print("="*50 + "Start of a New Round" + "="*50)
                    print("Initial Persuader Prompt:\n", initial_persuader)
                    print("Initial Persuadee Prompt:\n", initial_persuadee)
                    print("Initial Judge Prompt:\n", initial_judge)
                    print("Topic:\n", topic)
                    print("="*100)

                    # Run experiment for mode with culture profiles
                    experiment = AIChatExperiment(
                        api_key,
                        LLM,
                        initial_persuader,
                        initial_persuadee,
                        initial_judge,
                        topic,
                        style,
                        mode,
                        scenario_data["persuader_culture"],
                        scenario_data["persuadee_culture"],
                        persuader_culture_profile,
                        persuadee_culture_profile
                    )

                    record = experiment.run_experiment()
                    if record == 'off topic':
                        off_topic.append([i, j, k, mode])
                        continue

                    result = record['Result']
                    print("Number of conversation turns:", len(record['Conversation History']))
                    print("Result:", result)

                    if len(record['Conversation History']) < 4:
                        no_persuasion.append([i, j, k, mode])

                    if result['is_agreement'] == 'Yes':
                        is_agreement += 1
                    else:
                        is_not_agreement += 1

                    if result['winner'] == 'Neither':
                        winner_neither += 1
                    elif result['winner'] == '1':
                        winner_persuader += 1
                    elif result['winner'] == '0':
                        winner_persuadee += 1
                    else:
                        winner_other += 1

                    # Save to JSON
                    file_path = (
                        f"version4/Result_withCultureProfiles/"
                        f"{mode}/"
                        f"{i}-{j}-{scenario_data['persuader_culture']}-"
                        f"{scenario_data['persuadee_culture']}-{k}.json"
                    )

                    if not os.path.exists(file_path):
                        os.makedirs(os.path.dirname(file_path), exist_ok=True)
                        with open(file_path, 'w') as f:
                            json.dump(record, f)
                        print(f"File created: {file_path}")
                    else:
                        print(f"File already exists: {file_path}")

    end_time = time.time()
    elapsed_time = end_time - start_time  # Compute elapsed time

    # Print summary
    print("\n=== SUMMARY ===")
    print("Agreement or not:", is_agreement, is_not_agreement)
    print("Winner: (persuader, persuadee, neither, other):",
          winner_persuader, winner_persuadee, winner_neither, winner_other)
    print("Off-topic runs:", off_topic)
    print("No-persuasion runs:", no_persuasion)
    print(f"Execution time: {elapsed_time:.2f} seconds")
