import os
import sys
from pybuilder import bootstrap
from pybuilder.core import use_plugin, init, task, depends

src_path = os.path.join("src", "main", "python")
sys.path.append(src_path)
from database import Database
from app import app

use_plugin("python.coverage")
use_plugin("python.core")
use_plugin("python.unittest")
use_plugin("python.install_dependencies")
use_plugin("python.flake8")
use_plugin("python.distutils")

name = "ecommerce_site"
default_task = ["publish", "analyze"]


@init
def set_properties(project):
	project.set_property("flake8_break_build", False)
	project.set_property("flake8_verbose_output", True)
	project.set_property("flake8_ignore", "W191,E117")
	project.set_property("coverage_reset_modules", True)
	project.set_property("coverage_threshold_warn", 100)
	project.set_property("coverage_branch_threshold_warn", 1)
	project.set_property("coverage_branch_partial_threshold_warn", 1)
	project.set_property("coverage_exceptions", [])
	project.set_property("coverage_break_build", False)
	# project.depends_on_requirements("requirements.txt")


@task
def setup_db(project):

	database_uri = os.path.join("src", "main", "python", "database.db")
	if not os.path.exists(database_uri):
		print("setting up the database...")
		db = Database(database_uri)

		db.initialize_database()

		# add sample inventory
		db.add_category("tools")

		hammer = {
			"categoryID": 1,
			"name": "hammer",
			"description": "steel, rubber grip",
			"imageURL": None,
			"price": 1000,
			"quantityAvailable": 10
		}

		db.add_product(hammer)

		db.add_category("books")

		book = {
			"categoryID": 2,
			"name": "Python book",
			"description": "for programmers",
			"imageURL": None,
			"price": 2000,
			"quantityAvailable": 100
		}
		
		db.add_product(book)


		db.add_category("tech")

		smart_watch = {
			"categoryID": 3,
			"name": "smart watch",
			"description": "leather band",
			"imageURL": None,
			"price": 20000,
			"quantityAvailable": 50
		}
		
		db.add_product(smart_watch)

		print("database initialized")
	else:
		print("database exists moving on")

@task
@depends("setup_db")
def run(project):
	app.run()

bootstrap()