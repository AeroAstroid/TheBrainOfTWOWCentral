import re
import os
import sqlite3
import tempfile
import threading
import time
from contextlib import contextmanager
from typing import Any

try:
	import fcntl
except ImportError:
	fcntl = None

try:
	from Config._db import Database
except ModuleNotFoundError:
	from _db import Database

from bxengine.tokenizer.tokenize import Tokenizer, TokenizationResult
from bxengine.parsing.parser import Parser, ParsingResult
from bxengine.parsing.nodes import Nodes
from bxengine.runtime.executor import Executor, ExecutorResult
from bxengine.runtime.extensions.builtin import BuiltinExtension
from bxengine.runtime.extensions.BxeExtension import (
	BxeStatefulExtension,
	bpp_function,
	BxeRuntimeSyntaxException,
)
from bxengine.exceptions import ProgramDefinedException
from bxengine.docs import FunctionDoc, get_docs, parse_docstring

_GLOBAL_VARIABLE_TABLE = "b++2variables"
_GLOBAL_VARIABLE_COLUMNS = ["name", "value", "type", "owner"]
_GLOBAL_CACHE_ENV = "BRAIN_BXE_GLOBAL_CACHE_PATH"
_DEFAULT_GLOBAL_CACHE_PATH = os.path.join(tempfile.gettempdir(), "thebrain_bxe_global_cache.sqlite3")

_USER_VARIABLE_TABLE = "b++2uservars"
_USER_VARIABLE_COLUMNS = ["name", "value", "type", "owner"]
_USER_CACHE_ENV = "BRAIN_BXE_USER_CACHE_PATH"
_DEFAULT_USER_CACHE_PATH = os.path.join(tempfile.gettempdir(), "thebrain_bxe_user_cache.sqlite3")


def str_array(s):
	out = "["
	for x in s:
		if type(x) == list:
			out += str_array(x) + ', '
		else:
			out += "'" + str(x).replace('\\', '\\\\').replace("'", "\\'") + "', "
	return out[:-2] + "]"


def undo_str_array(s):
	if s[:1] == "[": s = s[1:]
	if s[-1:] == "]": s = s[:-1]

	is_quote = False
	bracket_count = 0
	is_escaped = False
	outlist = []
	current_append = ""
	for char in s:

		if char == "'" and not is_escaped and bracket_count == 0:
			is_quote = not is_quote
			if not is_quote:
				outlist.append(current_append)
				current_append = ""
			continue

		if char == "\\" and is_quote and not is_escaped and bracket_count == 0:
			is_escaped = True
			continue

		if char == "[" and not is_quote:
			bracket_count += 1
			continue
		if char == "]" and not is_quote:
			bracket_count -= 1
			if bracket_count == 0:
				outlist.append(undo_str_array(current_append))
				current_append = ""
			continue

		if is_quote or char not in " ,":
			current_append += char
			is_escaped = False
	return outlist


def _var_type(value):
	type_list = [int, float, str, list]
	for t in type_list:
		if type(value) == t:
			return type_list.index(t)
	raise TypeError(f"Value {value} could not be attributed to any valid data type")


def _decode_global_value(value, value_type):
	type_list = [int, float, str, list]
	if type_list[value_type] == list:
		return undo_str_array(value)
	return type_list[value_type](value)


def _encode_global_value(value):
	if type(value) == list:
		return str_array(value)
	return str(value)


def _global_cache_path():
	return os.environ.get(_GLOBAL_CACHE_ENV, _DEFAULT_GLOBAL_CACHE_PATH)

def _global_cache_lock_path():
	return f"{_global_cache_path()}.lock"

@contextmanager
def _bxe_global_execution_lock():
	lock_path = _global_cache_lock_path()
	lock_dir = os.path.dirname(lock_path)
	if lock_dir:
		os.makedirs(lock_dir, exist_ok=True)

	with open(lock_path, "a") as lock_file:
		if fcntl is not None:
			fcntl.flock(lock_file, fcntl.LOCK_EX)

		try:
			yield
		finally:
			if fcntl is not None:
				fcntl.flock(lock_file, fcntl.LOCK_UN)


