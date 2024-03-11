# -*- coding: utf-8 -*-

# Commented out IPython magic to ensure Python compatibility.
#install all packages
!pip install langchain
!pip install langchain-community
!pip install langchain-openai
!pip install cohere
!pip install requests
!pip install google-search-results
!pip install langchainhub
# %pip install --upgrade --quiet  "unstructured[all-docs]"
!pip install fastapi
!pip install kaleido
!pip install uvicorn
!pip install pydantic

#import all libraries
from langchain_community.utilities import GoogleSerperAPIWrapper
from typing import Any, Dict, List, Optional
from langchain.agents import Tool
from langchain.tools import  tool
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_react_agent, load_tools
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate,SystemMessagePromptTemplate,AIMessagePromptTemplate,PromptTemplate,MessagesPlaceholder
import pprint
from langchain import hub
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List
from langchain.agents.format_scratchpad import format_to_openai_function_messages
from langchain_community.document_loaders import DirectoryLoader
from pprint import pprint
from langchain.chains import LLMChain
from langchain_community.document_loaders import UnstructuredFileLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import requests
from langchain_core.pydantic_v1 import BaseModel, Field, validator
from uuid import uuid4
import os

from langchain.chains import (
    StuffDocumentsChain,
    LLMChain,
    ReduceDocumentsChain,
    MapReduceDocumentsChain,
)

from langchain.chains.summarize import load_summarize_chain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain



unique_id = uuid4().hex[0:8]
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = f"Tracing Walkthrough - {unique_id}"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"] = "ls__122d2ee48a954006a2ce6515be96e2fc"  # Update to your API key

from langsmith import Client

client = Client()

"""## Find LinkedIn Profile through Google (deprecated)"""

#set your api-keys in an environment
import os
os.environ['SERPAPI_API_KEY']="2927372a3d32f8da15d1f67e8b210a17883779c5"


os.environ['OPENAI_API_KEY']="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"

os.environ['SERPER_API_KEY']="2927372a3d32f8da15d1f67e8b210a17883779c5"

class CustomGoogleSerperAPIWrapper(GoogleSerperAPIWrapper):
    def __init__(self):
        super().__init__(k=3)

    # getting metadata from my search results in google
    def _parse_snippets(self, results: dict) -> List[str]:
        pprint(results)
        snippets = []

         # extract value from the google search metadata
        for result in results[self.result_key_for_type[self.type]][:self.k]:
            if "snippet" in result:
                snippets.append(result["snippet"])
            for attribute, value in results.get("attributes", {}).items():
                snippets.append(f"{attribute}: {value}.")
            if "link" in result and "title" in result:
                snippets.append(f"""{result["title"]}: {result["link"]}.""")

        if len(snippets) == 0:
            return ["No good Google Search Result was found"]
        return snippets


#one of the tools the agent would use
@tool
def get_linkedin_profile_url(name: str):
  """ expect an input as a name Searches for LinkedIn profile page of that name and returns the linkedin profile url
  useful when you want to search for name on linkedin """
  search = CustomGoogleSerperAPIWrapper()
  result = search.run(f"{name}")
  return result

llm = ChatOpenAI(temperature=0)

tools = [get_linkedin_profile_url]

template = """
            Your answer should only contain a linkedin profile url link.


            {tools}

            Use the following format:

            Question: the input question you must answer
            Thought: you should always think about what to do
            Action: the action to take, should be one of [{tool_names}]
            Action Input: the input to the action
            Observation: the result of the action
            ... (this Thought/Action/Action Input/Observation can repeat N times)
            Thought: I now know the final answer
            Final Answer: the final answer to the original input question

            ***Your final answer should only contain a linkedin profile url link***

            Begin!

           Question: {input}
           Thought:{agent_scratchpad}"""

prompt = PromptTemplate.from_template(template=template, MessagesPlaceholder=["{agent_scratchpad"] )

agent = create_react_agent(llm, tools, prompt)

agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True, max_iterations=3)

#TODO: Before running the next step, check if the leads csv contains a Linkedin_profile_url. If it doesn't, skip next step. If it does, make linkedin_profile_url = df['linkedin_profile_url']

