import os
import sys
import logging

sys.path.append("..")
from callback_logging import log_query_to_model, log_model_response
from dotenv import load_dotenv
import google.cloud.logging
from google.adk import Agent
from google.genai import types
from typing import Optional, List, Dict

from google.adk.tools.tool_context import ToolContext

from edupilot.bigquery_utils import bigquery_toolset

load_dotenv()

cloud_logging_client = google.cloud.logging.Client()
cloud_logging_client.setup_logging()

# Tools (add the tool here when instructed)


# Agents

data_agent = Agent(
    name="data_agent",
    model=os.getenv("MODEL"),
    description="Finds and queries public education datasets",
    instruction="""
        - Provide the user options for attractions to visit within their selected country.
        """,
    before_model_callback=log_query_to_model,
    after_model_callback=log_model_response,
    # When instructed to do so, paste the tools parameter below this line

    )

insights_agent = Agent(
    name="insights_agent",
    model=os.getenv("MODEL"),
    description="Analyzes user needs and the data and provides suggestions",
    instruction="""
        Provide a few suggestions of popular countries for travelers.
        
        Help a user identify their primary goals of travel:
        adventure, leisure, learning, shopping, or viewing art

        Identify countries that would make great destinations
        based on their priorities.
        """,
    before_model_callback=log_query_to_model,
    after_model_callback=log_model_response,
)

bigquery_agent = Agent(
   model="gemini-2.0-flash",
   name="bigquery_agent",
   description=(
       "Agent that answers questions about BigQuery data by executing SQL queries"
   ),
   instruction=""" You are a data analysis agent with access to several BigQuery tools. Make use of those tools to answer the user's questions.

   """,
   tools=[bigquery_toolset],
)

root_agent = Agent(
    name="steering",
    model=os.getenv("MODEL"),
    description="Start an education planner.",
    instruction="""
        You are a  conversational agent that empowers parents, educators, and public officials to identify needs, compare resources, and prioritize interventions that directly address educational gaps and needs.
        Ask the user what are important criteria for them in selecting schools.
        If they need query data about BigQuery, send them to the 'bigquery_agent'.
        """,
    generate_content_config=types.GenerateContentConfig(
        temperature=0,
    ),
    sub_agents=[bigquery_agent]
)
