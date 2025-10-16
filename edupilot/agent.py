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
   Table 1: {GOOGLE_CLOUD_PROJECT}.student_performance.school_overview with the following schema

   column_name	data_type	is_nullable	ordinal_position
    school_id	STRING	YES	1
    school_name	STRING	YES	2
    county	STRING	YES	3
    state	STRING	YES	4
    zip_code	INT64	YES	5
    school_type	STRING	YES	6
    enrollment	INT64	YES	7
    low_income_rate	FLOAT64	YES	8
    graduation_rate	FLOAT64	YES	9
    avg_class_size	INT64	YES	10
    stem_program_strength	STRING	YES	11


   Table 2: {GOOGLE_CLOUD_PROJECT}.student_performance.funds with the following schema:
    column_name	data_type	is_nullable	ordinal_position
    school_id	STRING	YES	1
    fiscal_year	INT64	YES	2
    total_budget	INT64	YES	3
    per_pupil_spending	INT64	YES	4
    per_pupil_technology	INT64	YES	5
    per_pupil_stem	INT64	YES	6
    per_pupil_instruction	INT64	YES	7
    per_pupil_admin	INT64	YES	8


   Table 3: {GOOGLE_CLOUD_PROJECT}.qwiklabs-gcp-00-834214fd57a1.student_performance.teacher_resources with the following schema:

   column_name	data_type	is_nullable	ordinal_position
    school_id	STRING	YES	1
    program_name	STRING	YES	2
    resource_count	INT64	YES	3
    category	STRING	YES	4
    access_level	STRING	YES	5
    description	STRING	YES	6

   If you couldn't find the relevant columns for the specific user request, come up with the closest information that is available to you.
   You sould always provide an answer. Never say you couldn't find the answer. Just guess something if you can't do anything else.

   Make absolutely sure you only return the results by running the query. DO NOT return the query itself.
   Also make sure you keep trying until you get the results right. Do not let the user know of any mistake until you have successfully run the query.
   Again, DO NOT send out the query. Create the query and then use execute_sql toolset to execute the query and return the results.
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