"""## Retrieve LinkedIn profile, experience and recent posts through Relevance AI API"""

name = "Kim Clark"
linkedin_profile_url = agent_executor.invoke({"input": name})

linkedin_profile = linkedin_profile_url['output']
print(linkedin_profile)

#OVERRIDE FOR EXAMPLES:
linkedin_profile = "https://www.linkedin.com/in/kim-clark-52868894/"
name = "Kim Clark"

#Alejo:
#Relevance AI LinkedIn Scraper

relevance_api_key = 'sk-Nzc0YTcwOWQtNTU3Ni00YzQ3LWIzNTYtMGFjZWFiYjQwMGU0'
relevance_auth_token = 'c1f21666e351-4b45-a5be-161df131fcdc:sk-Nzc0YTcwOWQtNTU3Ni00YzQ3LWIzNTYtMGFjZWFiYjQwMGU0'
relevance_project_id = 'c1f21666e351-4b45-a5be-161df131fcdc'
relevance_region = 'bcbe5a'

linkedin_scraper_api_endpoint = 'https://api-bcbe5a.stack.tryrelevance.com/latest/studios/921d8f24-ff0d-479c-98fa-10b2f2972f39/trigger_limited'

payload = {
  "params": {
    "url": linkedin_profile,
    "name": name
  },
  "project": "c1f21666e351-4b45-a5be-161df131fcdc"
}

headers = {
  'Content-Type': 'application/json'

}

response = requests.post(linkedin_scraper_api_endpoint, json=payload, headers=headers)

linkedin_data = response.json()

class PersonProfile(BaseModel):
  full_name: str = Field(description="The full name of the person")
  introduction: str = Field(description="A short introduction paragraph of the person")
  projects: List[str]= Field(description="""a list of projects of the person worked or working on.""")
  experience : List[str] = Field(description=""" a list of the companies they've worked for, the roles they've held""")
  topics_of_interests: List[str] = Field(description="""a list of Topics that may interest the person""")
  recent_post : List[str] = Field(description="""recent post created by the person""")


  def to_dict(self):
    return{
        "full_name": self.full_name,
        "introduction":self.introduction,
        "projects": self.projects,
        "experience": self.experience,
        "topics_of_interest": self.topics_of_interests,
        "recent_post": self.recent_post
    }

person_parser = PydanticOutputParser(pydantic_object=PersonProfile)

analyst_agent_template = """
Given the LinkedIn information about a person, your task is to extract and structure the following details into a single valid JSON dictionary. Ensure the JSON dictionary strictly adheres to the format instructions provided, with each key mapping to a correctly formatted nested JSON dictionary or list as specified:

full_name: The person's full name.
introduction: A brief introduction paragraph about the person.
projects: A list detailing projects the person has worked on or is currently involved in.
experience: A list of companies the person has been employed by, including roles held at each.
topics_of_interests: A list of topics the person is interested in.
recent_post : A list of the recent post by the person.
LinkedIn Information Provided:
{linkedin_information}

Format Instructions:
{format_instructions}

Ensure the final output is a single valid JSON dictionary without any additional notes or explanations. Follow these steps carefully to validate the accuracy of the information and the integrity of the JSON structure before submission.

Overarching goal
Your task is crucial for personalizing outreach efforts, so take time to think and apply meticulous attention to detail during the extraction and structuring process."""


linkedin_profile_template = PromptTemplate(
    template=analyst_agent_template,
    input_variables=["linkedin_information"],
    partial_variables={"format_instructions": person_parser.get_format_instructions()},
)

llm = ChatOpenAI(temperature=0, model="gpt-4-0125-preview")
chain = LLMChain(llm=llm, prompt=linkedin_profile_template)

result = chain.run(linkedin_information=linkedin_data)
pprint(result)

"""## Read Knowledge Base to understand how the profile is relevant to Fasterise and its Real Estate Products"""

loader = UnstructuredFileLoader("/content/sample_data/Fasterise_Knowledge_Base_Real_Estate.txt")

import numpy as np
np.__version__

docs = loader.load()
docs = str(docs)

