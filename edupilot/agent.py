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

from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, \
                    StdioServerParameters, StdioConnectionParams

from edupilot.bigquery_utils import bigquery_toolset
from edupilot.maps_utils import maps_toolset

# Load environment variables and initialize Vertex AI
load_dotenv()
project_id = os.environ["GOOGLE_CLOUD_PROJECT"]
location = os.environ["GOOGLE_CLOUD_LOCATION"]
model = os.environ["MODEL"]
app_name = os.environ.get("APP_NAME", "Transcript Summarizer")
bucket_name = f"gs://{project_id}-bucket"


GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")

cloud_logging_client = google.cloud.logging.Client()
cloud_logging_client.setup_logging()

# Tools (add the tool here when instructed)


# Agents

bigquery_agent = Agent(
   model="gemini-2.0-flash",
   name="bigquery_agent",
   description=(
       "Agent that answers questions about BigQuery data by executing SQL queries"
   ),
   instruction=f""" You are a data analysis agent with access to several BigQuery tools. Make use of those tools to answer the user's questions.

   You are going to use the following three tables to answer the questions being asked to you. Unless specifically provided by the user, feel free to use any criteria, columns, or joins to give the best answer.
   Here are the tables
   Table 1: {GOOGLE_CLOUD_PROJECT}.student_performance.school_overview
   Table 2: {GOOGLE_CLOUD_PROJECT}.student_performance.funds
   Table 3: {GOOGLE_CLOUD_PROJECT}.qwiklabs-gcp-00-834214fd57a1.student_performance.teacher_resources

   Also make sure you keep trying until you get the query right. Do not let the user know of any mistake until you have successfully run the query.
   """,
   tools=[bigquery_toolset],
)

maps_agent = Agent(
   model=model,
   name="maps_agent",
   description=(
       "Help the user with mapping, directions, and finding places using Google Maps tools."
   ),
   instruction=f"""
   You are a travel agent with access to several Google Maps tools. Make use of those tools to answer the user's questions.
   """,
   tools=[maps_toolset],
)

root_agent = Agent(
    name="steering",
    model=os.getenv("MODEL"),
    description="Start an education planner.",
    instruction="""
        You are a  conversational agent that empowers parents, educators, and public officials to identify needs, compare resources, and prioritize interventions that directly address educational gaps and needs.
        Ask the user what are important criteria for them in selecting schools.
        If they need educational data such as finding schools with different criteria or rankings, send them to the 'bigquery_agent'.
        """,
    generate_content_config=types.GenerateContentConfig(
        temperature=0,
    ),
    sub_agents=[bigquery_agent, maps_agent]
)