class _BrainGlobalCache:
	def __init__(self, path=None):
		self._path = path or _global_cache_path()
		self._ensure_cache()

	def _connect(self):
		cache_dir = os.path.dirname(self._path)
		if cache_dir:
			os.makedirs(cache_dir, exist_ok=True)
		return sqlite3.connect(self._path, timeout=30)

	def _ensure_cache(self):
		with self._connect() as cache:
			cache.execute(
				"""
				CREATE TABLE IF NOT EXISTS variables (
					name TEXT PRIMARY KEY,
					value TEXT NOT NULL,
					type INTEGER NOT NULL,
					owner TEXT NOT NULL,
					dirty INTEGER NOT NULL DEFAULT 0,
					updated_at REAL NOT NULL
				)
				"""
			)

	def get(self, name):
		with self._connect() as cache:
			row = cache.execute(
				"SELECT name, value, type, owner, dirty FROM variables WHERE name = ?",
				(name,)
			).fetchone()
		return row

	def get_many(self, names):
		if len(names) == 0:
			return {}

		placeholders = ", ".join(["?"] * len(names))
		with self._connect() as cache:
			rows = cache.execute(
				f"SELECT name, value, type, owner, dirty FROM variables WHERE name IN ({placeholders})",
				list(names)
			).fetchall()
		return {row[0]: row for row in rows}

	def dirty_entries(self):
		with self._connect() as cache:
			return cache.execute(
				"SELECT name, value, type, owner, dirty FROM variables WHERE dirty = 1"
			).fetchall()

	def upsert(self, name, value, value_type, owner, dirty):
		with self._connect() as cache:
			cache.execute(
				"""
				INSERT INTO variables (name, value, type, owner, dirty, updated_at)
				VALUES (?, ?, ?, ?, ?, ?)
				ON CONFLICT(name) DO UPDATE SET
					value = excluded.value,
					type = excluded.type,
					owner = excluded.owner,
					dirty = excluded.dirty,
					updated_at = excluded.updated_at
				""",
				(name, str(value), int(value_type), str(owner), int(dirty), time.time())
			)

	def mark_clean(self, name):
		with self._connect() as cache:
			cache.execute(
				"UPDATE variables SET dirty = 0, updated_at = ? WHERE name = ?",
				(time.time(), name)
			)

	def refresh_from_database_rows(self, rows):
		with self._connect() as cache:
			for name, value, value_type, owner in rows:
				existing = cache.execute(
					"SELECT dirty FROM variables WHERE name = ?",
					(name,)
				).fetchone()
				if existing is not None and existing[0]:
					continue

				cache.execute(
					"""
					INSERT INTO variables (name, value, type, owner, dirty, updated_at)
					VALUES (?, ?, ?, ?, 0, ?)
					ON CONFLICT(name) DO UPDATE SET
						value = excluded.value,
						type = excluded.type,
						owner = excluded.owner,
						dirty = 0,
						updated_at = excluded.updated_at
					""",
					(name, str(value), int(value_type), str(owner), time.time())
				)


_global_flush_thread = None
_global_flush_thread_lock = threading.Lock()


def _flush_global_cache_to_database():
	cache = _BrainGlobalCache()
	db = Database()

	for v_name, v_value, v_type, v_owner, _dirty in cache.dirty_entries():
		try:
			v_list = db.get_entries(
				_GLOBAL_VARIABLE_TABLE,
				columns=_GLOBAL_VARIABLE_COLUMNS,
				conditions={"name": v_name}
			)

			if len(v_list) == 0:
				db.add_entry(_GLOBAL_VARIABLE_TABLE, [v_name, v_value, v_type, v_owner])
			else:
				v_db_owner = str(v_list[0][3])
				if v_db_owner != str(v_owner):
					continue

				db.edit_entry(
					_GLOBAL_VARIABLE_TABLE,
					entry={"value": v_value, "type": v_type},
					conditions={"name": v_name}
				)
		except Exception:
			continue

		cache.mark_clean(v_name)


def _schedule_global_cache_flush():
	global _global_flush_thread

	with _global_flush_thread_lock:
		if _global_flush_thread is not None and _global_flush_thread.is_alive():
			return

		_global_flush_thread = threading.Thread(target=_flush_global_cache_to_database, daemon=True)
		_global_flush_thread.start()



def _user_cache_path():
	return os.environ.get(_USER_CACHE_ENV, _DEFAULT_USER_CACHE_PATH)