docs = """
# Fasterise Knowledge Base

## Company Overview
- **Purpose**: Leveraging AI to amplify human potential, with a focus on ethical AI use.

## Team Composition
- **Expertise**: Combines AI experts, programmers, marketers, real estate agents and mortgage lenders.

## Challenges and Solutions
- **Product Direction**: Identified AI impact areas in real estate.
- **Ethics**: Prioritized human-amplifying projects, maintaining ethical standards.

## Projects
### Ski Chalet Concierge
An AI-powered service that enhances vacation rental experiences by providing personalized recommendations, automating booking processes, and offering virtual concierge services to guests for a seamless stay. **For real estate agents, this tool can significantly improve client satisfaction and retention for vacation rental properties.**

### Scheduler Assistant
This tool streamlines employee scheduling in various industries by predicting optimal work schedules, thereby reducing manual efforts and improving efficiency. **Real estate agents can use it to optimize their viewings and meetings schedule, ensuring maximum productivity.**

### Lead Qualifier
An automated system that uses AI to qualify leads for businesses, prioritizing those most likely to convert. **This enables real estate agents to focus their efforts on high-potential clients, optimizing sales strategies.**

### Zoom Transcriber to Pinecone Integration
Captures and transcribes content from virtual meetings, making the data searchable. **This aids real estate agents in keeping track of client preferences and important discussion points for personalized follow-ups.**

### Knowledge Base Builder
Centralizes company knowledge into a single database, improving internal communication. **Real estate agencies can utilize this to streamline their operations and enhance the onboarding process for new agents.**

### Massive Personalized Outreach System
Personalizes client outreach at scale, improving engagement rates. **This system allows real estate agents to maintain personal connections with a large client base efficiently, enhancing relationship management.**

### Administrative Automation Tools
Reduces administrative tasks in real estate, including document management and client communication. **These tools help agents save time on paperwork, allowing them to focus more on client interaction and closing deals.**

### Education-focused AI Solutions
Focuses on personalized learning experiences in education. **While not directly related to real estate, these solutions highlight the potential of AI in personalizing services, a concept that can be applied to client interactions in real estate.**

Each project's relevance to real estate agents showcases the potential of AI to streamline operations, enhance client relationships, and improve overall efficiency in the real estate industry.


### Future Directions
- **Innovation**: Continual exploration of AI's transformative potential.

## Vision
- **Adaptive Growth**: Staying ahead in AI development.
- **Societal Impact**: Ethically deploying AI to enhance society.

## Engagement and Security
- **Marketing**: Uses video content and LinkedIn for engagement.
- **Ethics and Security**: Emphasizes data privacy and secure storage solutions.

## Conclusion
- **Ongoing Development**: Refines AI solutions based on feedback.
- **Community Engagement**: Uses workshops and webinars for better understanding needs.

This concise knowledge base provides a clear overview of Fasterise's objectives, projects, and ethical stance, as well as how their work is directly relevant to improving the success of Real Estate agents.
"""

text_splitter = RecursiveCharacterTextSplitter(
    # Set a really small chunk size, just to show.
    chunk_size=1000,
    chunk_overlap=20,
    length_function=len,
    is_separator_regex=False,
)
texts = text_splitter.split_text(docs)
document = text_splitter.create_documents(texts)

len(texts)

"""## Qualify Lead"""

@tool
def qualify_lead(query: str):
  "useful when evaluating and identifying if a person is a perfect match for our company based of our knowledge base "
  summary = result
  return summary

llm = ChatOpenAI(temperature=0, model="gpt-4-0125-preview")

tools = [get_linkedin_profile_url]
tools = tools + [qualify_lead]

