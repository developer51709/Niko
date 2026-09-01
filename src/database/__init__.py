import json
import os
import re
from datetime import datetime, timezone
from typing import Optional, Union

import aiosqlite

DATETIME_COLUMNS = {"adopted_at"}
LIST_COLUMNS = {"roles"}


def _convert_query(query: str) -> str:
    return re.sub(r"\$\d+", "?", query)


def _serialize_args(args):
    out = []
    for arg in args:
        if isinstance(arg, list):
            out.append(json.dumps(arg))
        else:
            out.append(arg)
    return out


class Row(dict):
    def __getitem__(self, key):
        value = super().__getitem__(key)
        if key in LIST_COLUMNS:
            if isinstance(value, str):
                try:
                    return json.loads(value)
                except Exception:
                    return []
            return value if value is not None else []
        if key in DATETIME_COLUMNS:
            if isinstance(value, str):
                try:
                    dt = datetime.fromisoformat(value)
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=timezone.utc)
                    return dt
                except Exception:
                    pass
        return value

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default


def _make_row(cursor, raw_row):
    if raw_row is None:
        return None
    columns = [desc[0] for desc in cursor.description]
    return Row(zip(columns, raw_row))


class SQLitePool:
    def __init__(self, db: aiosqlite.Connection):
        self._db = db
        self.db_type = "sqlite"

    async def execute(self, query: str, *args):
        q = _convert_query(query)
        a = _serialize_args(args)
        await self._db.execute(q, a)
        await self._db.commit()

    async def fetchrow(self, query: str, *args):
        q = _convert_query(query)
        a = _serialize_args(args)
        async with self._db.execute(q, a) as cursor:
            raw = await cursor.fetchone()
            return _make_row(cursor, raw)

    async def fetch(self, query: str, *args):
        q = _convert_query(query)
        a = _serialize_args(args)
        async with self._db.execute(q, a) as cursor:
            rows = await cursor.fetchall()
            return [_make_row(cursor, r) for r in rows]

    async def fetchval(self, query: str, *args):
        q = _convert_query(query)
        a = _serialize_args(args)
        async with self._db.execute(q, a) as cursor:
            raw = await cursor.fetchone()
            if raw is None:
                return None
            return raw[0]

    async def fetchone(self, query: str, *args):
        return await self.fetchrow(query, *args)