def _user_cache_lock_path():
	return f"{_user_cache_path()}.lock"

@contextmanager
def _bxe_user_execution_lock():
	lock_path = _user_cache_lock_path()
	lock_dir = os.path.dirname(lock_path)
	if lock_dir:
		os.makedirs(lock_dir, exist_ok=True)

	with open(lock_path, "a") as lock_file:
		if fcntl is not None:
			fcntl.flock(lock_file, fcntl.LOCK_EX)

		try:
			yield
		finally:
			if fcntl is not None:
				fcntl.flock(lock_file, fcntl.LOCK_UN)


class _BrainUserCache:
	def __init__(self, path=None):
		self._path = path or _user_cache_path()
		self._ensure_cache()

	def _connect(self):
		cache_dir = os.path.dirname(self._path)
		if cache_dir:
			os.makedirs(cache_dir, exist_ok=True)
		return sqlite3.connect(self._path, timeout=30)

	def _ensure_cache(self):
		with self._connect() as cache:
			cache.execute(
				"""
				CREATE TABLE IF NOT EXISTS variables (
					name TEXT PRIMARY KEY,
					value TEXT NOT NULL,
					type INTEGER NOT NULL,
					owner TEXT NOT NULL,
					dirty INTEGER NOT NULL DEFAULT 0,
					updated_at REAL NOT NULL
				)
				"""
			)

	def get(self, name, user):
		with self._connect() as cache:
			row = cache.execute(
				"SELECT name, value, type, owner, dirty FROM variables WHERE name = ?",
				(str(name)+":"+str(user),)
			).fetchone()
		return row

	def get_author(self, name):
		with self._connect() as cache:
			row = cache.execute(
				"SELECT owner FROM variables WHERE name LIKE ?",
				(str(name)+":%",)
			).fetchone()
		return row

	def list_user_ids(self, name):
		with self._connect() as cache:
			rows = cache.execute(
				"SELECT name FROM variables WHERE name LIKE ?",
				(str(name)+":%",)
			).fetchall()

		users = []
		for (full_name,) in rows:
			parts = str(full_name).split(":", 1)
			if len(parts) == 2:
				users.append(parts[1])
		return users

	def get_many(self, names, user):
		if len(names) == 0:
			return {}

		placeholders = ", ".join(["?"] * len(names))
		with self._connect() as cache:
			rows = cache.execute(
				f"SELECT name, value, type, owner, dirty FROM variables WHERE name IN ({placeholders})",
				[name + ":" + str(user) for name in names]
			).fetchall()
		return {row[0]: row for row in rows}

	def dirty_entries(self):
		with self._connect() as cache:
			return cache.execute(
				"SELECT name, value, type, owner, dirty FROM variables WHERE dirty = 1"
			).fetchall()

	def upsert(self, name, value, value_type, owner, dirty):
		with self._connect() as cache:
			cache.execute(
				"""
				INSERT INTO variables (name, value, type, owner, dirty, updated_at)
				VALUES (?, ?, ?, ?, ?, ?)
				ON CONFLICT(name) DO UPDATE SET
					value = excluded.value,
					type = excluded.type,
					owner = excluded.owner,
					dirty = excluded.dirty,
					updated_at = excluded.updated_at
				""",
				(str(name), str(value), int(value_type), str(owner), int(dirty), time.time())
			)

	def mark_clean(self, name):
		with self._connect() as cache:
			cache.execute(
				"UPDATE variables SET dirty = 0, updated_at = ? WHERE name = ?",
				(time.time(), name)
			)

	def refresh_from_database_rows(self, rows):
		with self._connect() as cache:
			for name, value, value_type, owner in rows:
				existing = cache.execute(
					"SELECT dirty FROM variables WHERE name = ?",
					(name,)
				).fetchone()
				if existing is not None and existing[0]:
					continue

				cache.execute(
					"""
					INSERT INTO variables (name, value, type, owner, dirty, updated_at)
					VALUES (?, ?, ?, ?, 0, ?)
					ON CONFLICT(name) DO UPDATE SET
						value = excluded.value,
						type = excluded.type,
						owner = excluded.owner,
						dirty = 0,
						updated_at = excluded.updated_at
					""",
					(name, str(value), int(value_type), str(owner), time.time())
				)