qualifier_agent_template = """ You are a Relevance Analyst and Matchmaker with deep understaning of the artifical inteliegnce AI sector
                your role is to Carefully review the information of the person
                assess how significance the person is in artificial intelligence
                using critical thinking analyze how person information aligns with our company goals which is a artificial intelligence (AI) solution company
                Here is the knowledge base our company to get more context about what we do {document}
                Output Format
                Produce a **narrative report** detailing
                Strategic Alignment Assessment: A qualitative analysis of the profile's relevance to our strategic goals, emphasizing areas of high alignment.
                Potential Engagement Opportunities: Suggested pathways for leveraging person's expertise and experience in alignment with our strategic objectives in artificial intellgence(AI).

                {tools}

                Use the following format:

                Question: the input question you must answer
                Thought: you should always think about what to do
                Action: the action to take, should be one of [{tool_names}]
                Action Input: the input to the action
                Observation: the result of the action
                Thought: I now know the final answer
                Final Answer: the final answer to the original input question

                Begin!

               Question: {input}
               Thought:{agent_scratchpad}"""




qualifier_prompt = PromptTemplate.from_template(template=qualifier_agent_template, MessagesPlaceholder=["agent_scratchpad","summary", "document"])

agent = create_react_agent(llm=llm, tools=tools, prompt=qualifier_prompt)

agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True, max_interaction=3)

qualified_result = agent_executor.invoke({"input":result, "document":document})

summarize_agent_prompt= """ write a summary of the following text:
"{document}"
SUMMARY:"""

map_prompt_template = PromptTemplate(template=summarize_agent_prompt, input_variables=["document"])
llm_chain = LLMChain(llm=llm,prompt=map_prompt_template)
stuff_chain= StuffDocumentsChain(llm_chain=llm_chain, document_variable_name="document")
summarized = stuff_chain.run(document)
print(summarized)

"""## Ice Breakers / Hook creation based on LinkedIn profile info"""

@tool
def ice_breakers_first_line(input: str) -> str:
  """useful for creating icebreakers based on linkedin profile information, the icebreaker is for initiating conversations with professionals."""
  profile_information = result
  return profile_information

ice_breaker_agent_template =  """ You are a Ice Breakers Generator, your role is to create personalized and engaging ice breakers for initiating conversations with professionals, based on their LinkedIn profile information . These ice breakers should foster meaningful connections, reflecting the individual's professional background, interests, and communication preferences.
you should use Information extracted from the LinkedIn profile, including full name, introduction, projects, experience, topics of interest, and any other relevant details.
Cultural and Contextual Considerations: Background information that might influence the appropriateness of certain ice breakers, including industry norms, cultural nuances, and recent professional achievements.


linkedlin profile information: {profile_data}


use this Ice Breaker Generation Guidelines:

1.  Professionally Relevant:
   - Craft ice breakers that reference specific details from the individual’s professional background, such as notable projects or roles they've held. Example: "I was truly impressed by your innovative approach in [specific project]; could you share more about how you tackled [specific challenge]?"

2. Interests-Based:
   - Incorporate the person's topics of interest to create a more personal and engaging connection. Example: "I noticed you're interested in [topic]; have you seen the latest [related news/event]? What are your thoughts on it?"

3. Adaptive Communication Style:
   - Match the tone and formality of the ice breaker to the communication style preferred by the individual. This could range from formal to more casual, based on the profile's language and content.

4. Interactive and Open-Ended:
   - Ensure ice breakers encourage a response by posing questions or sharing thoughts that invite dialogue. Example: "What's your perspective on [industry trend]? I find it fascinating how it's evolving."

5.  Culturally and Contextually Aware:
   - Be mindful of cultural nuances and contextual factors, crafting ice breakers that are respectful and considerate. Example: "Congratulations on your recent achievement of [milestone]; it's a significant accomplishment in [specific context or culture]."

6. Timely and Relevant:
   - Reference recent events, achievements, or publications related to the person’s professional life. Example: "I admired your recent article on [topic]; it shed new light on [aspect]. Could you elaborate on your findings?"

7. Suggestive of Collaboration:
   - Hint at potential areas for future collaboration or mutual interest, laying the groundwork for a professional relationship. Example: "Your expertise in [field] aligns with my current project on [project]; I'd love to explore how we might collaborate."

Output:
Generate a list of 3-5 ice breakers tailored to the individual, ensuring they meet the above guidelines. Each ice breaker should be unique, personalized, and designed to initiate a productive and meaningful conversation.

---


Generate Ice Breakers:
Begin Generation:
Question: {input}
"""


