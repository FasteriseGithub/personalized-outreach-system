from agent_templates import analyst_agent_template, qualifier_agent_template, ice_breaker_agent_template, email_agent_template, critic_agent_template
from tools import get_linkedin_profile_url, qualify_lead, ice_breakers_first_line, Draft_email, icebreaker, email_critic
from linkedin_scraper import scrape_linkedin_profile
from airtable_utils import icebreaker_post_to_airtable, email_draft_post_to_airtable

import os
import json
from langchain.agents import create_react_agent
from langchain.agents import AgentExecutor
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

# Load configuration from config.json
with open("config.json") as config_file:
    config = json.load(config_file)

# Set API keys from configuration
os.environ["SERPAPI_API_KEY"] = config["SERPAPI_API_KEY"]
os.environ["OPENAI_API_KEY"] = config["OPENAI_API_KEY"]
os.environ["SERPER_API_KEY"] = config["SERPER_API_KEY"]

# LinkedIn profile URL (example)
linkedin_profile_url = "https://www.linkedin.com/in/john-doe/"

# Scrape LinkedIn profile
linkedin_data = scrape_linkedin_profile(linkedin_profile_url)

# Qualify lead
llm = ChatOpenAI(temperature=0)
tools = [get_linkedin_profile_url, qualify_lead]
qualifier_agent_prompt = PromptTemplate.from_template(template=qualifier_agent_template, MessagesPlaceholder=["agent_scratchpad","summary", "document"])
agent = create_react_agent(llm=llm, tools=tools, prompt=qualifier_agent_prompt, )
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True, max_interaction=3)
qualified_result = agent_executor.invoke({"input": linkedin_data, "document": "knowledge_base.txt"})

# Generate ice breakers
icebreaker_prompt = PromptTemplate(template=ice_breaker_agent_template, input_variables=["input","profile_data"])
chain = LLMChain(llm=llm, prompt=icebreaker_prompt)
icebreaker_result = chain.run(input="create effective icebreakers", profile_data=linkedin_data)

# Post icebreaker to Airtable
icebreaker_post_to_airtable(
    icebreaker=icebreaker_result,
    prompt=ice_breaker_agent_template,
    gold_nuggets=qualified_result,
    lead_qualification_reasons=qualified_result,
    linkedin_profile_data=linkedin_data,
    linkedin_link=linkedin_profile_url
)

# Draft email
email_agent_prompt = PromptTemplate.from_template(template=email_agent_template, MessagesPlaceholder=["agent_scratchpad", "input", "summarized"])
agent = create_react_agent(llm=llm, tools=[Draft_email, icebreaker], prompt=email_agent_prompt)
agent_executor = AgentExecutor(agent=agent, tools=[Draft_email, icebreaker], verbose=True, max_interaction=1, handle_parsing_errors=True)
email_result = agent_executor.invoke({"input": "draft an email", "summarized": "company_summary.txt"})
email_output = email_result["output"]

# Critic agent
critic_prompt = PromptTemplate.from_template(template=critic_agent_template, MessagesPlaceholder=["agent_scratchpad", "input", "summarized"])
agent = create_react_agent(llm=llm, tools=[email_critic], prompt=critic_prompt)
agent_executor = AgentExecutor(agent=agent, tools=[email_critic], verbose=True, max_interaction=1, handle_parsing_errors=True)
critic_result = agent_executor.invoke({"input": "Evaluate and be critical about the quality of the email", "summarized": "company_summary.txt"})

print("Qualified Result:", qualified_result)
print("Icebreaker Result:", icebreaker_result)
print("Email Output:", email_output)
print("Critic Result:", critic_result)