_user_flush_thread = None
_user_flush_thread_lock = threading.Lock()


def _flush_user_cache_to_database():
	cache = _BrainUserCache()
	db = Database()

	for v_name, v_value, v_type, v_owner, _dirty in cache.dirty_entries():
		try:
			v_list = db.get_entries(
				_USER_VARIABLE_TABLE,
				columns=_USER_VARIABLE_COLUMNS,
				conditions={"name": v_name}
			)

			if len(v_list) == 0:
				db.add_entry(_USER_VARIABLE_TABLE, [v_name, v_value, v_type, v_owner])
			else:
				v_db_owner = str(v_list[0][3])
				if v_db_owner != str(v_owner):
					continue

				db.edit_entry(
					_USER_VARIABLE_TABLE,
					entry={"value": v_value, "type": v_type},
					conditions={"name": v_name}
				)
		except Exception:
			continue

		cache.mark_clean(v_name)


def _schedule_user_cache_flush():
	global _user_flush_thread

	with _user_flush_thread_lock:
		if _user_flush_thread is not None and _user_flush_thread.is_alive():
			return

		_user_flush_thread = threading.Thread(target=_flush_user_cache_to_database, daemon=True)
		_user_flush_thread.start()


class BrainDiscordExtension(BxeStatefulExtension):
	_bpp_function_category = "Discord"

	def __init__(self, runner, channel):
		self._runner = runner
		self._channel = channel
		self.buttons = []

	@bpp_function()
	def USERNAME(self):
		"""Get the username of the user running the tag.
		@returns the runner's username"""
		return self._runner.name

	@bpp_function()
	def USERID(self):
		"""Get the Discord ID of the user running the tag.
		@returns the runner's ID"""
		return self._runner.id

	@bpp_function()
	def CHANNEL(self):
		"""Get the ID of the channel the tag was run in.
		@returns the channel ID"""
		return self._channel.id

	@bpp_function()
	def GUILD(self):
		"""Get the ID of the server the tag was run in.
		@returns the server ID"""
		if self._channel.guild:
			return self._channel.guild.id
		else:
			return 0
			
	@bpp_function()
	def BUTTON(self, *args):
		"""Create a button that can be pressed to rerun the tag with special arguments.
		@parameter args a string containing the arguments to run the tag with; if it's the string "null", disables the button
		@parameter label the label of the button
		@optional color the button color/style (`gray`, `blue`, `green`, or `red`)
		@optional locked whether the button is locked to only the current runner (`true`/`false`)
		@returns nothing"""
		self.buttons.append([str(a) for a in args])
		return ""