icebreaker_prompt =  PromptTemplate(template=ice_breaker_agent_template, input_variables=["input","profile_data"])

llm = ChatOpenAI(temperature=0, model="gpt-4-0125-preview")
chain = LLMChain(llm=llm, prompt=icebreaker_prompt)

icebreaker_result = chain.run(input= "create effective icebreakers", profile_data = result )

print(icebreaker_result)

"""## Upload Icebreakers to Airtable"""

!pip install pyairtable

import os
from pyairtable import Api

airtable_key = 'pato8cChB3wsNWWyG.c8cea7e3657770665e0400a6dfd1819c9ebe01e606688294152e78f190e9a2a7'
airtable_api = Api(airtable_key)
table = airtable_api.table('app4ngdBC3uyeutjO', 'tbltpU7zNum9axElY')



import os
import requests
import time
from datetime import date

airtable_key = 'pato8cChB3wsNWWyG.c8cea7e3657770665e0400a6dfd1819c9ebe01e606688294152e78f190e9a2a7'
airtable_api = Api(airtable_key)

icebreakers_table = airtable_api.table('app4ngdBC3uyeutjO', 'tbltpU7zNum9axElY') #/Ice_Breakers'
emails_table = airtable_api.table('app4ngdBC3uyeutjO', 'tbl6TmlXJj90bOFaZ') #/Emails'




# Add Icebreaker to Airtable
def icebreaker_post_to_airtable(icebreaker,
                      prompt,
                      gold_nuggets,
                      lead_qualification_reasons,
                      linkedin_profile_data,
                      #agent,
                      linkedin_link,
                      email_address="None"):

    print(icebreakers_table.all())


    data = {
                "Icebreaker": icebreaker,
                "Prompt": prompt,
                "Gold Nuggets": gold_nuggets,
                "Lead Qualification Reasons": lead_qualification_reasons,
                "Profile Data": linkedin_profile_data,
                "Agent": "gpt-4-0125-preview",
                "Date": str(date.today()),
                "LinkedIn Link": linkedin_link,
                "Email": email_address #{email_address or "None"}
    }

    try:
      icebreakers_table.create(data)
    except Exception as e:
      print("ERROR: ", e)

    return data


# Add time off to Unavailability table
def email_draft_post_to_airtable(email_draft,
                                 icebreaker,
                                  prompt,
                                  gold_nuggets,
                                  lead_qualification_reasons,
                                  linkedin_profile_data,
                                  #agent,
                                  linkedin_link,
                                  email_address):
    # Get Unavailability data from airtable
    headers = {
        'Authorization': f'Bearer {airtable_key}',
        'Content-Type': 'application/json'
    }
    data = {
        "records": [
            {
            "fields": {
                "Email Draft": email_draft,
                "Prompt": prompt,
                "Agent": "gpt-4-0125-preview",
                #"Date": date.today(),
                "LinkedIn Link": linkedin_link,
                #"Email": {email_address or "None"}
            }
            }
        ]
    }
    response = requests.post(emails_tbl_url, headers=headers, json=data)
    response.raise_for_status()

#@title Upload Icebreakers to Airtable
icebreaker_post_to_airtable(icebreaker=str(icebreaker_result),
                      prompt=str(ice_breaker_template),
                      gold_nuggets=str(qualified_result),
                      lead_qualification_reasons=str(qualified_result),
                      linkedin_profile_data=str(linkedin_data),
                      #agent=llm,
                      linkedin_link=str(linkedin_profile_url))



"""## Draft Email based on prospect profile"""

@tool
def Draft_email(text: str) -> str:
    """
    useful when you need gather information about a recipient professional background. expects the input as an empty str ''
    """
    report = qualified_result
    return report

@tool
def icebreaker(text:str)-> str:
  """ useful when you want to draft email and needs icebreakers about a recipient to create a personalized introduction, expects input as an empty string"""

  email = icebreaker_result

  return email

llm = ChatOpenAI(temperature=0,model="gpt-4-0125-preview")

tools =  [Draft_email,icebreaker]

