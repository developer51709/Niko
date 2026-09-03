import json
import os
import re
from datetime import datetime, timezone
from typing import Optional, Union

import aiosqlite

DATETIME_COLUMNS = {"adopted_at"}
LIST_COLUMNS = {"roles"}

# Columns stored as JSON text in SQLite and kept as JSON strings in MongoDB so
# both backends behave identically. The interpreter transparently serialises
# list/dict arguments on write and parses them back on read.
JSON_COLUMNS = {
    "economy_users": ("inventory", "effects", "transactions", "achievements"),
    "level_config": ("level_roles",),
    "giveaways": ("requirements",),
    "ticket_config": ("panel_categories", "support_roles", "open_tickets"),
}


# The live pool is stored here once ``events.startup.database.init_database``
# has run, so modules without a bot reference (e.g. onboarding config helpers)
# can reach the same connection the bot uses.
_shared_pool: Optional[Union["SQLitePool", "MongoPool"]] = None


def _convert_query(query: str) -> str:
    return re.sub(r"\$\d+", "?", query)


def _serialize_args(args):
    out = []
    for arg in args:
        if isinstance(arg, (list, dict)):
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
    """Thin async wrapper around aiosqlite exposing the pool API the bot uses."""

    def __init__(self, db: aiosqlite.Connection):
        self._db = db
        self.db_type = "sqlite"

    async def execute(self, query: str, *args):
        q = _convert_query(query)
        a = _serialize_args(list(args))
        await self._db.execute(q, a)
        await self._db.commit()

    async def fetchrow(self, query: str, *args):
        q = _convert_query(query)
        a = _serialize_args(list(args))
        async with self._db.execute(q, a) as cursor:
            raw = await cursor.fetchone()
            return _make_row(cursor, raw)

    async def fetch(self, query: str, *args):
        q = _convert_query(query)
        a = _serialize_args(list(args))
        async with self._db.execute(q, a) as cursor:
            rows = await cursor.fetchall()
            return [_make_row(cursor, r) for r in rows]

    async def fetchval(self, query: str, *args):
        q = _convert_query(query)
        a = _serialize_args(list(args))
        async with self._db.execute(q, a) as cursor:
            raw = await cursor.fetchone()
            if raw is None:
                return None
            return raw[0]

    async def fetchone(self, query: str, *args):
        return await self.fetchrow(query, *args)


# ─────────────────────────────────────────────────────────────────────────────
#  Primary-key conventions per table. Composite keys become a single "_id"
#  string joined with underscores inside MongoDB.
# ─────────────────────────────────────────────────────────────────────────────
PRIMARY_KEYS: dict = {
    "economy_users": "user_id",
    "economy_lottery": "id",
    "donors": "user_id",
    "levels": ("guild_id", "user_id"),
    "level_config": "guild_id",
    "giveaways": "message_id",
    "participants": ("message_id", "user_id"),
    "triggers": "id",
    "follows": ("guild_id", "platform", "username"),
    "youtube": "channel_id",
    "youtube_history": ("channel_id", "video_id"),
    "voicemaster_settings": "guild_id",
    "voicemaster_channels": "channel_id",
    "onboarding": "guild_id",
    "logging_config": "guild_id",
    "moderation_config": "guild_id",
    "modlog": "guild_id",
    "guild_profiles": "guild_id",
    "donation_invoices": "order_id",
    "transcripts": "transcript_id",
    "ticket_config": "guild_id",
    "sticky_messages": "channel_id",
    "birthday_users": "user_id",
    "birthday_guilds": "guild_id",
    "birthday_state": "key",
    "sync_state": "key",
    "afk_users": "user_id",
    "warns": "id",
    "mutes": "id",
    "blacklist_users": "id",
    "blacklist_guilds": "id",
    "roleplay_actions": "message_id",
    # Dedicated music database (utils.music.database) — same cluster on
    # MongoDB but a separate database, so these tables live in their own pool.
    "music_liked_songs": ("user_id", "track_key"),
    "music_playlists": ("user_id", "name"),
    "music_playlist_tracks": ("user_id", "name", "track_key"),
}