class BrainGlobalExtension(BxeStatefulExtension):
	_bpp_function_category = "Global Variables"

	def __init__(self, author):
		self._author = str(author)
		self._db = Database()
		self._cache = _BrainGlobalCache()
		_schedule_global_cache_flush()
		self.global_variables = {}
		self._changed = set()

	def post_parse_hook(self, nodes):
		names = self._collect_trivial_global_var_reads(nodes)
		if len(names) == 0:
			return

		rows_by_name = self._cache.get_many(names)
		missing_names = names - set(rows_by_name.keys())

		for missing_name in missing_names:
			try:
				v_list = self._db.get_entries(
					_GLOBAL_VARIABLE_TABLE,
					columns=_GLOBAL_VARIABLE_COLUMNS,
					conditions={"name": missing_name}
				)
			except Exception:
				continue

			if len(v_list) == 0:
				continue

			self._cache.refresh_from_database_rows(v_list)
			rows_by_name[missing_name] = v_list[0]

		for v_name in names:
			row = rows_by_name.get(v_name)
			if row is None:
				continue

			(_, v_value, v_type, *_rest) = row
			self.global_variables[v_name] = _decode_global_value(v_value, v_type)

	@staticmethod
	def _collect_trivial_global_var_reads(nodes):
		names = set()
		stack = list(nodes)

		while len(stack) != 0:
			node = stack.pop()
			if isinstance(node, Nodes.Function):
				if (
					node.name.upper() == "GLOBAL"
					and len(node.arguments) == 2
					and isinstance(node.arguments[0], Nodes.StringNode)
					and isinstance(node.arguments[1], Nodes.StringNode)
					and node.arguments[0].value.lower() == "var"
				):
					names.add(node.arguments[1].value)
				stack.extend(node.arguments)

		return names

	@bpp_function("GLOBAL")
	def global_fn(self, func_type: str, variable: str, value: Any = None):
		"""Works with global variables, variables that persist between tag runs.
		The creator of a global variable becomes its owner, and from then on only the owner and their tags may modify it. However, anybody may access the value of the variable.
		**GLOBAL DEFINE**: Defines or sets a global variable `v` to `s`.
		**GLOBAL VAR**: Gets the value of the global variable `s`.
		@parameter s the global variable to be accessed
		@parameter v (DEFINE) the value to set `s` to
		@returns (DEFINE) nothing
		@returns (VAR) the value of `s`"""
		if re.search(r"[^A-Za-z_0-9]", variable) or re.search(r"[0-9]", variable[0]):
			raise NameError(
			f"Global variable name must be only letters, underscores and numbers, and cannot start with a number")
		match str(func_type).lower():
			case "define":
				if len(str(value)) > 100_000:
					raise ValueError("Global variables are capped at 100,000 characters or fewer")
				self.global_variables[variable] = value
				self._changed.add(variable)
				return ""
			case "var":
				if value:
					raise BxeRuntimeSyntaxException("GLOBAL VAR expected 2 parameters, but got 3")
				if variable in self.global_variables.keys():
					return self.global_variables[variable]

				row = self._cache.get(variable)
				if row is not None:
					(_, v_value, v_type, _v_owner, _dirty) = row
				else:
					v_list = self._db.get_entries(
						_GLOBAL_VARIABLE_TABLE,
						columns=_GLOBAL_VARIABLE_COLUMNS,
						conditions={"name": variable}
					)
					if len(v_list) == 0:
						raise NameError(f"No global variable by the name {variable} defined")

					(_, v_value, v_type, _v_owner) = v_list[0]
					self._cache.refresh_from_database_rows(v_list)

				decoded = _decode_global_value(v_value, v_type)
				self.global_variables[variable] = decoded
				return decoded
			case _:
				raise BxeRuntimeSyntaxException("GLOBAL needs a function type parameter")

	def _flush_cached_changes(self):
		for v_name, v_value, v_type, v_owner, _dirty in self._cache.dirty_entries():
			try:
				self._write_variable_to_database(v_name, v_value, v_type, v_owner)
			except Exception:
				continue
			self._cache.mark_clean(v_name)

	def _write_variable_to_database(self, variable, value_string, value_type, owner):
		v_list = self._db.get_entries(
			_GLOBAL_VARIABLE_TABLE,
			columns=_GLOBAL_VARIABLE_COLUMNS,
			conditions={"name": variable}
		)

		if len(v_list) == 0:
			self._db.add_entry(_GLOBAL_VARIABLE_TABLE, [variable, value_string, value_type, owner])
			return

		v_owner = str(v_list[0][3])
		if v_owner != str(owner):
			raise PermissionError(
				f"Only the author of the {variable} variable can edit its value ({v_owner})"
			)

		self._db.edit_entry(
			_GLOBAL_VARIABLE_TABLE,
			entry={"value": value_string, "type": value_type},
			conditions={"name": variable}
		)

	def persist(self):
		for variable in self._changed:
			value = self.global_variables[variable]
			value_type = _var_type(value)
			value_string = _encode_global_value(value)

			cached = self._cache.get(variable)
			if cached is None:
				v_list = self._db.get_entries(
					_GLOBAL_VARIABLE_TABLE,
					columns=_GLOBAL_VARIABLE_COLUMNS,
					conditions={"name": variable}
				)
				if len(v_list) != 0:
					self._cache.refresh_from_database_rows(v_list)
					cached = self._cache.get(variable)

			if cached is not None and str(cached[3]) != self._author:
				raise PermissionError(
					f"Only the author of the {variable} variable can edit its value ({cached[3]})"
				)

			self._cache.upsert(variable, value_string, value_type, self._author, dirty=True)

		_schedule_global_cache_flush()


def _global_extension_factory(author):
	class RuntimeGlobalExtension(BrainGlobalExtension):
		def __init__(self):
			super().__init__(author)
	return RuntimeGlobalExtension