email_agent_template = """ You are a email copywriter, your role is write personalised outreach email to a potential client based on the professional information you have about the client, icebreaker about the client and knowledge you have about our company.
The email should highlights the synergy between the client expertise and our company's initiatives.
Maintain a respectful and professional tone throughout the email, ensuring the content is engaging and reflects positively on our company.
Prioritize clarity and conciseness, avoiding overly technical jargon unless it's relevant to the recipient's background

{tools}
always include the knowledge you have about company when drafting the email for example you can add our company name or any other information that is important to make email more personalised.
Here is more information about our company: {summarized}


###use the client's name in case where necessary###


Use the following format:

                Question: the input question you must answer
                Thought: you should always think about what to do
                Action: the action to take, should be one of [{tool_names}]
                Action Input: the input to the action
                Observation: the result of the action
                Thought: I now know the final answer
                Final Answer: the final answer should be only email draft

                Begin!



               Question: {input}
               Thought:{agent_scratchpad}"""





email_prompt = PromptTemplate.from_template(template=email_agent_template, MessagesPlaceholder=["agent_scratchpad", "input", "summarized"])

agent = create_react_agent(llm=llm, tools=tools, prompt=email_prompt)

agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, max_interaction=1, handle_parsing_errors=True)

email_result = agent_executor.invoke({"input":"draft an email", "summarized":summarized})

email_output = email_result['output']

print(email_output)

"""## Critic Agent to evaluate how human the email sounds, how well it flows, and how relevant it is to the prospect's profile"""

@tool
def email_critic(input: str) -> str:
    """
    useful when you want to evaluate if the email sounds human, personalised and the information matches our company projects and value offer"
    """
    email = email_output
    return email

llm = ChatOpenAI(temperature=0)

tools = [get_linkedin_profile_url]
tools = tools + [Draft_email]+[icebreaker]+[email_critic]

critic_agent_template = """ You are a email editor and communication specialist,combining your expertise in effective business communication with a deep understanding of personalized marketing strategies and  skills at identifying areas for improvement in written content.
                      your job is to review the email ensuring the email draft that is provided are both compelling and reflective of genuine human interaction.

                     {tools}

                     to get more context about business here is more informaton about what we do: {summarized}

                     From the email Highlight sections that can be made more concise or clearer to ensure the message is easily understood and free of unnecessary complexity.
                    - Suggest modifications to enhance the email's natural flow and make it more relatable and engaging to the recipient.
                    - Recommend adjustments to better reflect the company's brand voice, ensuring consistency across communications.

                    Ensure feedback is constructive, providing clear recommendations for enhancements rather than merely identifying issues.
                   Balance conciseness with completeness, ensuring the email remains informative and engaging without being overly wordy.
                   Preserve the original intent and strategic messaging of the email, ensuring proposed changes do not dilute its purpose or the call-to-action.

                    Output Format
                     Generate a **feedback report** for each email reviewed, including:
                    **Identified Areas for Improvement**: Specific sections or aspects of the email that could be enhanced for clarity, conciseness, or engagement.
                    **Suggested Revisions**: Concrete recommendations for rewriting or restructuring parts of the email to improve its overall effectiveness and appeal.
                    **Enhancement Tips**: General advice on writing techniques or strategies that could be applied to future email drafts to preemptively address common issues.


                Use the following format:

                Question: the input question you must answer
                Thought: you should always think about what to do
                Action: the action to take, should be one of [{tool_names}]
                Action Input: the input to the action
                Observation: the result of the action
                Thought: I now know the final answer
                Final Answer: the final answer to the original input question

                Begin!

               Question: {input}
               Thought:{agent_scratchpad}"""



critic_prompt = PromptTemplate.from_template(template=critic_agent_template, MessagesPlaceholder=["agent_scratchpad", "input", "summarized"])

agent = create_react_agent(llm=llm, tools=tools, prompt=critic_prompt)

agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, max_interaction=1, handle_parsing_errors=True)

critic_result = agent_executor.invoke({"input":"Evaluate and be critical about the quality of the email, including the icebreaker, relevance to prospect and the flow and human-sounding of the email,", "summarized":summarized})

"""## TODO: Iterate on Writer Agent to write the final version taking in all the information so far"""