def _typed(value):
    """Best-effort int coercion for values reconstructed from composite _ids."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return value


def _composite_id(doc: dict, key_cols: tuple) -> str:
    return "_".join(str(doc.get(col)) for col in key_cols)


class _ConditionParser:
    """Parses SQL WHERE/ON clauses into MongoDB filter documents.

    Supports: =, !=, <>, >, <, >=, <=, IS NULL, IS NOT NULL, LIKE, NOT LIKE,
    AND / OR with parentheses, placeholders (?) and inline literals.
    """

    def __init__(self, args: list):
        self.args = args
        self.pos = 0

    def parse(self, clause: str) -> dict:
        clause = (clause or "").strip()
        if not clause:
            return {}
        if clause.upper() in ("1=1", "1 = 1", "TRUE"):
            return {}

        or_parts = self._split_top_level(clause, " OR ")
        if len(or_parts) > 1:
            return {"$or": [self.parse(p) for p in or_parts]}

        and_parts = self._split_top_level(clause, " AND ")
        if len(and_parts) > 1:
            filters = [self.parse(p) for p in and_parts]
            merged: dict = {}
            conflicts = any(
                set(a) & set(b) for a in filters for b in filters if a is not b
            )
            if not conflicts:
                for f in filters:
                    merged.update(f)
                return merged
            return {"$and": filters}

        return self._parse_simple(clause)

    @staticmethod
    def _split_top_level(clause: str, sep: str) -> list:
        parts, depth, start, i = [], 0, 0, 0
        sep_upper = sep.upper()
        while i < len(clause):
            ch = clause[i]
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth = max(0, depth - 1)
            elif (
                depth == 0
                and clause[i : i + len(sep)].upper() == sep_upper
            ):
                parts.append(clause[start:i])
                start = i + len(sep)
                i += len(sep)
                continue
            i += 1
        parts.append(clause[start:])
        return parts

    def _next_arg(self):
        if self.pos >= len(self.args):
            raise ValueError(
                "Query references more placeholders than supplied arguments"
            )
        value = self.args[self.pos]
        self.pos += 1
        return value

    @staticmethod
    def _strip_quotes(name: str) -> str:
        """Strip backticks or double-quotes from a column/identifier name."""
        if name.startswith("`") and name.endswith("`"):
            return name[1:-1]
        if name.startswith('"') and name.endswith('"'):
            return name[1:-1]
        return name

    def _parse_simple(self, cond: str) -> dict:
        cond = cond.strip()
        if cond.startswith("(") and cond.endswith(")"):
            return self.parse(cond[1:-1])

        m = re.match(r"(\w+)\s*(=|!=|<>|>=|<=|>|<)\s*\?\s*$", cond)
        if m:
            column, op = m.groups()
            return self._op_filter(self._strip_quotes(column), op, self._next_arg())

        m = re.match(
            r"(\w+)\s*(=|!=|<>|>=|<=|>|<)\s*"
            r"('(?:[^']|'')*'|\"(?:[^\"]|\"\")*\"|-?\d+(?:\.\d+)?)\s*$",
            cond,
        )
        if m:
            column, op, literal = m.groups()
            return self._op_filter(self._strip_quotes(column), op, self._coerce_literal(literal))

        m = re.match(r"(\w+)\s+IS\s+NOT\s+NULL\s*$", cond, re.IGNORECASE)
        if m:
            return {self._strip_quotes(m.group(1)): {"$ne": None}}

        m = re.match(r"(\w+)\s+IS\s+NULL\s*$", cond, re.IGNORECASE)
        if m:
            return {self._strip_quotes(m.group(1)): None}

        m = re.match(
            r"(\w+)\s+NOT\s+LIKE\s+('(?:[^']|'')*')\s*$", cond, re.IGNORECASE
        )
        if m:
            pattern = self._like_to_regex(m.group(2)[1:-1])
            return {self._strip_quotes(m.group(1)): {"$not": re.compile(pattern, re.IGNORECASE)}}

        m = re.match(r"(\w+)\s+LIKE\s+('(?:[^']|'')*')\s*$", cond, re.IGNORECASE)
        if m:
            pattern = self._like_to_regex(m.group(2)[1:-1])
            return {self._strip_quotes(m.group(1)): {"$regex": pattern, "$options": "i"}}

        raise ValueError(f"Cannot parse WHERE condition: {cond}")

    def _op_filter(self, column: str, op: str, value):
        if op == "=":
            return {column: value}
        if op in ("!=", "<>"):
            return {column: {"$ne": value}}
        if op == ">":
            return {column: {"$gt": value}}
        if op == "<":
            return {column: {"$lt": value}}
        if op == ">=":
            return {column: {"$gte": value}}
        if op == "<=":
            return {column: {"$lte": value}}
        raise ValueError(f"Unsupported operator {op}")

    @staticmethod
    def _like_to_regex(pattern: str) -> str:
        out = []
        for ch in pattern:
            if ch == "%":
                out.append(".*")
            elif ch == "_":
                out.append(".")
            else:
                out.append(re.escape(ch))
        return "^" + "".join(out) + "$"

    @staticmethod
    def _coerce_literal(literal: str):
        if literal.startswith("'") or literal.startswith('"'):
            return literal[1:-1].replace("''", "'").replace('""', '"')
        if re.fullmatch(r"-?\d+", literal):
            return int(literal)
        try:
            return float(literal)
        except (TypeError, ValueError):
            return literal


class MongoPool:
    """Translates the bot's SQL statements into native MongoDB operations.

    Not a general SQL engine — it implements the precise statement shapes the
    Niko codebase issues, so ``bot.cxn`` callers never need to know whether
    they are talking to SQLite or MongoDB.
    """

    def __init__(self, client, db_name: str):
        self._client = client
        self._db = client[db_name]
        self.db_type = "mongodb"

    # ────────────────────────────────────────────────────────────── API ──
    async def execute(self, query: str, *args):
        query = query.strip()
        head = query.split(None, 1)[0].upper() if query else ""
        upper_head = query[:40].upper()
        if head == "CREATE" and "TABLE" in upper_head:
            return  # schema-less: collections are created implicitly
        if head in ("ALTER", "DROP", "PRAGMA", "BEGIN", "COMMIT"):
            return
        q = _convert_query(re.sub(r"\s+", " ", query)).strip()
        upper = q.upper()
        if upper.startswith("INSERT") or upper.startswith("REPLACE INTO"):
            if "SELECT" in upper and "VALUES" not in upper:
                return await self._handle_insert_select(q, list(args))
            if "ON CONFLICT" in upper:
                return await self._handle_upsert(q, list(args))
            if "OR IGNORE" in upper:
                return await self._handle_insert(q, list(args), mode="ignore")
            return await self._handle_insert(q, list(args), mode="replace")
        if upper.startswith("UPDATE"):
            return await self._handle_update(q, list(args))
        if upper.startswith("DELETE"):
            return await self._handle_delete(q, list(args))
        raise NotImplementedError(
            f"MongoDB does not support this SQL query: {query[:60]}"
        )

    async def fetch(self, query: str, *args):
        q = _convert_query(re.sub(r"\s+", " ", query)).strip()
        if not q.upper().startswith("SELECT"):
            raise NotImplementedError(
                f"MongoDB does not support this SQL query: {q[:60]}"
            )
        return await self._handle_select(q, list(args))

    async def fetchrow(self, query: str, *args):
        rows = await self.fetch(query, *args)
        return rows[0] if rows else None

    async def fetchone(self, query: str, *args):
        return await self.fetchrow(query, *args)

    async def fetchval(self, query: str, *args):
        row = await self.fetchrow(query, *args)
        if row is None:
            return None
        return next(iter(row.values()), None)

    # ─────────────────────────────────────────────── public helpers ──
    def collection(self, name: str):
        """Direct motor collection access for code that wants native Mongo."""
        return self._db[name]

    @property
    def client(self):
        return self._client

    @property
    def db(self):
        return self._db

    # ───────────────────────────────────────────── primary-key mapping ──
    def _resolve_id(self, table: str, doc: dict):
        pk = PRIMARY_KEYS.get(table)
        if pk is None:
            if "guild_id" in doc and "user_id" in doc:
                return _composite_id(doc, ("guild_id", "user_id"))
            if "user_id" in doc:
                return doc["user_id"]
            if "id" in doc:
                return doc["id"]
            if "guild_id" in doc:
                return doc["guild_id"]
            return None
        if isinstance(pk, tuple):
            if any(doc.get(col) is None for col in pk):
                return None
            return _composite_id(doc, pk)
        return doc.get(pk)

    def _apply_pk_filter(self, table: str, filter_dict: dict) -> dict:
        """Collapse primary-key equality filters onto _id for indexed lookups."""
        pk = PRIMARY_KEYS.get(table)
        if isinstance(pk, tuple):
            if all(col in filter_dict for col in pk):
                composite = "_".join(str(filter_dict[col]) for col in pk)
                rest = {k: v for k, v in filter_dict.items() if k not in pk}
                return {"_id": composite, **rest}
            return filter_dict
        if pk and pk in filter_dict:
            rest = {k: v for k, v in filter_dict.items() if k != pk}
            return {"_id": filter_dict[pk], **rest}
        return filter_dict

    def _restore_pk_fields(self, table: str, doc: dict, _id) -> dict:
        """Ensure primary-key fields exist on documents read back from Mongo."""
        pk = PRIMARY_KEYS.get(table)
        if isinstance(pk, tuple):
            parts = str(_id).split("_") if _id is not None else []
            if len(parts) == len(pk):
                for col, part in zip(pk, parts):
                    if doc.get(col) is None:
                        doc[col] = _typed(part)
            return doc
        if pk and doc.get(pk) is None and _id is not None:
            doc[pk] = _typed(_id)
        return doc

    # ─────────────────────────────────────────── JSON column handling ──
    def _encode_doc(self, table: str, doc: dict) -> dict:
        table_cols = JSON_COLUMNS.get(table, ())
        out = {}
        for k, v in doc.items():
            if k == "_id":
                out[k] = v
            elif k in table_cols and isinstance(v, (list, dict)):
                out[k] = json.dumps(v)
            elif k not in table_cols and isinstance(v, (list, dict)):
                out[k] = json.dumps(v)
            else:
                out[k] = v
        return out

    def _decode_rows(self, table: str, docs: list) -> list:
        table_cols = JSON_COLUMNS.get(table, ())
        rows = []
        for doc in docs:
            doc = dict(doc)
            _id = doc.pop("_id", None)
            doc = self._restore_pk_fields(table, doc, _id)
            for col in table_cols:
                if col in doc and isinstance(doc[col], str):
                    try:
                        doc[col] = json.loads(doc[col])
                    except Exception:
                        pass
            rows.append(Row(doc))
        return rows

    # ─────────────────────────────────────────────────────── SELECT ──
    async def _handle_select(self, q: str, args: list) -> list:
        m = re.match(
            r"SELECT\s+(.+?)\s+FROM\s+([A-Za-z_]\w*)\s*(.*)$",
            q,
            re.IGNORECASE | re.DOTALL,
        )
        if not m:
            raise ValueError(f"Cannot parse SELECT query: {q}")
        columns_raw, table, tail = m.groups()
        tail = (tail or "").strip()

        where_clause = None
        order_by = []
        limit = None
        if tail:
            wm = re.search(
                r"\bWHERE\b\s+(.*?)(?=\bORDER\s+BY\b|\bLIMIT\b|$)",
                tail,
                re.IGNORECASE | re.DOTALL,
            )
            if wm:
                where_clause = wm.group(1).strip()
            om = re.search(
                r"\bORDER\s+BY\b\s+(.+?)(?=\bLIMIT\b|$)",
                tail,
                re.IGNORECASE | re.DOTALL,
            )
            if om:
                for part in om.group(1).split(","):
                    bits = part.strip().split()
                    if not bits:
                        continue
                    direction = (
                        bits[1].upper()
                        if len(bits) > 1 and bits[1].upper() in ("ASC", "DESC")
                        else "ASC"
                    )
                    order_by.append((bits[0], 1 if direction == "ASC" else -1))
            lm = re.search(r"\bLIMIT\s+(\d+)", tail, re.IGNORECASE)
            if lm:
                limit = int(lm.group(1))

        upper_cols = columns_raw.upper()
        if "COUNT(" in upper_cols or "SUM(" in upper_cols:
            return await self._handle_aggregate_select(
                table, columns_raw, where_clause, args
            )

        parser = _ConditionParser(args)
        filter_dict = parser.parse(where_clause)
        filter_dict = self._apply_pk_filter(table, filter_dict)

        projection = None
        columns = columns_raw.strip()
        if columns.upper() == "1":
            projection = {"_id": 1}
        elif columns != "*":
            projection = {c.strip(): 1 for c in columns.split(",")}
            projection["_id"] = 1

        cursor = self._db[table].find(filter_dict, projection)
        if order_by:
            cursor = cursor.sort(order_by)
        if limit is not None:
            cursor = cursor.limit(limit)
        docs = await cursor.to_list(length=None)
        rows = self._decode_rows(table, docs)

        if projection is not None and columns.upper() != "1":
            wanted = [c.strip() for c in columns.split(",")]
            for row in rows:
                for key in list(row.keys()):
                    if key not in wanted and key != "_id":
                        row.pop(key, None)
        return rows

    async def _handle_aggregate_select(
        self, table: str, columns_raw: str, where_clause, args: list
    ) -> list:
        parser = _ConditionParser(args)
        filter_dict = parser.parse(where_clause)
        filter_dict = self._apply_pk_filter(table, filter_dict)

        m = re.search(r"COUNT\s*\(\s*(\*|\w+)\s*\)", columns_raw, re.IGNORECASE)
        if not m:
            raise NotImplementedError(
                f"Unsupported aggregate SELECT: {columns_raw}"
            )
        target = m.group(1)
        if target == "*":
            count = await self._db[table].count_documents(filter_dict)
            return [Row({"COUNT(*)": count, "count": count})]
        count = await self._db[table].count_documents(
            {**filter_dict, target: {"$ne": None}}
        )
        return [Row({target: count})]

    # ─────────────────────────────────────────────────────── INSERT ──
    _INSERT_RE = re.compile(
        r"(?:INSERT\s+(?:OR\s+\w+\s+)?|REPLACE\s+)INTO\s+([A-Za-z_]\w*)\s*"
        r"\((.*?)\)\s*VALUES\s*\((.*)\)\s*$",
        re.IGNORECASE | re.DOTALL,
    )

    def _parse_insert(self, q: str):
        m = self._INSERT_RE.match(q)
        if not m:
            raise ValueError(f"Cannot parse INSERT query: {q}")
        table, cols_raw, values_raw = m.groups()
        columns = [c.strip() for c in cols_raw.split(",")]
        return table, columns, values_raw

    def _split_values(self, values_raw: str) -> list:
        """Split a VALUES(...) body on top-level commas."""
        parts, depth, start = [], 0, 0
        in_string = False
        quote = ""
        for i, ch in enumerate(values_raw):
            if in_string:
                if ch == quote:
                    if i + 1 < len(values_raw) and values_raw[i + 1] == quote:
                        continue
                    in_string = False
                continue
            if ch in ("'", '"'):
                in_string = True
                quote = ch
            elif ch == "(":
                depth += 1
            elif ch == ")":
                depth = max(0, depth - 1)
            elif ch == "," and depth == 0:
                parts.append(values_raw[start:i].strip())
                start = i + 1
        parts.append(values_raw[start:].strip())
        return parts

    def _bind_values(self, values: list, args: list, start_index: int):
        """Bind a VALUES list against positional args. Returns (doc, next_idx)."""
        doc = {}
        idx = start_index
        for raw in values:
            if raw == "?":
                if idx >= len(args):
                    raise ValueError("Missing argument for INSERT statement")
                doc[f"__arg{len(doc)}"] = args[idx]
                idx += 1
            else:
                doc[f"__arg{len(doc)}"] = self._eval_value_expr(raw, None, [])
        return doc, idx

    async def _handle_insert(self, q: str, args: list, mode: str):
        table, columns, values_raw = self._parse_insert(q)
        values = self._split_values(values_raw)

        doc = {}
        arg_idx = 0
        for i, col in enumerate(columns):
            raw = values[i] if i < len(values) else "?"
            if raw == "?":
                if arg_idx >= len(args):
                    raise ValueError(f"Missing argument for INSERT INTO {table}")
                doc[col] = args[arg_idx]
                arg_idx += 1
            else:
                doc[col] = self._eval_value_expr(raw, None, [])

        if table == "triggers" and doc.get("id") is None:
            # AUTOINCREMENT emulation: allocate the next free integer id.
            highest = await self._db.triggers.find_one(
                {"id": {"$type": ["int", "long"]}}, sort=[("id", -1)]
            )
            doc["id"] = (highest.get("id") or 0) + 1 if highest else 1

        _id = self._resolve_id(table, doc)
        if _id is None:
            raise ValueError(
                f"INSERT INTO {table}: primary key value missing ({columns})"
            )
        doc["_id"] = _id
        doc = self._encode_doc(table, doc)

        collection = self._db[table]
        if mode == "ignore":
            existing = await collection.find_one({"_id": _id}, {"_id": 1})
            if existing:
                return
            await collection.insert_one(doc)
            return
        await collection.replace_one({"_id": _id}, doc, upsert=True)

    async def _handle_upsert(self, q: str, args: list):
        """INSERT ... ON CONFLICT (col) DO UPDATE SET expr = ..."""
        m = re.match(
            r"INSERT\s+INTO\s+([A-Za-z_]\w*)\s*\((.*?)\)\s*VALUES\s*\((.*?)\)\s*"
            r"ON\s+CONFLICT\s*\((\w+)\)\s*DO\s+UPDATE\s+SET\s+(.*)$",
            q,
            re.IGNORECASE | re.DOTALL,
        )
        if not m:
            return await self._handle_insert(q, args, mode="replace")
        table, cols_raw, values_raw, _conflict_col, set_clause = m.groups()
        columns = [c.strip() for c in cols_raw.split(",")]
        values = self._split_values(values_raw)

        doc = {}
        arg_idx = 0
        for i, col in enumerate(columns):
            raw = values[i] if i < len(values) else "?"
            if raw == "?":
                if arg_idx >= len(args):
                    raise ValueError(f"Missing argument for INSERT INTO {table}")
                doc[col] = args[arg_idx]
                arg_idx += 1
            else:
                doc[col] = self._eval_value_expr(raw, None, [])

        _id = self._resolve_id(table, doc)
        remaining_args = args[arg_idx:]
        update = self._build_update_ops(table, set_clause, remaining_args)

        collection = self._db[table]
        base = self._encode_doc(table, doc)
        if _id is not None:
            filter_dict = {"_id": _id}
        else:
            # No resolvable id: upsert by the insert values' natural key columns.
            filter_dict = {k: v for k, v in base.items() if k != "_id"}
        insert_values = {k: v for k, v in base.items() if k != "_id"}

        # 1) Upsert the raw INSERT ... VALUES row ($setOnInsert only applies
        #    when the document does not exist yet, matching SQL semantics).
        result = await collection.update_one(
            filter_dict, {"$setOnInsert": insert_values}, upsert=True
        )

        # 2) On conflict (row already existed), apply DO UPDATE SET ops.
        if result.upserted_id is None:
            ops = []
            if update.get("$set"):
                ops.append({"$set": update["$set"]})
            if update.get("$inc"):
                ops.append({"$inc": update["$inc"]})
            if update.get("$unset"):
                ops.append({"$unset": update["$unset"]})
            if ops:
                await collection.update_one(filter_dict, ops)

    async def _handle_insert_select(self, q: str, args: list):
        m = re.match(
            r"(?:INSERT\s+(?:OR\s+IGNORE\s+)?|REPLACE\s+)INTO\s+([A-Za-z_]\w*)\s*"
            r"\((.*?)\)\s*(SELECT\s+.*)$",
            q,
            re.IGNORECASE | re.DOTALL,
        )
        if not m:
            raise ValueError(f"Cannot parse INSERT...SELECT: {q}")
        table, cols_raw, select_sql = m.groups()
        target_columns = [c.strip() for c in cols_raw.split(",")]

        sel_m = re.search(
            r"SELECT\s+(.+?)\s+FROM", select_sql, re.IGNORECASE | re.DOTALL
        )
        if not sel_m:
            raise ValueError(f"Cannot parse INSERT...SELECT: {q}")
        select_cols = [c.strip() for c in sel_m.group(1).split(",")]

        rows = await self._handle_select(select_sql, args)
        collection = self._db[table]
        inserted = 0
        for row in rows:
            doc = {
                target: row.get(select_col)
                for target, select_col in zip(target_columns, select_cols)
            }
            _id = self._resolve_id(table, doc)
            if _id is None:
                continue
            if await collection.find_one({"_id": _id}, {"_id": 1}):
                continue
            await collection.insert_one(
                self._encode_doc(table, {**doc, "_id": _id})
            )
            inserted += 1
        return inserted

    # ─────────────────────────────────────────────────────── UPDATE ──
    _UPDATE_RE = re.compile(
        r"UPDATE\s+([A-Za-z_]\w*)\s+SET\s+(.+?)(?:\s+WHERE\s+(.*))?$",
        re.IGNORECASE | re.DOTALL,
    )

    async def _handle_update(self, q: str, args: list):
        m = self._UPDATE_RE.match(q)
        if not m:
            raise ValueError(f"Cannot parse UPDATE query: {q}")
        table, set_clause, where_clause = m.groups()
        if where_clause:
            where_clause = where_clause.strip()

        # Process SET clause first to count how many args it consumes,
        # then feed the remaining args to the WHERE parser.
        # _build_update_ops uses its own arg_idx counter to track consumption.
        set_update = self._build_update_ops(table, set_clause, args)
        set_arg_count = set_update.pop("_arg_count", 0)
        where_args = args[set_arg_count:]

        parser = _ConditionParser(where_args)
        filter_dict = parser.parse(where_clause)
        filter_dict = self._apply_pk_filter(table, filter_dict)

        ops = []
        if set_update.get("$set"):
            ops.append({"$set": set_update["$set"]})
        if set_update.get("$inc"):
            ops.append({"$inc": set_update["$inc"]})
        if set_update.get("$unset"):
            ops.append({"$unset": set_update["$unset"]})
        if not ops:
            return
        await self._db[table].update_many(filter_dict, ops)

    def _build_update_ops(self, table: str, set_clause: str, args: list) -> dict:
        update: dict = {}
        arg_idx = 0

        def set_col(col, value):
            update.setdefault("$set", {})[col] = value

        for assignment in _ConditionParser._split_top_level(set_clause, ","):
            assignment = assignment.strip()
            if not assignment:
                continue
            m = re.match(r"(\w+)\s*=\s*(.+)$", assignment, re.DOTALL)
            if not m:
                continue
            column = _ConditionParser._strip_quotes(m.group(1))
            expr = m.group(2).strip()

            # col = ?                       → set arg
            if expr == "?":
                if arg_idx >= len(args):
                    raise ValueError(f"Missing argument for SET clause: {set_clause}")
                set_col(column, args[arg_idx])
                arg_idx += 1
                continue

            up = expr.upper().replace(" ", "")

            # col = col + ? / col - ?       → $inc (also handles col = col + 5)
            m2 = re.match(rf"{re.escape(column)}\s*([+\-])\s*(\?|-?\d+(?:\.\d+)?)$", expr)
            if m2 and not expr.lower().startswith("datetime"):
                sign, operand = m2.groups()
                if operand == "?":
                    if arg_idx >= len(args):
                        raise ValueError(f"Missing argument for SET clause: {set_clause}")
                    value = args[arg_idx]
                    arg_idx += 1
                else:
                    value = _typed(operand) if re.fullmatch(r"-?\d+", operand) else float(operand)
                delta = value if sign == "+" else -value
                if isinstance(delta, float) and delta.is_integer():
                    delta = int(delta)
                update.setdefault("$inc", {})[column] = delta
                continue

            # col = DATETIME('now')
            if up in ("DATETIME('NOW')",):
                set_col(
                    column,
                    datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
                )
                continue

            # COALESCE(existing_col, fallback)
            m2 = re.match(
                r"COALESCE\s*\(\s*(\w+)\s*,\s*(.+?)\s*\)$", expr, re.IGNORECASE
            )
            if m2:
                set_col(column, self._eval_value_expr(m2.group(2), None, []))
                continue

            # total = total + ?  handled above; anything else is a literal expr
            set_col(column, self._eval_value_expr(expr, None, args))
        update["_arg_count"] = arg_idx
        return update

    def _eval_value_expr(self, expr: str, doc, args) -> object:
        expr = expr.strip()
        up = expr.upper().replace(" ", "")
        if up in ("NULL",):
            return None
        if up in ("TRUE",):
            return True
        if up in ("FALSE",):
            return False
        if up in ("DATETIME('NOW')",):
            return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        if expr.startswith("'") and expr.endswith("'") and len(expr) >= 2:
            return expr[1:-1].replace("''", "'")
        if expr.startswith('"') and expr.endswith('"') and len(expr) >= 2:
            return expr[1:-1].replace('""', '"')
        if re.fullmatch(r"-?\d+", expr):
            return int(expr)
        try:
            return float(expr)
        except (TypeError, ValueError):
            return expr

    # ─────────────────────────────────────────────────────── DELETE ──
    _DELETE_RE = re.compile(
        r"DELETE\s+FROM\s+([A-Za-z_]\w*)\s*(?:WHERE\s+(.*))?$",
        re.IGNORECASE | re.DOTALL,
    )

    async def _handle_delete(self, q: str, args: list):
        m = self._DELETE_RE.match(q)
        if not m:
            raise ValueError(f"Cannot parse DELETE query: {q}")
        table, where_clause = m.groups()
        parser = _ConditionParser(args)
        filter_dict = parser.parse((where_clause or "").strip() or None)
        filter_dict = self._apply_pk_filter(table, filter_dict)
        await self._db[table].delete_many(filter_dict)


async def create_pool(db_path: str) -> Union[SQLitePool, MongoPool]:
    """Create the shared database pool.

    Prefers MongoDB whenever MONGODB_URL is configured and reachable; falls
    back to SQLite (data/database.db) otherwise — identical behaviour either
    way because every call site speaks the pool API, not the raw driver.
    """
    global _shared_pool
    mongo_url = os.getenv("MONGODB_URL")
    if mongo_url:
        try:
            from motor.motor_asyncio import AsyncIOMotorClient

            db_name = os.getenv("MONGODB_DATABASE", "discord_bot")
            client = AsyncIOMotorClient(
                mongo_url,
                serverSelectionTimeoutMS=4000,
                connectTimeoutMS=4000,
            )
            await client.admin.command("ping")
            pool = MongoPool(client, db_name)
            _shared_pool = pool
            return pool
        except Exception as e:
            print(f"Failed to connect to MongoDB: {e}. Falling back to SQLite.")

    db = await aiosqlite.connect(db_path)
    await db.execute("PRAGMA journal_mode=WAL")
    await db.execute("PRAGMA foreign_keys=ON")
    pool = SQLitePool(db)
    _shared_pool = pool
    return pool