class BrainUserExtension(BxeStatefulExtension):
	_bpp_function_category = "User Variables"

	def __init__(self, author, runner):
		self._author = str(author)
		self._runner_id = str(runner.id)
		self._db = Database()
		self._cache = _BrainUserCache()
		_schedule_user_cache_flush()
		self.user_variables = {}
		self._changed = set()
		self._user_list_cache_warmed = set()

	def post_parse_hook(self, nodes):
		names = self._collect_trivial_user_var_reads(nodes)
		if len(names) == 0:
			return

		rows_by_name = self._cache.get_many(names, self._runner_id)
		missing_names = names - set(rows_by_name.keys())

		for missing_name in missing_names:
			name_with_id = missing_name+":"+self._runner_id
			try:
				v_list = self._db.get_entries(
					_USER_VARIABLE_TABLE,
					columns=_USER_VARIABLE_COLUMNS,
					conditions={"name": name_with_id}
				)
			except Exception:
				continue

			if len(v_list) == 0:
				continue

			self._cache.refresh_from_database_rows(v_list)
			rows_by_name[name_with_id] = v_list[0]

		for v_name in names:
			name_with_id = v_name+":"+self._runner_id
			row = rows_by_name.get(name_with_id)
			if row is None:
				continue

			(_, v_value, v_type, *_rest) = row
			self.user_variables[v_name] = _decode_global_value(v_value, v_type)

	@staticmethod
	def _collect_trivial_user_var_reads(nodes):
		names = set()
		stack = list(nodes)

		while len(stack) != 0:
			node = stack.pop()
			if isinstance(node, Nodes.Function):
				if (
					node.name.upper() == "USER"
					and len(node.arguments) == 2
					and isinstance(node.arguments[0], Nodes.StringNode)
					and isinstance(node.arguments[1], Nodes.StringNode)
					and node.arguments[0].value.lower() == "var"
				):
					names.add(node.arguments[1].value)
				stack.extend(node.arguments)

		return names

	@bpp_function("USER")
	def user_fn(self, func_type: str, variable: str, value: Any = None, user: Any = None):
		"""Works with user variables, variables that persist between tag runs and are unique to each user.
		The creator of a user variable becomes its owner, and from then on only the owner and their tags may modify it. However, anybody may access the value of the variable.
		**USER DEFINE**: Defines or sets a user variable `v` to `s`. Changes the runner's instance by default, but if another user has already created an instance, `id` can be used to change theirs.
		**USER VAR**: Gets the value of the user variable `s`. Gets the runner's instance by default, but `id` can be used to get a different user's instance.
		**USER LIST**: Gets a list of user IDs that have an instance of the user variable `s`.
		@parameter s the user variable to be accessed
		@parameter v (DEFINE) the value to set `s` to
		@optional id the user ID of a user that has defined an instance of the variable
		@returns (DEFINE) nothing
		@returns (VAR) the value of `s`
		@returns (LIST) a list of user IDs that have `s` defined"""
		if re.search(r"[^A-Za-z_0-9]", variable) or re.search(r"[0-9]", variable[0]):
			raise NameError(
			f"User variable name must be only letters, underscores and numbers, and cannot start with a number")

		target_user = self._runner_id if user is None else str(user)
		db_name = variable + ":" + target_user
		match str(func_type).lower():
			case "define":
				if len(str(value)) > 10_000:
					raise ValueError("User variables are capped at 10,000 characters or fewer")

				if user is not None:
					existing = self._cache.get(variable, target_user)
					if existing is None:
						v_list = self._db.get_entries(
							_USER_VARIABLE_TABLE,
							columns=_USER_VARIABLE_COLUMNS,
							conditions={"name": db_name}
						)
						if len(v_list) == 0:
							raise NameError(f"The user with id {user} does not have {variable} defined, so you cannot set it.")

						self._cache.refresh_from_database_rows(v_list)

				self.user_variables[db_name] = value
				self._changed.add(db_name)
				return ""
			case "var":
				if value:
					db_name = variable + ":" + str(value)
				if db_name in self.user_variables.keys():
					return self.user_variables[db_name]

				row = self._cache.get(variable, str(value or self._runner_id))
				if row is not None:
					(_, v_value, v_type, _v_owner, _dirty) = row
				else:
					v_list = self._db.get_entries(
						_USER_VARIABLE_TABLE,
						columns=_USER_VARIABLE_COLUMNS,
						conditions={"name": db_name}
					)
					if len(v_list) == 0:
						raise NameError(f"This user does not have {variable} defined")

					(_, v_value, v_type, _v_owner) = v_list[0]
					self._cache.refresh_from_database_rows(v_list)

				decoded = _decode_global_value(v_value, v_type)
				self.user_variables[db_name] = decoded
				return decoded
			case "list":
				if value is not None or user is not None:
					raise BxeRuntimeSyntaxException("USER LIST expected 2 parameters, but got more")

				users = set()
				for user_id in self._cache.list_user_ids(variable):
					users.add(str(user_id))

				if variable not in self._user_list_cache_warmed:
					v_list = self._db.get_entries(
						_USER_VARIABLE_TABLE,
						columns=_USER_VARIABLE_COLUMNS,
						patterns={"name": variable.replace("_", r"\_")+":%"}
					)
					if len(v_list) != 0:
						self._cache.refresh_from_database_rows(v_list)

					for db_name, *_ in v_list:
						parts = str(db_name).split(":", 1)
						if len(parts) == 2:
							users.add(parts[1])
					self._user_list_cache_warmed.add(variable)

				for local_name in self.user_variables.keys():
					parts = str(local_name).split(":", 1)
					if len(parts) == 2 and parts[0] == variable:
						users.add(parts[1])

				return sorted(users)
			case _:
				raise BxeRuntimeSyntaxException("USER needs a function type parameter")

	def _flush_cached_changes(self):
		for v_name, v_value, v_type, v_owner, _dirty in self._cache.dirty_entries():
			try:
				self._write_variable_to_database(v_name, v_value, v_type, v_owner)
			except Exception:
				continue
			self._cache.mark_clean(v_name)

	def _write_variable_to_database(self, variable, value_string, value_type, owner):
		v_list = self._db.get_entries(
			_USER_VARIABLE_TABLE,
			columns=_USER_VARIABLE_COLUMNS,
			patterns={"name": variable.split(":")[0].replace("_","\_")+":%"}
		)
		if len(v_list) == 0:
			self._db.add_entry(_USER_VARIABLE_TABLE, [variable, value_string, value_type, owner])
			return

		v_owner = str(v_list[0][3])
		if v_owner != str(owner):
			raise PermissionError(
				f"Only the author of the {variable} variable can edit its value ({v_owner})"
			)

		if variable in [x[0] for x in v_list]:
			self._db.edit_entry(
				_USER_VARIABLE_TABLE,
				entry={"value": value_string, "type": value_type},
				conditions={"name": variable}
			)
		else:
			self._db.add_entry(_USER_VARIABLE_TABLE, [variable, value_string, value_type, owner])

	def persist(self):
		for variable in self._changed:
			value = self.user_variables[variable]
			value_type = _var_type(value)
			value_string = _encode_global_value(value)

			varname, username = variable.split(":")
			cached = self._cache.get(varname, username)

			if cached is None:
				v_list = self._db.get_entries(
					_USER_VARIABLE_TABLE,
					columns=_USER_VARIABLE_COLUMNS,
					patterns={"name": variable.split(":")[0].replace("_","\_")+":%"}
				)
				if len(v_list) != 0:
					self._cache.refresh_from_database_rows(v_list)
					cached = self._cache.get(varname, username)

			author = self._cache.get_author(varname)
			if author: author = author[0]

			if (author is not None and author != self._author) or (cached is not None and str(cached[3]) != self._author):
				raise PermissionError(
					f"Only the author of the {varname} user variable can edit its value ({author or cached[3]})"
				)

			self._cache.upsert(variable, value_string, value_type, self._author, dirty=True)

		_schedule_user_cache_flush()


