from dotenv import load_dotenv
import os
from os.path import join, dirname

# load environment variables
dotenv_path = join(dirname(dirname(__file__)), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