class MongoPool:
    def __init__(self, client, db_name: str):
        self._client = client
        self._db = client[db_name]
        self.db_type = "mongodb"

    async def execute(self, query: str, *args):
        """Execute a SQL-like query by translating it to MongoDB operations."""
        query = query.strip()
        
        # Handle CREATE TABLE
        if query.upper().startswith("CREATE TABLE"):
            # MongoDB doesn't need explicit table creation
            # Collections are created automatically
            return
        
        # Handle ALTER TABLE
        if query.upper().startswith("ALTER TABLE"):
            # MongoDB is schema-less, no ALTER needed
            return
        
        # Handle INSERT OR REPLACE
        if "INSERT OR REPLACE" in query.upper() or "REPLACE INTO" in query.upper():
            return await self._handle_insert_or_replace(query, args)

        # Handle INSERT ... SELECT
        if "INSERT" in query.upper() and "SELECT" in query.upper():
            return await self._handle_insert_select(query, args)

        # Handle INSERT OR IGNORE
        if query.upper().startswith("INSERT OR IGNORE"):
            return await self._handle_insert_ignore(query, args)
        
        # Handle regular INSERT
        if query.upper().startswith("INSERT"):
            return await self._handle_insert(query, args)
        
        # Handle UPDATE
        if query.upper().startswith("UPDATE"):
            return await self._handle_update(query, args)
        
        # Handle DELETE
        if query.upper().startswith("DELETE"):
            return await self._handle_delete(query, args)
        
        raise NotImplementedError(f"MongoDB does not support this SQL query: {query[:50]}...")

    async def fetchrow(self, query: str, *args):
        """Fetch a single row by translating SQL to MongoDB."""
        query = query.strip()
        
        if query.upper().startswith("SELECT"):
            return await self._handle_select_one(query, args)
        
        raise NotImplementedError(f"MongoDB does not support this SQL query: {query[:50]}...")

    async def fetch(self, query: str, *args):
        """Fetch multiple rows by translating SQL to MongoDB."""
        query = query.strip()
        
        if query.upper().startswith("SELECT"):
            return await self._handle_select_many(query, args)
        
        raise NotImplementedError(f"MongoDB does not support this SQL query: {query[:50]}...")

    async def fetchval(self, query: str, *args):
        """Fetch a single value by translating SQL to MongoDB."""
        row = await self.fetchrow(query, *args)
        if row:
            return list(row.values())[0] if row else None
        return None

    async def fetchone(self, query: str, *args):
        return await self.fetchrow(query, *args)

    def _parse_select_query(self, query: str, args: tuple) -> tuple:
        """Parse SELECT query to extract table, columns, and conditions."""
        # Simple parser for the queries used in this codebase
        import re
        
        # Remove newlines and extra spaces, and normalize parameter placeholders
        query = re.sub(r'\s+', ' ', query).strip()
        query = re.sub(r'\$\d+', '?', query)
        
        # Extract columns
        match = re.match(r'SELECT\s+(.+?)\s+FROM\s+(\w+)', query, re.IGNORECASE)
        if not match:
            raise ValueError(f"Cannot parse SELECT query: {query}")
        
        columns = match.group(1).strip()
        table = match.group(2).strip()
        
        # Extract WHERE clause
        where_match = re.search(r'WHERE\s+(.+?)(?:\s+GROUP BY|\s+ORDER BY|\s+LIMIT|$)', query, re.IGNORECASE)
        where_clause = where_match.group(1).strip() if where_match else None
        
        # Extract LIMIT
        limit_match = re.search(r'LIMIT\s+(\d+)', query, re.IGNORECASE)
        limit = int(limit_match.group(1)) if limit_match else None
        
        return table, columns, where_clause, limit, args

    def _parse_update_query(self, query: str, args: tuple) -> tuple:
        """Parse UPDATE query to extract table, set values, and conditions."""
        import re
        
        query = re.sub(r'\s+', ' ', query).strip()
        query = re.sub(r'\$\d+', '?', query)
        
        match = re.match(r'UPDATE\s+(\w+)\s+SET\s+(.+?)\s+WHERE\s+(.+)', query, re.IGNORECASE)
        if not match:
            raise ValueError(f"Cannot parse UPDATE query: {query}")
        
        table = match.group(1).strip()
        set_clause = match.group(2).strip()
        where_clause = match.group(3).strip()
        
        return table, set_clause, where_clause, args

    def _parse_insert_query(self, query: str, args: tuple) -> tuple:
        """Parse INSERT query to extract table and values."""
        import re
        
        query = re.sub(r'\s+', ' ', query).strip()
        query = re.sub(r'\$\d+', '?', query)
        
        # Try INSERT OR REPLACE first
        match = re.match(r'INSERT\s+OR\s+REPLACE\s+INTO\s+(\w+)\s+\((.+?)\)\s+VALUES\s+\((.+?)\)', query, re.IGNORECASE)
        if not match:
            match = re.match(r'REPLACE\s+INTO\s+(\w+)\s+\((.+?)\)\s+VALUES\s+\((.+?)\)', query, re.IGNORECASE)
        
        # Try regular INSERT
        if not match:
            match = re.match(r'INSERT\s+INTO\s+(\w+)\s+\((.+?)\)\s+VALUES\s+\((.+?)\)', query, re.IGNORECASE)
        
        if not match:
            raise ValueError(f"Cannot parse INSERT query: {query}")
        
        table = match.group(1).strip()
        columns = [col.strip() for col in match.group(2).split(',')]
        # Values are passed as args, not in the query string
        
        return table, columns, args

    def _build_mongo_filter(self, where_clause: str, args: tuple) -> dict:
        """Build MongoDB filter from SQL WHERE clause."""
        if not where_clause:
            return {}
        
        import re
        
        # Normalize parameter placeholders to a single format
        normalized_clause = re.sub(r'\$\d+', '?', where_clause)
        
        # Handle simple equality: user_id = ? or user_id = $1
        match = re.match(r'(\w+)\s*=\s*\?', normalized_clause.strip())
        if match:
            return {match.group(1): args[0]}
        
        # Handle inequality: lottery_tickets > 0
        match = re.match(r'(\w+)\s*>\s*(\d+)', normalized_clause.strip())
        if match:
            return {match.group(1): {"$gt": int(match.group(2))}}
        
        # Handle inequality with parameter: lottery_tickets > ?
        match = re.match(r'(\w+)\s*>\s*\?', normalized_clause.strip())
        if match:
            return {match.group(1): {"$gt": args[0]}}
        
        # Handle ended = 0 (boolean check)
        match = re.match(r'(\w+)\s*=\s*(\d+)', normalized_clause.strip())
        if match:
            return {match.group(1): int(match.group(2))}

        # Handle IS NOT NULL
        match = re.match(r'(\w+)\s+IS\s+NOT\s+NULL', normalized_clause.strip(), re.IGNORECASE)
        if match:
            return {match.group(1): {"$ne": None}}

        # Handle IS NULL
        match = re.match(r'(\w+)\s+IS\s+NULL', normalized_clause.strip(), re.IGNORECASE)
        if match:
            return {match.group(1): None}
        
        # Handle complex conditions with AND
        if ' AND ' in normalized_clause.upper():
            conditions = normalized_clause.split(' AND ')
            filter_dict = {}
            arg_index = 0
            for cond in conditions:
                cond = cond.strip()
                match = re.match(r'(\w+)\s*=\s*\?', cond)
                if match:
                    filter_dict[match.group(1)] = args[arg_index]
                    arg_index += 1
                else:
                    match = re.match(r'(\w+)\s*=\s*(\d+)', cond)
                    if match:
                        filter_dict[match.group(1)] = int(match.group(2))
            return filter_dict
        
        raise ValueError(f"Cannot parse WHERE clause: {where_clause}")

    def _build_mongo_update(self, set_clause: str, args: tuple) -> dict:
        """Build MongoDB update document from SQL SET clause."""
        import re
        
        # Normalize parameter placeholders
        normalized_clause = re.sub(r'\$\d+', '?', set_clause)
        
        # Parse multiple assignments: col1 = ?, col2 = ?, ...
        assignments = [a.strip() for a in normalized_clause.split(',')]
        update_dict = {}
        arg_index = 0
        
        for assignment in assignments:
            match = re.match(r'(\w+)\s*=\s*\?', assignment)
            if match:
                update_dict[match.group(1)] = args[arg_index]
                arg_index += 1
            else:
                match = re.match(r'(\w+)\s*=\s*(.+)', assignment)
                if match:
                    value = match.group(2).strip()
                    if value.isdigit():
                        update_dict[match.group(1)] = int(value)
                    else:
                        update_dict[match.group(1)] = value
        
        return {"$set": update_dict}

    async def _handle_select_one(self, query: str, args: tuple) -> Row:
        """Handle SELECT query that returns one row."""
        table, columns, where_clause, limit, query_args = self._parse_select_query(query, args)
        
        filter_dict = self._build_mongo_filter(where_clause, query_args)
        
        # Special case: handle tables that use 'id' instead of 'user_id' as primary key
        if 'id' in filter_dict and table == 'economy_lottery':
            filter_dict['_id'] = filter_dict.pop('id')
        
        # Special case: handle giveaways table with message_id as primary key
        if 'message_id' in filter_dict and table == 'giveaways':
            filter_dict['_id'] = filter_dict.pop('message_id')
        
        # Special case: handle participants table with composite key
        if table == 'participants' and 'message_id' in filter_dict and 'user_id' in filter_dict:
            filter_dict['_id'] = f"{filter_dict['message_id']}_{filter_dict['user_id']}"
            del filter_dict['message_id']
            del filter_dict['user_id']
        
        collection = self._db[table]
        doc = await collection.find_one(filter_dict)
        
        if doc:
            # Convert _id to user_id if present (for user tables)
            if '_id' in doc and table != 'economy_lottery' and table != 'participants' and table != 'giveaways':
                doc['user_id'] = doc['_id']
            # Convert _id to id for lottery table
            elif '_id' in doc and table == 'economy_lottery':
                doc['id'] = doc['_id']
            # Convert _id to message_id for giveaways table
            elif '_id' in doc and table == 'giveaways':
                doc['message_id'] = doc['_id']
            # Convert _id back to composite key for participants
            elif '_id' in doc and table == 'participants':
                parts = doc['_id'].split('_')
                if len(parts) == 2:
                    doc['message_id'] = int(parts[0])
                    doc['user_id'] = int(parts[1])
            
            # Filter columns if specific columns requested
            if columns != '*':
                cols_list = [c.strip() for c in columns.split(',')]
                doc = {k: v for k, v in doc.items() if k in cols_list or k == '_id'}
            
            return Row(doc)
        return None

    async def _handle_select_many(self, query: str, args: tuple) -> list:
        """Handle SELECT query that returns multiple rows."""
        table, columns, where_clause, limit, query_args = self._parse_select_query(query, args)
        
        filter_dict = self._build_mongo_filter(where_clause, query_args)
        
        # Special case: handle tables that use 'id' instead of 'user_id' as primary key
        if 'id' in filter_dict and table == 'economy_lottery':
            filter_dict['_id'] = filter_dict.pop('id')
        
        # Special case: handle giveaways table with message_id as primary key
        if 'message_id' in filter_dict and table == 'giveaways':
            filter_dict['_id'] = filter_dict.pop('message_id')
        
        # Special case: handle participants table with composite key
        if table == 'participants' and 'message_id' in filter_dict and 'user_id' in filter_dict:
            filter_dict['_id'] = f"{filter_dict['message_id']}_{filter_dict['user_id']}"
            del filter_dict['message_id']
            del filter_dict['user_id']
        elif table == 'participants' and 'message_id' in filter_dict:
            # For queries filtering by message_id only, use regex to match composite keys
            filter_dict['_id'] = {'$regex': f"^{filter_dict['message_id']}_"}
            del filter_dict['message_id']
        
        collection = self._db[table]
        cursor = collection.find(filter_dict)
        
        if limit:
            cursor = cursor.limit(limit)
        
        docs = await cursor.to_list(length=None)
        
        rows = []
        for doc in docs:
            # Convert _id to user_id if present (for user tables)
            if '_id' in doc and table != 'economy_lottery' and table != 'participants' and table != 'giveaways':
                doc['user_id'] = doc['_id']
            # Convert _id to id for lottery table
            elif '_id' in doc and table == 'economy_lottery':
                doc['id'] = doc['_id']
            # Convert _id to message_id for giveaways table
            elif '_id' in doc and table == 'giveaways':
                doc['message_id'] = doc['_id']
            # Convert _id back to composite key for participants
            elif '_id' in doc and table == 'participants':
                parts = doc['_id'].split('_')
                if len(parts) == 2:
                    doc['message_id'] = int(parts[0])
                    doc['user_id'] = int(parts[1])
            
            # Filter columns if specific columns requested
            if columns != '*':
                cols_list = [c.strip() for c in columns.split(',')]
                doc = {k: v for k, v in doc.items() if k in cols_list or k == '_id'}
            
            rows.append(Row(doc))
        
        return rows

    async def _handle_update(self, query: str, args: tuple):
        """Handle UPDATE query."""
        table, set_clause, where_clause, query_args = self._parse_update_query(query, args)
        
        filter_dict = self._build_mongo_filter(where_clause, query_args)
        update_dict = self._build_mongo_update(set_clause, query_args)
        
        # Special case: handle tables that use 'id' instead of 'user_id' as primary key
        if 'id' in filter_dict and table == 'economy_lottery':
            filter_dict['_id'] = filter_dict.pop('id')
        
        # Special case: handle giveaways table with message_id as primary key
        if 'message_id' in filter_dict and table == 'giveaways':
            filter_dict['_id'] = filter_dict.pop('message_id')
        
        # Special case: handle participants table with composite key
        if table == 'participants' and 'message_id' in filter_dict and 'user_id' in filter_dict:
            filter_dict['_id'] = f"{filter_dict['message_id']}_{filter_dict['user_id']}"
            del filter_dict['message_id']
            del filter_dict['user_id']
        
        collection = self._db[table]
        await collection.update_one(filter_dict, update_dict, upsert=True)

    async def _handle_insert_or_replace(self, query: str, args: tuple):
        """Handle INSERT OR REPLACE query."""
        table, columns, query_args = self._parse_insert_query(query, args)
        
        doc = {}
        for i, col in enumerate(columns):
            if i < len(query_args):
                doc[col] = query_args[i]
        
        collection = self._db[table]
        
        # Handle different primary key strategies based on table
        if table == 'participants':
            # Composite key: message_id + user_id
            doc['_id'] = f"{doc.get('message_id')}_{doc.get('user_id')}"
        elif table == 'giveaways':
            # Use message_id as _id
            doc['_id'] = doc.get('message_id')
        elif 'user_id' in doc:
            # Use user_id as _id for user tables
            doc['_id'] = doc['user_id']
        elif 'id' in doc:
            # Use id as _id for tables like lottery
            doc['_id'] = doc['id']
        
        await collection.replace_one({'_id': doc.get('_id')}, doc, upsert=True)

    async def _handle_insert_select(self, query: str, args: tuple):
        """
        Handle SQL:
            INSERT [OR IGNORE] INTO table (col1, col2)
            SELECT colA, colB FROM other WHERE ...
        """

        # Normalize whitespace
        q = " ".join(query.split())

        # Extract target table + columns + SELECT portion
        upper = q.upper()

        # Find INTO
        into_idx = upper.index("INTO") + len("INTO")
        after_into = q[into_idx:].strip()

        # Table name
        table = after_into.split(" ", 1)[0].strip()

        # Column list inside parentheses
        col_start = after_into.index("(")
        col_end = after_into.index(")")
        col_list = after_into[col_start + 1:col_end]
        target_columns = [c.strip() for c in col_list.split(",")]

        # SELECT portion begins after the closing parenthesis
        select_sql = after_into[col_end + 1:].strip()
        if not select_sql.upper().startswith("SELECT"):
            raise ValueError(f"Cannot parse INSERT SELECT query: {query}")

        # Parse SELECT using your existing parser
        sel_table, sel_columns, where_clause, limit, sel_args = self._parse_select_query(select_sql, args)

        # Fetch rows using your existing SELECT handler
        rows = await self._handle_select_many(select_sql, sel_args)

        # Prepare target collection
        collection = self._db[table]
        inserted = 0

        # SELECT column list
        select_cols = [c.strip() for c in sel_columns.split(",")]

        for row in rows:
            doc = {}

            # Build document from SELECT result
            for target_col, select_col in zip(target_columns, select_cols):
                doc[target_col] = row.get(select_col)

            # Apply your existing primary-key rules
            if table == 'participants':
                doc['_id'] = f"{doc.get('message_id')}_{doc.get('user_id')}"
            elif table == 'giveaways':
                doc['_id'] = doc.get('message_id')
            elif 'user_id' in doc:
                doc['_id'] = doc['user_id']
            elif 'id' in doc:
                doc['_id'] = doc['id']

            # OR IGNORE behavior: skip if exists
            if await collection.find_one({'_id': doc.get('_id')}):
                continue

            await collection.insert_one(doc)
            inserted += 1

        return inserted

    async def _handle_insert_ignore(self, query: str, args: tuple):
        """Handle INSERT OR IGNORE INTO ... VALUES (...)"""

        # Strip OR IGNORE so your existing parser works
        cleaned = query.replace("OR IGNORE", "")

        table, columns, query_args = self._parse_insert_query(cleaned, args)

        doc = {}
        for i, col in enumerate(columns):
            if i < len(query_args):
                doc[col] = query_args[i]

        collection = self._db[table]

        # Apply your existing primary-key rules
        if table == 'participants':
            doc['_id'] = f"{doc.get('message_id')}_{doc.get('user_id')}"
        elif table == 'giveaways':
            doc['_id'] = doc.get('message_id')
        elif 'user_id' in doc:
            doc['_id'] = doc['user_id']
        elif 'id' in doc:
            doc['_id'] = doc['id']

        # OR IGNORE behavior: skip if exists
        if await collection.find_one({'_id': doc.get('_id')}):
            return None

        await collection.insert_one(doc)
        return None

    async def _handle_insert(self, query: str, args: tuple):
        """Handle regular INSERT query."""
        table, columns, query_args = self._parse_insert_query(query, args)
        
        doc = {}
        for i, col in enumerate(columns):
            if i < len(query_args):
                doc[col] = query_args[i]
        
        collection = self._db[table]
        
        # Handle different primary key strategies based on table
        if table == 'participants':
            # Composite key: message_id + user_id
            doc['_id'] = f"{doc.get('message_id')}_{doc.get('user_id')}"
        elif table == 'giveaways':
            # Use message_id as _id
            doc['_id'] = doc.get('message_id')
        elif 'user_id' in doc:
            # Use user_id as _id for user tables
            doc['_id'] = doc['user_id']
        elif 'id' in doc:
            # Use id as _id for tables like lottery
            doc['_id'] = doc['id']
        
        await collection.insert_one(doc)

    async def _handle_delete(self, query: str, args: tuple):
        """Handle DELETE query."""
        import re
        
        query = re.sub(r'\s+', ' ', query).strip()
        query = re.sub(r'\$\d+', '?', query)
        
        match = re.match(r'DELETE\s+FROM\s+(\w+)\s+WHERE\s+(.+)', query, re.IGNORECASE)
        if not match:
            raise ValueError(f"Cannot parse DELETE query: {query}")
        
        table = match.group(1).strip()
        where_clause = match.group(2).strip()
        
        filter_dict = self._build_mongo_filter(where_clause, args)
        
        # Special case: handle giveaways table with message_id as primary key
        if 'message_id' in filter_dict and table == 'giveaways':
            filter_dict['_id'] = filter_dict.pop('message_id')
        
        # Special case: handle participants table with composite key
        if table == 'participants' and 'message_id' in filter_dict and 'user_id' in filter_dict:
            filter_dict['_id'] = f"{filter_dict['message_id']}_{filter_dict['user_id']}"
            del filter_dict['message_id']
            del filter_dict['user_id']
        elif table == 'participants' and 'message_id' in filter_dict:
            # For queries filtering by message_id only, use regex to match composite keys
            filter_dict['_id'] = {'$regex': f"^{filter_dict['message_id']}_"}
            del filter_dict['message_id']
        
        collection = self._db[table]
        await collection.delete_many(filter_dict)

    @property
    def client(self):
        return self._client

    @property
    def db(self):
        return self._db


async def create_pool(db_path: str) -> Union[SQLitePool, MongoPool]:
    # Check for MongoDB connection string in environment variables
    mongo_url = os.getenv("MONGODB_URL")
    
    if mongo_url:
        try:
            from motor.motor_asyncio import AsyncIOMotorClient
            
            # Extract database name from URL or use default
            db_name = os.getenv("MONGODB_DATABASE", "discord_bot")
            
            client = AsyncIOMotorClient(mongo_url)
            # Test connection
            await client.admin.command('ping')
            
            return MongoPool(client, db_name)
        except Exception as e:
            print(f"Failed to connect to MongoDB: {e}. Falling back to SQLite.")
    
    # Default to SQLite
    db = await aiosqlite.connect(db_path)
    await db.execute("PRAGMA journal_mode=WAL")
    await db.execute("PRAGMA foreign_keys=ON")
    return SQLitePool(db)