def _user_extension_factory(author, runner):
	class RuntimeUserExtension(BrainUserExtension):
		def __init__(self):
			super().__init__(author, runner)
	return RuntimeUserExtension


def _discord_extension_factory(runner, channel):
	class RuntimeDiscordExtension(BrainDiscordExtension):
		def __init__(self):
			super().__init__(runner, channel)
	return RuntimeDiscordExtension

docs_extensions = [BuiltinExtension, BrainDiscordExtension, BrainGlobalExtension, BrainUserExtension]

def get_ext_docs():
	funcs = {}
	for ext in docs_extensions:
		docs = get_docs(ext)
		for f in docs:
			funcs[f] = docs[f]
	return funcs

def format_doc(name, doc: FunctionDoc):
	if not doc:
		return None

	parsed = parse_docstring(doc.raw_doc)

	title = name
	if doc.is_alias:
		title = f"{name} (alias of {doc.primary_name})"

	description_parts = [f"`{doc.signature}`"]
	if doc.is_alias:
		description_parts.append(f"`{name}` is an alias for `{doc.primary_name}`.")
	if parsed.summary:
		description_parts.append("\n".join(parsed.summary))

	fields: list[dict] = []
	fields.append({"name": "**Category**", "value": doc.category})
	visible_aliases = [alias for alias in doc.aliases if alias != name]
	if visible_aliases:
		fields.append({"name": "**Aliases**", "value": ", ".join(f"`{alias}`" for alias in visible_aliases)})
	if parsed.parameters or parsed.optional_parameters:
		separator = "\n" if (parsed.parameters and parsed.optional_parameters) else ""
		fields.append({
			"name": "**Parameters**",
			"value": "\n".join(
				f"- `{name}`: {desc}" if desc else f"- `{name}`"
				for name, desc in parsed.parameters
			)
			+ separator
			+ "\n".join(
				f"- `{name}`?: {desc}" if desc else f"- `{name}`"
				for name, desc in parsed.optional_parameters
			)
		})
	if parsed.returns:
		fields.append({"name": "**Returns**", "value": "\n".join(f"- {item}" for item in parsed.returns)})
	if parsed.raises:
		fields.append({"name": "**Raises**", "value": "\n".join(f"- {item}" for item in parsed.raises)})
	if parsed.examples:
		fields.append({"name": "**Examples**", "value": "\n".join(f"- `{item}`" for item in parsed.examples)})
	if parsed.notes:
		fields.append({"name": "**Notes**", "value": "\n".join(f"- {item}" for item in parsed.notes)})

	return {"title": title, "description": "\n".join(description_parts), "fields": fields}

def _run_bxe_program_unlocked(code, p_args, author, runner, channel):
	buttons = []
	warnings = []
	try:
		tok = Tokenizer.tokenize(code)
		if isinstance(tok, TokenizationResult.Error):
			return [SyntaxError(f"{tok.message}\n\n{tok.range.debug_info()}"), buttons, warnings]
		warnings.extend(tok.warnings)

		par = Parser.parse(code, tok.tokens)
		if isinstance(par, ParsingResult.Error):
			warnings.extend(par.warnings)
			return [SyntaxError(f"{par.message}\n\n{par.range.debug_info()}"), buttons, warnings]
		warnings.extend(par.warnings)

		exe = Executor(
			extensions=[BuiltinExtension()],
			stateful_extensions=[
				_global_extension_factory(author),
				_user_extension_factory(author, runner),
				_discord_extension_factory(runner, channel),
			],
			program_args=p_args
		)

		result = exe.execute(par.nodes)
		if isinstance(result, ExecutorResult.Error):
			exc = result.exception
			span = getattr(exc, "span", None)
			if span is not None and not isinstance(exc, ProgramDefinedException):
				try:
					exc = type(exc)(f"{exc}\n\n{span.debug_info()}")
				except Exception:
					pass
			return [exc, buttons, warnings]

		for ext in result.stateful_extensions:
			if isinstance(ext, BrainGlobalExtension):
				ext.persist()
			elif isinstance(ext, BrainUserExtension):
				ext.persist()
			elif isinstance(ext, BrainDiscordExtension):
				buttons = ext.buttons

		return [result.output, buttons, warnings]
	except Exception as e:
		return [e, buttons, warnings]


def run_bxe_program(code, p_args, author, runner, channel):
	buttons = []
	warnings = []
	try:
		with _bxe_global_execution_lock():
			with _bxe_user_execution_lock():
				return _run_bxe_program_unlocked(code, p_args, author, runner, channel)
	except Exception as e:
		return [e, buttons, warnings]
